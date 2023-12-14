import os
from django.db import transaction

import fitz

from parsers.models.ocr import OCR
from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus
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

                queue = Queue.objects.get(
                    document_id=document.id
                )
                if queue.queue_status == QueueStatus.STOPPED.value:
                    queue.queue_class = QueueClass.PROCESSED.value
                    queue.queue_status = QueueStatus.READY.value
                    queue.save()
                    break

                page_num = page_idx + 1
                document_page = DocumentPage.objects.get(
                    document_id=document.id, page_num=page_num)
                if document_page.ocred == True:
                    continue

                xml = convert_pdf_to_xml(
                    path=source_file_path,
                    pagenos=[page_idx]
                )

                document_page.xml = xml
                document_page.ocred = True
                document_page.save()

            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        print(e)
