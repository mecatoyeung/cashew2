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
from .convert_pdf_to_xml import convert_pdf_to_xml

from django.db import transaction


def generate_images_from_pdf(document):
    try:
        folder_path = os.path.join(
            MEDIA_URL, 'documents/%s/' % (document.guid))
        abs_pdf_path = os.path.join(
            folder_path, 'source_file.' + document.extension)

        dpi = 150  # choose desired dpi here
        zoom = dpi / 72  # zoom factor, standard: 72 dpi
        magnify = fitz.Matrix(zoom, zoom)  # magnifies in x, resp. y direction
        with fitz.open(abs_pdf_path) as doc:  # open document
            for page_idx, page in enumerate(doc):
                page_no = page_idx + 1
                # render page to an image
                pix = page.get_pixmap(matrix=magnify)
                abs_png_path = os.path.join(
                    folder_path, "source_file-" + str(page_no) + ".png")
                pix.save(abs_png_path)

                image = PIL.Image.open(abs_png_path)
                width, height = image.size

                # Create document page object in database
                dp = DocumentPage(
                    document=document,
                    page_num=page_no,
                    image_file=abs_png_path,
                    width=width,
                    height=height
                )
                dp.save()

            # Update total page num
            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        raise e
