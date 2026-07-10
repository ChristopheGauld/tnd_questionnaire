from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from openpyxl import Workbook

from .models import Answer, Page, Question, Questionnaire, Response


@staff_member_required
def dashboard(request):
    questionnaires = Questionnaire.objects.prefetch_related('pages', 'responses')
    return render(request, 'questionnaires/dashboard.html', {'questionnaires': questionnaires})


def questionnaire_start(request, public_id):
    questionnaire = get_object_or_404(Questionnaire, public_id=public_id, is_active=True)
    first_page = questionnaire.pages.first()
    if not first_page:
        raise Http404('Questionnaire sans page.')

    response = Response.objects.create(questionnaire=questionnaire)
    return redirect(
        f'{reverse("questionnaire_page", kwargs={"public_id": public_id, "page_number": first_page.order})}'
        f'?r={response.token}'
    )


def questionnaire_page(request, public_id, page_number):
    questionnaire = get_object_or_404(Questionnaire, public_id=public_id, is_active=True)
    response = get_object_or_404(Response, questionnaire=questionnaire, token=request.GET.get('r'))
    pages = list(questionnaire.pages.prefetch_related('questions__options'))
    current_index = next((i for i, item in enumerate(pages) if item.order == page_number), None)
    if current_index is None:
        raise Http404('Page introuvable.')

    page = pages[current_index]
    questions = list(page.questions.prefetch_related('options'))
    existing = {
        answer.question_id: answer.value.get('value', '')
        for answer in response.answers.filter(question__page=page)
    }
    errors = {}

    if request.method == 'POST':
        answers = {}
        for question in questions:
            if question.question_type == Question.DISPLAY:
                continue
            field_name = f'q_{question.id}'
            if question.question_type == Question.MULTIPLE:
                value = request.POST.getlist(field_name)
            else:
                value = request.POST.get(field_name, '').strip()

            if question.required and not value:
                errors[question.id] = 'Réponse obligatoire.'
            answers[question] = value

        if not errors:
            with transaction.atomic():
                for question, value in answers.items():
                    Answer.objects.update_or_create(
                        response=response,
                        question=question,
                        defaults={'value': {'value': value}},
                    )
                participant = request.POST.get('participant_code', '').strip()
                if participant:
                    response.participant_code = participant
                    response.save(update_fields=['participant_code', 'updated_at'])

            if current_index + 1 < len(pages):
                next_page = pages[current_index + 1]
                return redirect(
                    f'{reverse("questionnaire_page", kwargs={"public_id": public_id, "page_number": next_page.order})}'
                    f'?r={response.token}'
                )

            response.completed_at = timezone.now()
            response.save(update_fields=['completed_at', 'updated_at'])
            return redirect('thank_you')

    previous_page = pages[current_index - 1] if current_index > 0 else None
    next_label = 'Terminer' if current_index + 1 == len(pages) else 'Continuer'

    return render(
        request,
        'questionnaires/page.html',
        {
            'questionnaire': questionnaire,
            'response': response,
            'page': page,
            'pages': pages,
            'questions': questions,
            'existing': existing,
            'errors': errors,
            'page_position': current_index + 1,
            'page_count': len(pages),
            'previous_page': previous_page,
            'next_label': next_label,
        },
    )


def thank_you(request):
    return render(request, 'questionnaires/thank_you.html')


@staff_member_required
def export_xlsx(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questions = list(
        Question.objects.filter(page__questionnaire=questionnaire)
        .exclude(question_type=Question.DISPLAY)
        .select_related('page')
        .order_by('page__order', 'order')
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Réponses'

    headers = ['response_id', 'participant_code', 'started_at', 'completed_at']
    headers += [f'{q.page.order}.{q.order} {q.prompt[:80]}' for q in questions]
    ws.append(headers)

    responses = questionnaire.responses.prefetch_related('answers__question').order_by('started_at')
    for response in responses:
        answer_map = {answer.question_id: answer.as_export_value() for answer in response.answers.all()}
        row = [
            str(response.token),
            response.participant_code,
            response.started_at.isoformat(),
            response.completed_at.isoformat() if response.completed_at else '',
        ]
        row += [answer_map.get(question.id, '') for question in questions]
        ws.append(row)

    for column_cells in ws.columns:
        header = str(column_cells[0].value or '')
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(len(header) + 2, 14), 48)

    out = BytesIO()
    wb.save(out)
    out.seek(0)
    filename = f'{questionnaire.slug}-reponses.xlsx'
    response = HttpResponse(
        out.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
