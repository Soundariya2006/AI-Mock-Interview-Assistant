import pymupdf
from docx import Document


def extract_pdf_text(file_path):

    text = ""

    document = pymupdf.open(file_path)

    for page in document:
        text += page.get_text() + "\n"

    document.close()

    return text.strip()


def extract_docx_text(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text.strip()


def extract_resume_text(file_path):

    if file_path.lower().endswith(".pdf"):
        return extract_pdf_text(file_path)

    elif file_path.lower().endswith(".docx"):
        return extract_docx_text(file_path)

    return ""