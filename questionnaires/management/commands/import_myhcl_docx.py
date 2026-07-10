import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from questionnaires.models import Option, Page, Question, Questionnaire


DEFAULT_SOURCE = '/Users/christophe/Desktop/Assos et Orga/FIND TND/myHCL TND/myHCL_TND.docx'


SECTION_OPTIONS = {
    'questionnaire relatif aux anomalies perceptives': [
        'Non',
        "Oui, sans degré de détresse",
        "Oui, avec un degré léger de détresse",
        "Oui, avec un degré modéré de détresse",
        "Oui, avec un degré sévère de détresse",
    ],
    'questionnaire sur les prodromes': [
        'Non',
        "Oui, sans degré de détresse",
        "Oui, avec un degré léger de détresse",
        "Oui, avec un degré modéré de détresse",
        "Oui, avec un degré sévère de détresse",
    ],
    'dépistage des troubles alimentaires': [
        '0 - Jamais',
        "1 - Moins d'une fois par mois",
        '2 - Une fois par mois',
        '3 - 2 à 3 fois par mois',
        '4 - Une fois par semaine',
        '5 - 2 à 3 fois par semaine',
        '6 - 4 à 6 fois par semaine',
        '7 - Tous les jours',
    ],
    'dépistage des troubles du sommeil': ['Jamais', 'Rarement', 'Parfois', 'Souvent', 'Toujours'],
    "échelle d'epworth": [
        '0 - Aucun risque',
        '1 - Faible risque',
        '2 - Risque modéré',
        '3 - Risque élevé',
    ],
    "index de sévérité de l'insomnie": ['0', '1', '2', '3', '4'],
    'questionnaire de typologie circadienne': ['1', '2', '3', '4', '5'],
    "échelle d'anxiété et de dépression": ['0', '1', '2', '3'],
    'échelle de gravité du risque suicidaire': ['Oui', 'Non'],
    'échelle d’anxiété liée au changement climatique': [
        'Jamais',
        'Rarement',
        'Parfois',
        'Souvent',
        'Presque toujours',
    ],
    'camouflage des traits autistiques': [
        'Fortement en désaccord',
        'En désaccord',
        'Plutôt en désaccord',
        'Ni en accord ni en désaccord',
        'Plutôt en accord',
        'En accord',
        'Fortement en accord',
    ],
    'échelle de réciprocité sociale': [
        'Pas vrai',
        'Parfois vrai',
        'Souvent vrai',
        'Presque toujours vrai',
        "Ne s'applique pas",
    ],
    'questionnaire sur la communication sociale': ['Oui', 'Non'],
    'questionnaire abrégé de conners': ['Pas du tout', 'Un petit peu', 'Beaucoup', 'Énormément'],
    "évaluation des troubles de déficit de l'attention": ['Jamais', 'Parfois', 'Souvent', 'Très souvent'],
    'échelle de tdah': ['Pas du tout', 'Un peu', 'Souvent', 'Très souvent'],
}


SKIP_HEADINGS = {
    'Neurodéveloppement',
    "Service de psychopathologie de l’enfant et de l’adolescent (HFME)",
}


class Command(BaseCommand):
    help = 'Importe le questionnaire myHCL TND depuis le fichier Word source.'

    def add_arguments(self, parser):
        parser.add_argument('--source', default=DEFAULT_SOURCE)
        parser.add_argument('--reset', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(options['source'])
        if not source.exists():
            raise CommandError(f'Fichier introuvable: {source}')

        if options['reset']:
            Questionnaire.objects.filter(slug='myhcl-tnd-neurodeveloppement').delete()

        questionnaire, _ = Questionnaire.objects.update_or_create(
            slug='myhcl-tnd-neurodeveloppement',
            defaults={
                'title': 'myHCL TND - Neurodéveloppement',
                'introduction': (
                    "Questionnaire issu du document Word myHCL_TND.docx. "
                    "Les réponses sont enregistrées en base et exportables en Excel."
                ),
                'is_active': True,
            },
        )
        questionnaire.pages.all().delete()

        sections = parse_sections(source)
        total_questions = 0
        for page_order, section in enumerate(sections, start=1):
            page = Page.objects.create(
                questionnaire=questionnaire,
                title=section['title'],
                instructions='',
                order=page_order,
            )
            total_questions += populate_page(page, section['items'])

        self.stdout.write(
            self.style.SUCCESS(
                f'{questionnaire.title}: {len(sections)} pages, {total_questions} questions importées.'
            )
        )


def parse_sections(source):
    doc = Document(source)
    sections = []
    current = None

    for block in iter_blocks(doc):
        if isinstance(block, Paragraph):
            raw = normalize(block.text)
            if not raw:
                continue
            style_name = block.style.name.lower()
            if style_name.startswith('toc'):
                continue
            if style_name == 'heading 1':
                if raw in SKIP_HEADINGS:
                    continue
                current = {'title': raw, 'items': []}
                sections.append(current)
                continue
            if raw == 'Remarques préliminaires' and current is None:
                current = {'title': raw, 'items': []}
                sections.append(current)
                continue
            if current is not None:
                current['items'].append({'kind': 'paragraph', 'text': raw, 'style': block.style.name})
        elif isinstance(block, Table) and current is not None:
            rows = table_rows(block)
            if rows:
                current['items'].append({'kind': 'table', 'rows': rows})

    return sections


def iter_blocks(document):
    body = document.element.body
    for child in body.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, document)
        elif child.tag.endswith('}tbl'):
            yield Table(child, document)


def table_rows(table):
    rows = []
    for row in table.rows:
        values = []
        for cell in row.cells:
            text = normalize(cell.text)
            if not values or values[-1] != text:
                values.append(text)
        while values and not values[-1]:
            values.pop()
        if any(values):
            rows.append(values)
    return rows


def populate_page(page, items):
    instructions = []
    q_order = 1
    last_question = None
    default_options = options_for_title(page.title)
    default_options_from_title = bool(default_options)

    for item in items:
        if item['kind'] == 'table':
            q_order = import_table(page, item['rows'], q_order, default_options)
            last_question = None
            continue

        text = item['text']
        if q_order == 1 and not default_options and item.get('style') == 'List Paragraph':
            instructions.append(text)
            continue

        option_labels = option_labels_from_text(text, item.get('style', ''))

        if option_labels:
            if last_question and not last_question.options.exists():
                add_options(last_question, option_labels)
                labels = [option.label for option in last_question.options.all()]
                last_question.question_type = infer_type(last_question.prompt, labels)
                last_question.save(update_fields=['question_type'])
            elif last_question and last_question.options.exists():
                add_options(last_question, option_labels)
                labels = [option.label for option in last_question.options.all()]
                last_question.question_type = infer_type(last_question.prompt, labels)
                last_question.save(update_fields=['question_type'])
            elif default_options_from_title:
                continue
            else:
                default_options = merge_options(default_options, option_labels)
            continue

        if is_question_text(text):
            question = create_question(page, text, q_order, default_options)
            q_order += 1
            last_question = question
            continue

        if q_order == 1:
            instructions.append(text)
        else:
            Question.objects.create(
                page=page,
                prompt=text,
                question_type=Question.DISPLAY,
                required=False,
                order=q_order,
            )
            q_order += 1
            last_question = None

    if instructions:
        page.instructions = '\n\n'.join(instructions)
        page.save(update_fields=['instructions'])

    return q_order - 1


def import_table(page, rows, q_order, default_options):
    for row in rows:
        cells = [cell for cell in row if cell]
        if not cells:
            continue
        prompt = cells[0]
        if not is_question_text(prompt):
            if len(prompt) > 35:
                Question.objects.create(
                    page=page,
                    prompt=prompt,
                    question_type=Question.DISPLAY,
                    order=q_order,
                )
                q_order += 1
            continue

        row_options = [cell for cell in cells[1:] if len(cell) < 120]
        options = row_options or default_options
        question = create_question(page, prompt, q_order, options)
        q_order += 1
    return q_order


def create_question(page, prompt, order, options):
    cleaned = normalize(prompt.replace('\t', ' '))
    cleaned = cleaned.replace('•••••', '').replace('•••', '').strip()
    required = '*' in cleaned
    cleaned = cleaned.replace('*', '').strip()

    qtype = infer_type(cleaned, options)
    question = Question.objects.create(
        page=page,
        prompt=cleaned,
        question_type=qtype,
        required=required,
        order=order,
    )
    if options and qtype in {Question.SINGLE, Question.MULTIPLE, Question.SCALE}:
        add_options(question, options)
    return question


def add_options(question, labels):
    seen = set()
    for option in question.options.all():
        seen.add(option.label.lower())
    order = question.options.count() + 1
    for label in labels:
        clean = re.sub(r'^[Oo]\s+', '', normalize(label)).strip(' :')
        if not clean or clean.lower() in seen:
            continue
        seen.add(clean.lower())
        Option.objects.create(question=question, label=clean, value=clean, order=order)
        order += 1


def infer_type(prompt, options):
    lower = prompt.lower()
    if options:
        if any(word in lower for word in ['genre', 'qui ', 'êtes-vous', 'etes-vous', 'situation', 'type de']):
            return Question.SINGLE
        return Question.SCALE if len(options) > 2 else Question.SINGLE
    if 'date de naissance' in lower or lower.startswith('date '):
        return Question.DATE
    if 'e-mail' in lower or 'email' in lower:
        return Question.EMAIL
    if 'téléphone' in lower or 'telephone' in lower:
        return Question.PHONE
    if any(word in lower for word in ['taille', 'poids', 'âge', 'age', "nombre d'heures", 'combien d']):
        return Question.NUMBER
    if any(word in lower for word in ['préciser', 'précision', 'raison', 'lequel', 'lesquels', 'autre']):
        return Question.TEXTAREA
    if len(prompt) > 180:
        return Question.TEXTAREA
    return Question.TEXT


def is_question_text(text):
    if len(text) < 2:
        return False
    lower = text.lower().strip()
    if lower in {'oui', 'non'}:
        return False
    if re.match(r'^\d+\s*[.)]?\s+\S+', text):
        return True
    if '?' in text:
        return True
    if text.endswith('*') or text.endswith(':'):
        return True
    if len(text) < 95 and not text.endswith('.'):
        return True
    return False


def option_labels_from_text(text, style_name):
    raw = text.strip()
    lower = raw.lower()
    if is_numbered_question(raw):
        return []
    if lower in {'oui', 'non'} or lower.startswith('o ') or lower.startswith('si oui'):
        return [raw]

    if style_name == 'List Paragraph' and not is_numbered_question(raw):
        return [raw]

    if '\t' in raw:
        return [part for part in raw.split('\t') if part.strip()]

    known = {
        'masculin', 'féminin', 'non binaire', 'transgenre', 'fluide', 'agenre',
        'jamais', 'rarement', 'parfois', 'souvent', 'presque toujours',
        'pas du tout', 'un peu', 'très souvent',
        'pas vrai', 'parfois vrai', 'souvent vrai', 'presque toujours vrai',
        "ne s'applique pas",
    }
    if lower in known:
        return [raw]
    return []


def merge_options(existing, new_labels):
    merged = list(existing)
    seen = {label.lower() for label in merged}
    for label in new_labels:
        clean = re.sub(r'^[Oo]\s+', '', normalize(label)).strip(' :')
        if clean and clean.lower() not in seen:
            merged.append(clean)
            seen.add(clean.lower())
    return merged


def is_numbered_question(text):
    return bool(re.match(r'^\d+\w?\s*[.)]?(?:\s|\t)+\S+', text))


def options_for_title(title):
    lower = title.lower()
    for key, labels in SECTION_OPTIONS.items():
        if key in lower:
            return labels
    return []


def normalize(text):
    return re.sub(r'[ \u00a0]+', ' ', text.replace('\r', '\n')).strip()
