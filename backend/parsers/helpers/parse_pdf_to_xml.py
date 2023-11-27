import os
from django.db import transaction

import fitz

from parsers.models.ocr import OCR
from parsers.models.document_page import DocumentPage
from parsers.helpers.convert_pdf_to_xml import convert_pdf_to_xml

from django.db import transaction

from backend.settings import MEDIA_URL


@transaction.atomic
def parse_pdf_to_xml(document):
    try:
        media_folder_path = MEDIA_URL
        documents_folder_path = os.path.join(
            media_folder_path, "documents", document.guid)

        source_file_path = os.path.join(
            documents_folder_path, "source_file.pdf")

        with fitz.open(source_file_path) as doc:
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1

                xml = convert_pdf_to_xml(
                    path=source_file_path,
                    pagenos=[page_idx]
                )

                document_page = DocumentPage.objects.get(
                    document_id=document.id, page_num=page_num)
                document_page.xml = xml
                document_page.ocred = True
                document_page.save()

            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        raise e