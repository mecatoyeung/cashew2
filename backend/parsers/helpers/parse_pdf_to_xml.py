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
from ..models.ocr import OCR
from ..models.ocr_type import OCRType
from ..models.document_page import DocumentPage
from ..models.queue import Queue
from ..models.queue_class import QueueClass

from backend.settings import MEDIA_URL
from .convert_pdf_to_xml import convert_pdf_to_xml

from django.db import transaction


@transaction.atomic
def parse_pdf_to_xml(document):
    try:
        ocr = OCR.objects.get(parser_id=document.parser_id)
        media_folder_path = MEDIA_URL
        documents_folder_path = os.path.join(
            media_folder_path, "documents", document.guid)

        if ocr.ocr_type != OCRType.NO_OCR.value:
            source_file_folder_path = os.path.join(
                documents_folder_path, "ocred.pdf")
        else:
            source_file_folder_path = os.path.join(
                documents_folder_path, "source_file.pdf")

        with fitz.open(source_file_folder_path) as doc:  # open document
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                # generate xml
                xml = convert_pdf_to_xml(
                    path=source_file_folder_path,
                    pagenos=[page_idx]
                )
                # fix bug in library
                xml = xml + "</pages>"

                # Output .xml file
                # xml_filename =os.path.join( working_path, str(page_num) + ".xml")

                # with (open(xml_filename, 'w', encoding="utf-8")) as outfile:
                #    outfile.write(xml)
                #    outfile.close()

                document_page = DocumentPage.objects.get(
                    document_id=document.id, page_num=page_num)
                document_page.xml = xml
                document_page.save()

            # Update total page num
            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        raise e
