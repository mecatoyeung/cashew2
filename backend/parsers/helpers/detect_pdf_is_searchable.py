import fitz

def detect_pdf_is_searchable(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()

    if len(text) > 0:
        return True
    else:
        return False