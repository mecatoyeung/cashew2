import os
import json

import fitz

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as ETElement
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

from parsers.models.ocr import OCR
from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus
from parsers.helpers.convert_pdf_to_xml import convert_pdf_to_xml
from parsers.helpers.path_helpers import xml_path

from django.db import transaction

from backend.settings import MEDIA_ROOT

def convert_json_to_xml(json_dict):

    xml = ET.fromstring('<pages></pages>')

    page_width = json_dict['width']
    page_height = json_dict['height']
    page = SubElement(xml, "page", attrib={
        "bbox": "0.000,0.000," + "{:.3f}".format(page_width) + "," + "{:.3f}".format(page_height)})
    
    for block in json_dict["blocks"]:

        for line in block["lines"]:

            for span in line["spans"]:

                ocr_line_x1 = int(span['bbox'][0])
                ocr_line_y1 = page_height - int(span['bbox'][3])
                ocr_line_x2 = int(span['bbox'][2])
                ocr_line_y2 = page_height - int(span['bbox'][1])

                textline = SubElement(
                    page,
                    "textline",
                    attrib={
                        "bbox": "{:.3f}".format(ocr_line_x1) + "," + "{:.3f}".format(ocr_line_y1) + "," + "{:.3f}".format(ocr_line_x2) + "," + "{:.3f}".format(ocr_line_y2),
                    },
                )

                ocrx_word = span['text']

                word_in_line_count = 0
                for char in span['text']:

                    char_x1 = (ocr_line_x2 - ocr_line_x1) / \
                        len(ocrx_word) * word_in_line_count + ocr_line_x1
                    char_x2 = (ocr_line_x2 - ocr_line_x1) / \
                        len(ocrx_word) * \
                        (word_in_line_count + 1) + ocr_line_x1
                    char_y1 = ocr_line_y1
                    char_y2 = ocr_line_y2

                    char_x1 = int(char_x1)
                    char_y1 = int(char_y1)
                    char_x2 = int(char_x2)
                    char_y2 = int(char_y2)
                    
                    text = SubElement(
                            textline,
                            "text",
                            attrib={
                                "font": "AAAAAA+invisible",
                                "bbox": "{:.3f}".format(char_x1) + "," + "{:.3f}".format(char_y1) + "," + "{:.3f}".format(char_x2) + "," + "{:.3f}".format(char_y2),
                                "conf": str(100.00)
                            },
                        )
                    text.text = char

                    word_in_line_count += 1
        
    return tostring(xml, xml_declaration=True, encoding="utf-8").decode("utf-8")


def parse_pdf_to_xml(document):
    try:
        media_folder_path = MEDIA_ROOT
        documents_folder_path = os.path.join(
            media_folder_path, "documents", document.guid)

        source_file_path = os.path.join(
            documents_folder_path, "source_file.pdf")
        
        page_idx = 0
        doc = fitz.open(source_file_path)
        for page in doc:

            page_num = page_idx + 1

            abs_xml_path = xml_path(document, page_num)

            queue = Queue.objects.get(
                document_id=document.id
            )
            if queue.queue_status == QueueStatus.STOPPED.value:
                queue.queue_class = QueueClass.PROCESSED.value
                queue.queue_status = QueueStatus.COMPLETED.value
                queue.save()
                break

            document_page = DocumentPage.objects.get(
                document_id=document.id, page_num=page_num)
            if document_page.ocred == True:
                continue

            text_page = page.get_textpage()
            json_dict = json.loads(text_page.extractJSON())
            xml = convert_json_to_xml(json_dict)
            with open(abs_xml_path, 'w', encoding="utf-8") as xml_file:
                xml_file.write(xml)
            document_page.xml = xml

            document_page.ocred = True
            document_page.save()

            page_idx += 1

        document.save()
        
    except Exception as e:
        raise e
