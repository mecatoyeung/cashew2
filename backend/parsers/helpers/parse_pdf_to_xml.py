import os

import uuid

from datetime import datetime

from pathlib import Path

from django.conf import settings
from django.db import transaction

from pdf2image import convert_from_path

import fitz

import PIL

from ..models.parser import Parser
from ..models.document import Document
from ..models.document_page import DocumentPage
from ..models.queue import Queue
from ..models.queue_class import QueueClass

from backend.settings import MEDIA_URL
from .convert_pdf import convert_pdf

from django.db import transaction

@transaction.atomic
def parse_pdf_to_xml(document):
    try:
        folder_path = os.path.join(MEDIA_URL, 'documents/%s/' % (document.guid))
        abs_pdf_path = os.path.join(folder_path, 'original.' + document.extension)

        with fitz.open(abs_pdf_path) as doc:  # open document
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                # generate xml
                xml = convert_pdf(
                    path=abs_pdf_path,
                    pagenos=[page_idx]
                )
                # fix bug in library
                xml = xml + "</pages>"

                # Create document page object in database
                dp = DocumentPage.objects.get(document_id=document.id, page_num=page_num)
                dp.xml = xml
                dp.save()

            # Update total page num
            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        raise e
