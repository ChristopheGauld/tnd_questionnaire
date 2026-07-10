from __future__ import annotations

import csv
import html
import json
import os
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "questionnaire_data.json"
LOCAL_RESPONSES = APP_DIR / "responses" / "responses.csv"


st.set_page_config(
    page_title="myHCL TND",
    page_icon="TND",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_questionnaire() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #172033;
            --muted: #64748b;
            --line: #d8e0ea;
            --paper: #f7f9fc;
            --field: #ffffff;
            --panel: #ffffff;
            --accent: #0f766e;
            --accent-soft: #e7f5f2;
            --warning-soft: #fff7ed;
        }
        .stApp {
            background: var(--paper);
            color: var(--ink);
        }
        .block-container {
            max-width: 1040px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        h1, h2, h3, p, label, .stMarkdown {
            letter-spacing: 0 !important;
        }
        h1 {
            font-size: clamp(2rem, 3.8vw, 3.25rem) !important;
            line-height: 1.04 !important;
            font-weight: 760 !important;
            margin: .45rem 0 .65rem !important;
        }
        h2 {
            font-weight: 740 !important;
        }
        div[data-testid="stSidebar"] {
            background: #0f172a;
            color: #f8fafc;
        }
        div[data-testid="stSidebar"] * {
            color: #f8fafc;
        }
        .meta-grid {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: center;
            margin: 0 0 1rem 0;
            border-bottom: 1px solid var(--line);
            padding: .2rem 0 1rem;
        }
        .meta-kicker {
            color: #0f766e;
            font-weight: 760;
            font-size: .78rem;
            text-transform: uppercase;
        }
        .meta-title {
            color: var(--ink);
            font-weight: 720;
            font-size: 1.05rem;
            flex: 1;
        }
        .meta-page {
            color: var(--muted);
            text-align: right;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }
        .intro {
            background: var(--accent-soft);
            border: 1px solid #bde4dd;
            border-radius: 8px;
            padding: 1rem 1.1rem;
            color: #164e46;
            white-space: pre-line;
            margin: 1rem 0 1.5rem;
        }
        .question-block {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem 1.1rem .8rem;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(15, 23, 42, .045);
        }
        .question-index {
            color: var(--accent);
            font-weight: 760;
            font-size: .78rem;
            margin-bottom: .4rem;
            font-variant-numeric: tabular-nums;
        }
        .display-text {
            background: var(--warning-soft);
            border: 1px solid #fed7aa;
            border-radius: 8px;
            padding: .85rem 1rem;
            color: #7c2d12;
            white-space: pre-line;
        }
        div[data-testid="stRadio"] label,
        div[data-testid="stCheckbox"] label {
            align-items: flex-start;
        }
        div[data-testid="stRadio"] > label,
        div[data-testid="stCheckbox"] > label,
        div[data-testid="stTextInput"] > label,
        div[data-testid="stTextArea"] > label {
            color: var(--ink);
            font-weight: 700;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stDateInput"] input {
            background: var(--field);
            border-radius: 6px;
            border-color: #b8c0cc;
        }
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 6px;
            border: 1px solid var(--accent);
            background: var(--accent);
            color: white;
            font-weight: 760;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: #115e59;
            background: #115e59;
            color: white;
        }
        .secondary-note {
            color: var(--muted);
            font-size: .92rem;
        }
        @media (max-width: 760px) {
            .meta-grid { align-items: flex-start; flex-direction: column; }
            .meta-page { text-align: left; }
            .block-container { padding-left: 1rem; padding-right: 1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_secret(name: str, default: str = "") -> str:
    if os.environ.get(name):
        return os.environ[name]
    if not secrets_file_exists():
        return default
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def secrets_file_exists() -> bool:
    candidates = [
        Path.home() / ".streamlit" / "secrets.toml",
        APP_DIR / ".streamlit" / "secrets.toml",
    ]
    return any(path.exists() for path in candidates)


def google_client():
    if not secrets_file_exists():
        return None
    gspread = import_gspread()
    if gspread is None:
        return None
    try:
        account_info = dict(st.secrets["google_service_account"])
    except Exception:
        return None
    try:
        return gspread.service_account_from_dict(account_info)
    except Exception as exc:
        st.error(f"Configuration Google Sheets invalide : {exc}")
        return None


def google_worksheet():
    sheet_id = get_secret("GOOGLE_SHEET_ID")
    gspread = import_gspread()
    client = google_client()
    if not sheet_id or client is None or gspread is None:
        return None
    try:
        spreadsheet = client.open_by_key(sheet_id)
        try:
            return spreadsheet.worksheet("responses")
        except gspread.WorksheetNotFound:
            return spreadsheet.add_worksheet(title="responses", rows=1000, cols=700)
    except Exception as exc:
        st.error(f"Connexion Google Sheets impossible : {exc}")
        return None


def import_gspread():
    try:
        import gspread
    except Exception:
        return None
    return gspread


def all_questions(data: dict) -> list[dict]:
    questions = []
    for page in data["pages"]:
        for question in page["questions"]:
            if question["question_type"] != "display":
                questions.append({**question, "page_title": page["title"]})
    return questions


def export_headers(data: dict) -> list[str]:
    headers = [
        "response_id",
        "submitted_at",
        "participant_code",
        "completed",
    ]
    for question in all_questions(data):
        label = question["prompt"].replace("\n", " ").strip()
        headers.append(f"Q{question['id']} - {label[:110]}")
    return headers


def flatten_response(data: dict, response_id: str, participant_code: str, answers: dict) -> dict:
    row = {
        "response_id": response_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "participant_code": participant_code,
        "completed": "yes",
    }
    for question in all_questions(data):
        key = f"q_{question['id']}"
        value = answers.get(key, "")
        if isinstance(value, list):
            value = "; ".join(value)
        row[f"Q{question['id']} - {question['prompt'].replace(chr(10), ' ').strip()[:110]}"] = value
    return row


def save_local(row: dict, headers: list[str]) -> None:
    LOCAL_RESPONSES.parent.mkdir(parents=True, exist_ok=True)
    exists = LOCAL_RESPONSES.exists()
    with LOCAL_RESPONSES.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not exists:
            writer.writeheader()
        writer.writerow({header: row.get(header, "") for header in headers})


def save_google(row: dict, headers: list[str]) -> bool:
    worksheet = google_worksheet()
    if worksheet is None:
        return False
    existing_headers = worksheet.row_values(1)
    if existing_headers != headers:
        worksheet.clear()
        worksheet.append_row(headers)
    worksheet.append_row([row.get(header, "") for header in headers], value_input_option="USER_ENTERED")
    return True


def load_responses(data: dict) -> list[dict]:
    headers = export_headers(data)
    worksheet = google_worksheet()
    if worksheet is not None:
        return normalize_rows(worksheet.get_all_records(), headers)
    if LOCAL_RESPONSES.exists():
        with LOCAL_RESPONSES.open("r", newline="", encoding="utf-8") as file:
            return normalize_rows(list(csv.DictReader(file)), headers)
    return []


def normalize_rows(rows: list[dict], headers: list[str]) -> list[dict]:
    return [{header: row.get(header, "") for header in headers} for row in rows]


def rows_to_xlsx(headers: list[str], rows: list[dict]) -> bytes:
    buffer = BytesIO()
    sheet_rows = [headers] + [[row.get(header, "") for header in headers] for row in rows]
    sheet_xml = build_sheet_xml(sheet_rows)
    timestamp = datetime.now(timezone.utc).isoformat()

    with ZipFile(buffer, "w", ZIP_DEFLATED) as xlsx:
        xlsx.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""",
        )
        xlsx.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
        )
        xlsx.writestr(
            "docProps/app.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>myHCL TND Streamlit</Application>
</Properties>""",
        )
        xlsx.writestr(
            "docProps/core.xml",
            f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Réponses myHCL TND</dc:title>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
</cp:coreProperties>""",
        )
        xlsx.writestr(
            "xl/workbook.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Réponses" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>""",
        )
        xlsx.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""",
        )
        xlsx.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buffer.getvalue()


def build_sheet_xml(rows: list[list[object]]) -> str:
    xml_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            ref = f"{column_name(col_index)}{row_index}"
            text = html.escape("" if value is None else str(value), quote=False)
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>')
        xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>'
        f'{"".join(xml_rows)}'
        '</sheetData>'
        '</worksheet>'
    )


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def init_state() -> None:
    if "response_id" not in st.session_state:
        st.session_state.response_id = str(uuid.uuid4())
    if "page_index" not in st.session_state:
        st.session_state.page_index = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False


def key_for(question: dict) -> str:
    return f"q_{question['id']}"


def render_question(question: dict, index: int) -> None:
    qtype = question["question_type"]
    key = key_for(question)
    default = st.session_state.answers.get(key)
    required = " *" if question.get("required") else ""

    st.markdown('<div class="question-block">', unsafe_allow_html=True)
    if qtype == "display":
        st.markdown(f'<div class="display-text">{question["prompt"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown(f'<div class="question-index">{index:02d}</div>', unsafe_allow_html=True)
    label = f"{question['prompt']}{required}"
    if question.get("help_text"):
        st.caption(question["help_text"])

    options = [option["value"] for option in question.get("options", [])]
    option_labels = {option["value"]: option["label"] for option in question.get("options", [])}

    if qtype in {"single", "scale"} and options:
        current_index = options.index(default) if default in options else None
        value = st.radio(
            label,
            options=options,
            index=current_index,
            format_func=lambda value: option_labels.get(value, value),
            key=key,
            horizontal=len(options) <= 5 and max(len(option) for option in options) < 28,
        )
    elif qtype == "multiple" and options:
        value = []
        st.markdown(f"**{label}**")
        previous = set(default or [])
        for option in question["options"]:
            opt_key = f"{key}_{option['id']}"
            checked = st.checkbox(option["label"], value=option["value"] in previous, key=opt_key)
            if checked:
                value.append(option["value"])
        st.session_state[key] = value
    elif qtype == "textarea":
        value = st.text_area(label, value=default or "", key=key)
    elif qtype == "number":
        value = st.text_input(label, value="" if default is None else str(default), key=key)
    elif qtype == "date":
        value = st.text_input(label, value=default or "", placeholder="JJ/MM/AAAA", key=key)
    elif qtype == "email":
        value = st.text_input(label, value=default or "", key=key)
    elif qtype == "phone":
        value = st.text_input(label, value=default or "", key=key)
    else:
        value = st.text_input(label, value=default or "", key=key)

    if qtype != "multiple":
        st.session_state.answers[key] = value
    st.markdown("</div>", unsafe_allow_html=True)


def collect_page_answers(page: dict) -> list[str]:
    errors = []
    for question in page["questions"]:
        if question["question_type"] == "display":
            continue
        key = key_for(question)
        if key in st.session_state:
            st.session_state.answers[key] = st.session_state[key]
        value = st.session_state.answers.get(key)
        if question.get("required") and not value:
            errors.append(question["prompt"])
    return errors


def public_app(data: dict) -> None:
    init_state()
    pages = data["pages"]
    page_index = st.session_state.page_index
    page = pages[page_index]
    progress = (page_index + 1) / len(pages)

    st.markdown(
        f"""
        <div class="meta-grid">
          <div class="meta-kicker">myHCL TND</div>
          <div class="meta-title">{data["questionnaire"]["title"]}</div>
          <div class="meta-page">{page_index + 1:02d}/{len(pages):02d}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(progress)
    st.title(page["title"])
    if page.get("instructions"):
        st.markdown(f'<div class="intro">{page["instructions"]}</div>', unsafe_allow_html=True)

    if page_index == 0:
        participant = st.text_input(
            "Identifiant participant",
            value=st.session_state.answers.get("participant_code", ""),
            key="participant_code_widget",
        )
        st.session_state.answers["participant_code"] = participant

    for idx, question in enumerate(page["questions"], start=1):
        render_question(question, idx)

    left, mid, right = st.columns([2, 6, 2])
    with left:
        if page_index > 0 and st.button("Retour", use_container_width=True):
            collect_page_answers(page)
            st.session_state.page_index -= 1
            st.rerun()
    with right:
        is_last = page_index == len(pages) - 1
        if st.button("Terminer" if is_last else "Continuer", use_container_width=True):
            errors = collect_page_answers(page)
            if errors:
                st.error("Merci de répondre aux questions obligatoires avant de continuer.")
            elif is_last:
                headers = export_headers(data)
                row = flatten_response(
                    data,
                    st.session_state.response_id,
                    st.session_state.answers.get("participant_code", ""),
                    st.session_state.answers,
                )
                saved_google = save_google(row, headers)
                if not saved_google:
                    save_local(row, headers)
                st.session_state.submitted = True
                st.rerun()
            else:
                st.session_state.page_index += 1
                st.rerun()


def admin_app(data: dict) -> None:
    st.title("Administration")
    st.markdown('<p class="secondary-note">Accès privé aux réponses et à l’export.</p>', unsafe_allow_html=True)

    admin_password = get_secret("ADMIN_PASSWORD", "")
    if not admin_password:
        st.warning("Définir ADMIN_PASSWORD dans les secrets Streamlit pour activer l'administration.")
        return
    entered = st.text_input("Mot de passe admin", type="password")
    if entered != admin_password:
        st.info("Saisir le mot de passe admin pour afficher les réponses.")
        return

    headers = export_headers(data)
    rows = load_responses(data)
    st.metric("Réponses", len(rows))
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.download_button(
        "Télécharger Excel",
        data=rows_to_xlsx(headers, rows),
        file_name="myhcl_tnd_reponses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    with st.expander("État du stockage"):
        if google_worksheet() is not None:
            st.success("Google Sheets est configuré.")
        else:
            st.warning("Google Sheets n'est pas configuré. Les réponses sont enregistrées localement pour les tests.")


def main() -> None:
    inject_css()
    data = load_questionnaire()

    mode = st.query_params.get("mode", "questionnaire")
    if isinstance(mode, list):
        mode = mode[0] if mode else "questionnaire"

    with st.sidebar:
        st.markdown("## myHCL TND")
        st.caption("Questionnaire en ligne")
        if st.button("Questionnaire"):
            st.query_params["mode"] = "questionnaire"
            st.rerun()
        if st.button("Admin"):
            st.query_params["mode"] = "admin"
            st.rerun()

    if st.session_state.get("submitted"):
        st.title("Merci")
        st.markdown('<div class="intro">Les réponses ont bien été enregistrées.</div>', unsafe_allow_html=True)
        if st.button("Commencer une nouvelle réponse"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        return

    if mode == "admin":
        admin_app(data)
    else:
        public_app(data)


if __name__ == "__main__":
    main()
