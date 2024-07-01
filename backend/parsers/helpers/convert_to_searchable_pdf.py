import os
import io
import traceback

import re

import base64
import shutil
import json
from statistics import mean
import uuid
from datetime import datetime
from io import BytesIO

from PyPDF2 import PdfWriter, PdfReader

import requests

from reportlab.pdfgen.canvas import Canvas

from PIL import Image
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import cv2

import fitz

from parsers.models.parser_type import ParserType
from parsers.models.rule import Rule
from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus
from parsers.models.pre_processing import PreProcessing
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from parsers.models.splitting import Splitting
from parsers.models.splitting_operator_type import SplittingOperatorType
from parsers.models.last_page_splitting_rule_type import LastPageSplittingRuleType
from parsers.models.consecutive_page_splitting_rule_type import ConsecutivePageSplittingRuleType
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.document_extension import DocumentExtension

from parsers.helpers.document_parser import DocumentParser
from parsers.helpers.stream_processor import StreamProcessor

from parsers.helpers.detect_pdf_is_searchable import detect_pdf_is_searchable
from parsers.helpers.parse_pdf_to_xml import parse_pdf_to_xml, convert_json_to_xml
from parsers.helpers.path_helpers import source_file_pdf_path, ocr_folder_path, ocred_pdf_path, original_image_path, \
    pre_processed_image_path, ocred_image_path, gcv_path, hocr_path, xml_path, document_path, \
    pre_processed_image_path

import parsers.schedule_jobs.process_ocr_queue as process_ocr_queue

import zlib

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element as ETElement
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

import lxml.html

from .gcv2hocr import fromResponse


doctr_model = None
paddle_model = None


def load_invisible_font():

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font = """
    eJzdlk1sG0UUx/+zs3btNEmrUKpCPxikSqRS4jpfFURUagmkEQQoiRXgAl07Y3vL2mvt2ml8APXG
    hQPiUEGEVDhWVHyIC1REPSAhBOWA+BCgSoULUqsKcWhVBKjhzfPU+VCi3Flrdn7vzZv33ryZ3TUE
    gC6chsTx8fHck1ONd98D0jnS7jn26GPjyMIleZhk9fT0wcHFl1/9GRDPkTxTqHg1dMkzJH9CbbTk
    xbWlJfKEdB+Np0pBswi+nH/Nvay92VtfJp4nvEztUJkUHXsdksUOkveXK/X5FNuLD838ICx4dv4N
    I1e8+ZqbxwCNP2jyqXoV/fmhy+WW/2SqFsb1pX68SfEpZ/TCrI3aHzcP//jitodvYmvL+6Xcr5mV
    vb1ScCzRnPRPfz+LsRSWNasuwRrZlh1sx0E8AriddyzEDfE6EkglFhJDJO5u9fJbFJ0etEMB78D5
    4Djm/7kjT0wqhSNURyS+u/2MGJKRu+0ExNkrt1pJti9p2x6b3TBJgmUXuzgnDmI8UWMbkVxeinCw
    Mo311/l/v3rF7+01D+OkZYE0PrbsYAu+sSyxU0jLLtIiYzmBrFiwnCT9FcsdOOK8ZHbFleSn0znP
    nDCnxbnAnGT9JeYtrP+FOcV8nTlNnsoc3bBAD85adtCNRcsSffjBsoseca/lBE7Q09LiJOm/ttyB
    0+IqcwfncJt5q4krO5k7jV7uY+5m7mPebuLKUea7iHvk48w72OYF5rvZT8C8k/WvMN/Dc19j3s02
    bzPvZZv3me9j/ox5P9t/xdzPzPVJcc7yGnPL/1+GO1lPVTXM+VNWOTRRg0YRHgrUK5yj1kvaEA1E
    xAWiCtl4qJL2ADKkG6Q3XxYjzEcR0E9hCj5KtBd1xCxp6jV5mKP7LJBr1nTRK2h1TvU2w0akCmGl
    5lWbBzJqMJsdyaijQaCm/FK5HqspHetoTtMsn4LO0T2mlqcwmlTVOT/28wGhCVKiNANKLiJRlxqB
    F603axQznIzRhDSq6EWZ4UUs+xud0VHsh1U1kMlmNwu9kTuFaRqpURU0VS3PVmZ0iE7gct0MG/8+
    2fmUvKlfRLYmisd1w8pk1LSu1XUlryM1MNTH9epTftWv+16gIh1oL9abJZyjrfF5a4qccp3oFAcz
    Wxxx4DpvlaKKxuytRDzeth5rW4W8qBFesvEX8RFRmLBHoB+TpCmRVCCb1gFCruzHqhhW6+qUF6tC
    pL26nlWN2K+W1LhRjxlVGKmRTFYVo7CiJug09E+GJb+QocMCPMWBK1wvEOfRFF2U0klK8CppqqvG
    pylRc2Zn+XDQWZIL8iO5KC9S+1RekOex1uOyZGR/w/Hf1lhzqVfFsxE39B/ws7Rm3N3nDrhPuMfc
    w3R/aE28KsfY2J+RPNp+j+KaOoCey4h+Dd48b9O5G0v2K7j0AM6s+5WQ/E0wVoK+pA6/3bup7bJf
    CMGjwvxTsr74/f/F95m3TH9x8o0/TU//N+7/D/ScVcA=
    """.encode('latin1')
    uncompressed = bytearray(zlib.decompress(base64.b64decode(font)))
    ttf = io.BytesIO(uncompressed)
    setattr(ttf, "name", "(invisible.ttf)")
    pdfmetrics.registerFont(TTFont('invisible', ttf))


load_invisible_font()


def element_coordinates(element):
    """
    Returns a tuple containing the coordinates of the bounding box around
    an element
    """
    boxPattern = re.compile('bbox((\s+\d+){4})')
    out = (0, 0, 0, 0)
    if 'title' in element.attrib:
        matches = boxPattern.search(element.attrib['title'])
    if matches:
        coords = matches.group(1).split()
        out = (int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3]))
    return out


def get_streamed_by_rule(rule_id, parsed_result):
    for r in parsed_result:
        if r["rule"]["id"] == rule_id:
            return r["streamed"]["value"]
    raise Exception("Cannot find streamed by rule from parsed result.")


def convert_page(parser, document, ocr, document_page):

    if document_page.ocred:
        return

    page_num = document_page.page_num

    ocr_engine = ocr.ocr_type

    preprocessings = PreProcessing.objects.filter(parser_id=parser.id)

    abs_ocr_folder_path = ocr_folder_path(document)
    if not os.path.exists(abs_ocr_folder_path):
        os.makedirs(abs_ocr_folder_path)

    if (preprocessings.count() > 0):
        last_preprocessing = preprocessings.order_by('-step')[0]
        abs_ocred_image_path = ocred_image_path(
            document, document_page.page_num)
        abs_pre_processed_image_path = pre_processed_image_path(
            document, last_preprocessing, document_page.page_num)
        shutil.copy(abs_pre_processed_image_path,
                    abs_ocred_image_path)
    else:
        abs_ocred_image_path = ocred_image_path(
            document, document_page.page_num)
        abs_original_image_path = original_image_path(
            document, document_page.page_num)
        shutil.copy(abs_original_image_path,
                    abs_ocred_image_path)

    if ocr_engine == "DOCTR":
        import torch
        global doctr_model
        if doctr_model == None:

            from doctr.models import ocr_predictor

            print("Loading DOCTR OCR Engine")
            device = torch.device("cpu")
            doctr_model = ocr_predictor(
                det_arch='db_mobilenet_v3_large', reco_arch='crnn_vgg16_bn', pretrained=True).to(device)
            print("Loaded DOCTR OCR Engine")
    elif ocr_engine == "PADDLE":
        global paddle_model
        lang = ocr.paddle_ocr_language
        if paddle_model == None:
            from paddleocr import PaddleOCR
            print("Loading Paddle OCR Engine")
            paddle_model = PaddleOCR(use_angle_cls=True, lang=lang)
            print("Loaded Paddle OCR Engine")

    # Check if Pre-Processing has been stopped
    queue = Queue.objects.get(
        document_id=document.id
    )
    if queue.queue_status == QueueStatus.STOPPED.value:
        queue.queue_class = QueueClass.PROCESSED.value
        queue.queue_status = QueueStatus.COMPLETED.value
        queue.save()

    abs_ocred_image_path = ocred_image_path(document, page_num)
    abs_hocr_path = hocr_path(document, page_num)
    abs_xml_path = xml_path(document, page_num)

    if ocr_engine == "NO_OCR":

        abs_source_file_pdf_path = source_file_pdf_path(document)

        doc = fitz.open(abs_source_file_pdf_path)
        page = doc[page_num-1]

        document_page = DocumentPage.objects.get(
            document_id=document.id, page_num=page_num)
        
        text_page = page.get_textpage()
        json_dict = json.loads(text_page.extractJSON())
        xml = convert_json_to_xml(json_dict)
        with open(abs_xml_path, 'w', encoding="utf-8") as xml_file:
            xml_file.write(xml)
        document_page.xml = xml

    elif ocr_engine == "DOCTR":
        from doctr.io import DocumentFile
        doc = DocumentFile.from_images(abs_ocred_image_path)
        result = doctr_model(doc)
        hocr_output = result.export_as_xml()[0][1]
        with open(abs_hocr_path, 'wb') as outfile:
            hocr_output.write(outfile)
            outfile.close()

        xml = convert_hocr_to_xml(abs_hocr_path, abs_xml_path)
        document_page.xml = xml

    elif ocr_engine == "PADDLE":
        result = paddle_model.ocr(abs_ocred_image_path, cls=True)
        im = cv2.imread(abs_ocred_image_path)
        hocr_output = export_as_hocr(im, result)
        with open(abs_hocr_path, 'wb') as f:
            f.write(hocr_output)
            f.close()

        xml = convert_hocr_to_xml(abs_hocr_path, abs_xml_path)
        document_page.xml = xml

    elif ocr_engine == "GOOGLE_VISION":
        google_vision_api_key = ocr.google_vision_ocr_api_key
        if google_vision_api_key == None:
            raise Exception("Please fill in Google Vision OCR API Key.")
        url = "https://vision.googleapis.com/v1/images:annotate?key=" + google_vision_api_key

        gcv_filename = gcv_path(document, page_num)

        with open(abs_ocred_image_path, 'rb') as image_file:
            png_in_base64 = base64.b64encode(
                image_file.read()).decode('ascii')
            response = requests.post(url, json={
                "requests": [
                    {
                        "image": {
                            "content": png_in_base64
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION"
                            }
                        ],
                        "imageContext": {
                            "textDetectionParams": {
                                "enableTextDetectionConfidenceScore": True
                            },
                            "languageHints": ["zh-Hant", "en"]
                        }
                    }
                ]
            })
            response_in_json = response.json()
            with open(gcv_filename, 'w') as f:
                json.dump(response_in_json, f)

            # Convert .gcv to .hocr
            im = cv2.imread(abs_ocred_image_path)
            height, width, c = im.shape
            hocr_page = fromResponse(
                response_in_json, abs_hocr_path, width, height)
            with (open(abs_hocr_path, 'w', encoding="utf-8")) as outfile:
                outfile.write(hocr_page.render().encode(
                    'utf-8') if str == bytes else hocr_page.render())
                outfile.close()

        xml = convert_hocr_to_xml(abs_hocr_path, abs_xml_path)
        document_page.xml = xml

    elif ocr_engine == "OMNIPAGE":
        from omnipage import kRecInit, kRecQuit, kRecSetLicense, kRecLoadImgF, \
            kRecRecognize, kRecSetLanguages, kRecSetDefaultRecognitionModule, \
            kRecSetCodePage, kRecFreeImg, kRecSetDefaults, kRecSetDTXTFormat, kRecGetLetters
        from .omnipage_utils import LICENSE_FILE, OEM_CODE, SID, PAGE_NUMBER_0, \
            InfoMsg, ErrMsg, USE_OEM_LICENSE, YOUR_COMPANY, YOUR_PRODUCT, \
            API_INIT_WARN, API_LICENSEVALIDATION_WARN, DTXT_HOCR, DTXT_IOTPDF, CreateEnabledLanguagesArray, \
            LANG_CHS, LANG_CHT, LANG_ENG, RM_AUTO, II_CURRENT, LoopMsg, ApiMsg

        from omnipage import REC_OK

        lang = ocr.omnipage_ocr_language

        rc = REC_OK

        if (USE_OEM_LICENSE):
            InfoMsg("Setting license information -- kRecSetLicense()")
            rc = kRecSetLicense(LICENSE_FILE, OEM_CODE)
            if (rc != REC_OK):
                ErrMsg("Error code = {}\n", rc)
                kRecQuit()
                return

        # InfoMsg("Initializing the Engine -- kRecInit()")
        # use your company and product name here
        rc = kRecInit(YOUR_COMPANY, YOUR_PRODUCT)
        if ((rc != REC_OK) and (rc != API_INIT_WARN) and (rc != API_LICENSEVALIDATION_WARN)):
            ErrMsg("Error code = {}\n", rc)
            kRecQuit()
            return
        if (rc == API_INIT_WARN):
            InfoMsg("Module initialization warning. One or more")
            InfoMsg("recognition modules haven't been initialized properly.")
            InfoMsg("For more information, see kRecGetModulesInfo()")

        InfoMsg("Reset all settings to their default values -- kRecSetDefaults()")
        rc = kRecSetDefaults(SID)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecQuit()
            return

        InfoMsg("Set current languages -- kRecSetLanguages()")
        if lang == "LANG_ENG":
            langs = CreateEnabledLanguagesArray([LANG_ENG])
        elif lang == "LANG_CHT":
            langs = CreateEnabledLanguagesArray([LANG_CHT, LANG_ENG])
        elif lang == "LANG_CHS":
            langs = CreateEnabledLanguagesArray([LANG_CHS, LANG_ENG])
        else:
            langs = CreateEnabledLanguagesArray([LANG_ENG])

        rc = kRecSetLanguages(SID, langs)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecQuit()
            return

        InfoMsg("Set code page -- kRecSetCodePage()")
        rc = kRecSetCodePage(SID, "UTF-8")
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        InfoMsg(
            "Set default recognition module -- kRecSetDefaultRecognitionModule()")
        rc = kRecSetDefaultRecognitionModule(SID, RM_AUTO)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        InfoMsg("Set output format -- kRecSetDTXTFormat()")
        rc = kRecSetDTXTFormat(SID, DTXT_HOCR)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        InfoMsg("Set code page -- kRecSetCodePage()")
        rc = kRecSetCodePage(SID, "UTF-8")
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        InfoMsg("Loading the specified image -- kRecLoadImgF()")
        rc, hPage = kRecLoadImgF(SID, abs_ocred_image_path, PAGE_NUMBER_0)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        InfoMsg("Processing page from selected image -- kRecRecognize()")
        rc = kRecRecognize(SID, hPage, abs_hocr_path)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        #InfoMsg("Get an output array of the recognized text -- kRecGetLetters()")
        #rc, pText = kRecGetLetters(hPage, II_CURRENT)
        #if (rc != REC_OK):
        #    ErrMsg("Error code = {}", rc)
        #    kRecFreeImg(hPage)
        #    kRecQuit()
        #    return

        #ApiMsg("# Now your application can process the recognized data #")
        #ApiMsg("We just display the recognized OMR information.")
        #pResult = ""
        #for letter in pText:
        #    if (letter.code != ' '):
        #        if (letter.code == '0'):
        #            pResult = "NO"
        #        elif (letter.code == '1'):
        #            pResult = "YES"
        #        else:
        #            pResult = "Rejected"
        #        LoopMsg("{}: '{}' = {}", letter.zone, letter.code, pResult)

        InfoMsg("Free the image -- kRecFreeImg()")
        rc = kRecFreeImg(hPage)
        if (rc != REC_OK):
            ErrMsg("Error code = {}\n", rc)
            kRecSetDefaults(SID)
            kRecQuit()
            return

        kRecSetDefaults(SID)
        InfoMsg("Free all resources allocated by the Engine -- kRecQuit()")
        kRecQuit()

        # Fix Omnipage Bug
        with open(abs_hocr_path, "r", encoding="utf-8", errors="ignore") as f:
            updated_hocr = f.read()
            updated_hocr = updated_hocr.split('</html>')[0] + '</html>'
        with open(abs_hocr_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(updated_hocr)

        xml = convert_hocr_to_xml(abs_hocr_path, abs_xml_path)
        document_page.xml = xml

    elif ocr_engine == "APPLE_VISION":
        from ocrmac import ocrmac
        annotations = ocrmac.OCR(abs_ocred_image_path, language_preference=[ocr.apple_vision_ocr_language]).recognize()
        im = cv2.imread(abs_ocred_image_path)
        height, width, c = im.shape

        hocr_result = export_apple_vision_result_as_hocr(im, annotations)

        with (open(abs_hocr_path, 'wb+')) as outfile:
            outfile.write(hocr_result)
            outfile.close()

        xml = convert_hocr_to_xml(abs_hocr_path, abs_xml_path)
        document_page.xml = xml

    document_page.ocred = True
    document_page.save()

def first_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num):
    first_page_conditions_passed = True
    for splitting_condition in first_page_splitting_rule.splitting_conditions.all():
        streamed_rule_value = ' '.join(get_streamed_by_rule(
            splitting_condition.rule.id, parsed_result_by_page_num[page_num]))
        if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
            if not splitting_condition.value in streamed_rule_value:
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
            if splitting_condition.value in streamed_rule_value:
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
            if not splitting_condition.value == streamed_rule_value:
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
            if not re.search(splitting_condition.value, streamed_rule_value):
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
            if re.search(splitting_condition.value, streamed_rule_value):
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
            if not streamed_rule_value.strip() == "":
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
            if streamed_rule_value.strip() == "":
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
            if page_num == 1:
                continue
            previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                splitting_condition.rule.id,
                parsed_result_by_page_num[page_num - 1]))
            if streamed_rule_value == previous_streamed_rule_value:
                first_page_conditions_passed = False
        elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
            if page_num == 1:
                continue
            previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
            if not streamed_rule_value == previous_streamed_rule_value:
                first_page_conditions_passed = False

    return first_page_conditions_passed

def any_last_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num):

    any_last_page_rules_passed = False
    for last_page_splitting_rule in first_page_splitting_rule.last_page_splitting_rules.all():

        if last_page_splitting_rule.last_page_splitting_rule_type == LastPageSplittingRuleType.BY_CONDITIONS.value:
            last_page_conditions_passed = True
            for splitting_condition in last_page_splitting_rule.last_page_splitting_conditions.all():
                streamed_rule_value = ' '.join(get_streamed_by_rule(
                    splitting_condition.rule.id, parsed_result_by_page_num[page_num]))
                if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                    if not splitting_condition.value in streamed_rule_value:
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                    if splitting_condition.value in streamed_rule_value:
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                    if not splitting_condition.value == streamed_rule_value:
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                    if not re.search(splitting_condition.value, streamed_rule_value):
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                    if re.search(splitting_condition.value, streamed_rule_value):
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                    if not streamed_rule_value.strip() == "":
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                    if streamed_rule_value.strip() == "":
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                    if page_num == 1:
                        continue
                    previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                        splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
                    if streamed_rule_value == previous_streamed_rule_value:
                        last_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                    if page_num == 1:
                        continue
                    previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                        splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
                    if not streamed_rule_value == previous_streamed_rule_value:
                        last_page_conditions_passed = False
            if last_page_conditions_passed:
                any_last_page_rules_passed = True

        elif last_page_splitting_rule.last_page_splitting_rule_type == LastPageSplittingRuleType.WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH.value:

            for first_page_splitting_rule_in_last_rule in first_page_splitting_rule.splitting.splitting_rules.exclude(pk=last_page_splitting_rule.parent_splitting_rule.id).all():
                last_page_conditions_passed = True
                for splitting_condition in first_page_splitting_rule_in_last_rule.splitting_conditions.all():
                    streamed_rule_value = ' '.join(get_streamed_by_rule(
                        splitting_condition.rule.id, parsed_result_by_page_num[page_num]))
                    if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                        if not splitting_condition.value in streamed_rule_value:
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                        if splitting_condition.value in streamed_rule_value:
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                        if not splitting_condition.value == streamed_rule_value:
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                        if not re.search(splitting_condition.value, streamed_rule_value):
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                        if re.search(splitting_condition.value, streamed_rule_value):
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                        if not streamed_rule_value.strip() == "":
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                        if streamed_rule_value.strip() == "":
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                        if page_num == 1:
                            continue
                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                            splitting_condition.rule.id,
                            parsed_result_by_page_num[page_num - 1]))
                        if streamed_rule_value == previous_streamed_rule_value:
                            last_page_conditions_passed = False
                    elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                        if page_num == 1:
                            continue
                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                            splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
                        if not streamed_rule_value == previous_streamed_rule_value:
                            last_page_conditions_passed = False

                if last_page_conditions_passed:

                    any_last_page_rules_passed = True
                    break

    return any_last_page_rules_passed

def any_consecutive_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num):
    any_consecutive_page_rules_passed = False
    for consecutive_page_splitting_rule in first_page_splitting_rule.consecutive_page_splitting_rules.all():
        
        if consecutive_page_splitting_rule.consecutive_page_splitting_rule_type == ConsecutivePageSplittingRuleType.BY_CONDITIONS.value:
            consecutive_page_conditions_passed = True
            for splitting_condition in consecutive_page_splitting_rule.consecutive_page_splitting_conditions.all():
                streamed_rule_value = ' '.join(get_streamed_by_rule(
                    splitting_condition.rule.id, parsed_result_by_page_num[page_num]))
                if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                    if not splitting_condition.value in streamed_rule_value:
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                    if splitting_condition.value in streamed_rule_value:
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                    if not splitting_condition.value == streamed_rule_value:
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                    if not re.search(splitting_condition.value, streamed_rule_value):
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                    if re.search(splitting_condition.value, streamed_rule_value):
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                    if not streamed_rule_value.strip() == "":
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                    if streamed_rule_value.strip() == "":
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                    if page_num == 1:
                        continue
                    previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                        splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
                    if streamed_rule_value == previous_streamed_rule_value:
                        consecutive_page_conditions_passed = False
                elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                    if page_num == 1:
                        continue
                    previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                        splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
                    if not streamed_rule_value == previous_streamed_rule_value:
                        consecutive_page_conditions_passed = False

            if consecutive_page_conditions_passed:
                any_consecutive_page_rules_passed = True

        elif consecutive_page_splitting_rule.consecutive_page_splitting_rule_type == ConsecutivePageSplittingRuleType.WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_DO_NOT_MATCH.value:
            any_other_first_page_splitting_rules_matched = False
            for first_page_splitting_rule_in_consecutive_rule in first_page_splitting_rule.splitting.splitting_rules.exclude(pk=consecutive_page_splitting_rule.parent_splitting_rule.id).all():
                first_page_splitting_rules_matched = True
                for splitting_condition in first_page_splitting_rule_in_consecutive_rule.splitting_conditions.all():
                    streamed_rule_value = ' '.join(get_streamed_by_rule(
                        splitting_condition.rule.id, parsed_result_by_page_num[page_num]))
                    if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                        if not splitting_condition.value in streamed_rule_value:
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                        if splitting_condition.value in streamed_rule_value:
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                        if not splitting_condition.value == streamed_rule_value:
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                        if not re.search(splitting_condition.value, streamed_rule_value):
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                        if re.search(splitting_condition.value, streamed_rule_value):
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                        if not streamed_rule_value.strip() == "":
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                        if streamed_rule_value.strip() == "":
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                        if page_num == 1:
                            continue
                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                            splitting_condition.rule.id,
                            parsed_result_by_page_num[page_num - 1]))
                        if streamed_rule_value == previous_streamed_rule_value:
                            first_page_splitting_rules_matched = False
                    elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                        if page_num == 1:
                            continue
                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                            splitting_condition.rule.id, parsed_result_by_page_num[page_num - 1]))
                        if not streamed_rule_value == previous_streamed_rule_value:
                            first_page_splitting_rules_matched = False

                if first_page_splitting_rules_matched:
                    any_other_first_page_splitting_rules_matched = True
                    break

            any_consecutive_page_rules_passed = not any_other_first_page_splitting_rules_matched

    return any_consecutive_page_rules_passed

def get_parsed_result_in_page_num(document_parser, rules, page_num, parsed_result_by_page_num):
    if not page_num in parsed_result_by_page_num:
        parsed_result = []
        for rule in rules:
            rule.pages = str(page_num)
            result = document_parser.extract_and_stream(rule, parsed_result)

            parsed_result.append(result)
        parsed_result_by_page_num[page_num] = parsed_result
    return parsed_result_by_page_num

def convert_to_searchable_pdf(parser, document: Document, ocr):

    if Splitting.objects.filter(parser_id=parser.id).count() > 0:
        splitting = Splitting.objects.get(parser_id=parser.id)
    else:
        splitting = None
    ocr_engine = ocr.ocr_type

    document_pages = document.document_pages.all()

    # Do the splitting job
    document_page_index = -1

    is_searchable = detect_pdf_is_searchable(source_file_pdf_path(document))

    accumulated_page_nums = []
    parsed_result_by_page_num = {}

    while (document_page_index+1) < len(document_pages):

        document_page_index += 1
        page_num = document_page_index + 1

        document_page = document_pages[document_page_index]

        convert_page(parser, document, ocr, document_page)

        if splitting != None and splitting.activated and not document.splitted:

            document_parser = DocumentParser(parser, document)
            rules = Rule.objects.filter(parser_id=parser.id).all()

            parsed_result_by_page_num = get_parsed_result_in_page_num(document_parser, rules, page_num, parsed_result_by_page_num)

            first_page_conditions_passed = False

            for first_page_splitting_rule in splitting.splitting_rules.all():

                first_page_conditions_passed = first_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num)

                if first_page_conditions_passed:

                    accumulated_page_nums.append(page_num)

                    any_last_page_rules_passed = any_last_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num)

                    if not any_last_page_rules_passed:

                        # if it is not the last page, identify consecutive pages also
                        while (document_page_index+1) < len(document_pages):

                            document_page_index += 1
                            page_num = document_page_index + 1

                            document_page = document_pages[document_page_index]

                            convert_page(parser, document, ocr, document_page)
                            parsed_result_by_page_num = get_parsed_result_in_page_num(document_parser, rules, page_num, parsed_result_by_page_num)

                            any_consecutive_page_rules_passed = any_consecutive_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num)
                                
                            if any_consecutive_page_rules_passed:

                                accumulated_page_nums.append(page_num)

                                any_last_page_rules_passed = any_last_page_conditions_passed_func(page_num, first_page_splitting_rule, parsed_result_by_page_num)

                                if any_last_page_rules_passed:
                                    break

                            else:
                                document_page_index -= 1
                                page_num = document_page_index + 1
                                break

                    break

            if first_page_conditions_passed:

                new_document = Document()
                new_document.document_type = document.document_type
                new_document.guid = str(uuid.uuid4())
                new_document.filename_without_extension = document.filename_without_extension + \
                    "_pages_" + \
                    str(accumulated_page_nums[0]) + \
                    "-" + str(accumulated_page_nums[-1])
                new_document.document_extension = DocumentExtension.PDF.value
                new_document.extension = "pdf"
                new_document.total_page_num = len(
                    accumulated_page_nums)
                new_document.splitted = True
                if parser.type == ParserType.LAYOUT.value:
                    new_document.parser_id = parser.id
                elif parser.type == ParserType.ROUTING.value:
                    route_to_parser_id = first_page_splitting_rule.route_to_parser_id
                    new_document.parser_id = route_to_parser_id
                new_document.last_modified_at = datetime.now()
                new_parser_ocr = OCR.objects.get(
                    parser_id=new_document.parser_id)

                new_documents_path = document_path(new_document)
                if not os.path.exists(new_documents_path):
                    os.makedirs(new_documents_path)

                new_searchable_pdf_path = os.path.join(
                    new_documents_path, 'source_file.pdf')

                fontname = "invisible"
                rendering_first_page = True

                if ocr_engine == "NO_OCR":

                    inputPdf = PdfReader(open(source_file_pdf_path(document), "rb"))
                    outputPdf = PdfWriter()

                    for accumulated_page_num in accumulated_page_nums:

                        i = accumulated_page_num - 1
                        outputPdf.add_page(inputPdf.pages[i])
                    with open(source_file_pdf_path(new_document), "wb") as outputStream:
                        outputPdf.write(outputStream)

                else:
                    
                    for accumulated_page_num in accumulated_page_nums:


                        abs_ocred_image_path = ocred_image_path(
                            document, accumulated_page_num)
                        abs_hocr_path = hocr_path(document, accumulated_page_num)

                        # put the image on the page, scaled to fill the page
                        im = Image.open(abs_ocred_image_path)
                        if 'dpi' in im.info:
                            width = float(im.size[0])/im.info['dpi'][0]
                            height = float(im.size[1])/im.info['dpi'][1]
                        else:
                            width = height = None

                        # a default, in case we can't find it
                        ocr_dpi = (300, 300)
                        # get dimensions of the OCR, which may not match the image
                        if os.path.exists(abs_hocr_path):
                            # Fix Omnipage Bug
                            with open(abs_hocr_path, "r", encoding="utf-8", errors="ignore") as f:
                                updated_hocr = f.read()
                                updated_hocr = updated_hocr.split('</html>')[0] + '</html>'
                            with open(abs_hocr_path, "w", encoding="utf-8", errors="ignore") as f:
                                f.write(updated_hocr)

                            hocr_tree = ET.parse(abs_hocr_path)
                            hocr = hocr_tree.getroot()
                            if hocr is not None:
                                for div in hocr.findall(".//{http://www.w3.org/1999/xhtml}div"):
                                    if div.attrib['class'] == 'ocr_page':
                                        coords = element_coordinates(div)
                                        ocrwidth = coords[2]-coords[0]
                                        ocrheight = coords[3]-coords[1]
                                    if width is None:
                                        # no dpi info with the image
                                        # assume OCR was done at 300 dpi
                                        width = ocrwidth/300
                                        height = ocrheight/300
                                    ocr_dpi = (ocrwidth/width, ocrheight/height)
                                    break  # there shouldn't be more than one, and if there is, we don't want it

                        if width is None:
                            # no dpi info with the image, and no help from the hOCR file either
                            # this will probably end up looking awful, so issue a warning
                            width = float(im.size[0])/96
                            height = float(im.size[1])/96

                        if rendering_first_page:
                            pdf = Canvas(new_searchable_pdf_path, pagesize=(
                                width*inch, height*inch), pageCompression=1)
                            rendering_first_page = False
                        else:
                            pdf.setPageSize((width*inch, height*inch))
                        pdf.drawInlineImage(
                            im, 0, 0, width=width*inch, height=height*inch)

                        im.close()

                        if os.path.exists(abs_hocr_path):
                            for word in hocr.findall(".//{http://www.w3.org/1999/xhtml}span"):
                                if word.attrib['class'] == 'ocrx_word':
                                    coords = element_coordinates(word)

                                    text = pdf.beginText()
                                    text.setTextRenderMode(3)  # invisible

                                    pdf.setLineWidth(0.2)
                                    pdf.setStrokeColor(HexColor(0xff0000))

                                    # set cursor to bottom left corner of line bbox (adjust for dpi)
                                    if ocr_engine == "DOCTR":
                                        x = (float(coords[0])/ocr_dpi[0])*inch
                                        y = (height*inch) - \
                                            (float(coords[3])/ocr_dpi[1])*inch
                                        text_width = (
                                            float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                                        text_height = (
                                            float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                                        fontsize = text_height * 0.40
                                        text.setFont(fontname, fontsize)
                                        text.setTextOrigin(x, y + 4)

                                    elif ocr_engine == "PADDLE":
                                        x = (
                                            float(coords[0])/ocr_dpi[0]) * inch
                                        y = (height*inch) - \
                                            (float(coords[3])/ocr_dpi[1])*inch
                                        text_width = (
                                            float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                                        text_height = (
                                            float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                                        fontsize = text_height * 0.30
                                        text.setFont(fontname, fontsize)
                                        text.setTextOrigin(x, y + 4)

                                    elif ocr_engine == "GOOGLE_VISION":
                                        x = (
                                            float(coords[0])/ocr_dpi[0]) * inch
                                        y = (height*inch) - \
                                            (float(coords[3])/ocr_dpi[1])*inch
                                        text_width = (
                                            float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                                        text_height = (
                                            float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                                        fontsize = text_height * 0.75
                                        text.setFont(fontname, fontsize)
                                        text.setTextOrigin(x, y + 2)

                                    elif ocr_engine == "OMNIPAGE":
                                        x = (
                                            float(coords[0])/ocr_dpi[0]) * inch
                                        y = (height*inch) - \
                                            (float(coords[3])/ocr_dpi[1])*inch
                                        text_width = (
                                            float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                                        text_height = (
                                            float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                                        fontsize = text_height * 0.70
                                        text.setFont(fontname, fontsize)
                                        text.setTextOrigin(x, y + 4)

                                    # redline the word
                                    if ocr.debug:
                                        pdf.rect(x, y, text_width,
                                                text_height, stroke=1, fill=0)

                                        # redline the char
                                        word_in_line_count = 0
                                        word_len = len(word.text)
                                        for char in word.text:

                                            pdf.setLineWidth(0.1)
                                            pdf.setStrokeColor(
                                                HexColor(0x0000ff))

                                            char_xmin = text_width / \
                                                word_len * word_in_line_count + x
                                            char_xmax = text_width / \
                                                word_len * \
                                                (word_in_line_count+1) + x
                                            char_width = char_xmax - char_xmin
                                            pdf.rect(char_xmin, y, char_width,
                                                    text_height, stroke=1, fill=0)

                                            word_in_line_count += 1

                                    # scale the width of the text to fill the width of the line's bbox
                                    if fontsize == 0.0:
                                        fontsize = 10.0
                                    if word.text == None:
                                        word.text = ""
                                        stringWidth = pdf.stringWidth(
                                            " ", fontname, fontsize)
                                    elif word.text == ' ':
                                        stringWidth = pdf.stringWidth(
                                            " ", fontname, fontsize)
                                    elif word.text.rstrip() == '':
                                        stringWidth = pdf.stringWidth(
                                            " ", fontname, fontsize)
                                    else:
                                        stringWidth = pdf.stringWidth(
                                            word.text.rstrip(), fontname, fontsize)
                                    try:
                                        text.setHorizScale(
                                            (((float(coords[2])/ocr_dpi[0]*inch)-(float(coords[0])/ocr_dpi[0]*inch))/stringWidth)*100)
                                    except Exception as e:
                                        traceback.print_exc()
                                        raise e

                                    # write the text to the page
                                    text.textLine(word.text.rstrip())
                                    pdf.drawText(text)

                            # finish up the page and save it
                            pdf.showPage()
                    pdf.save()

                new_document.save()

                # End of generating OCR document

                new_document_page_num_counter = 0
                for accumulated_page_num in accumulated_page_nums:
                    new_document_page_num_counter += 1
                    document_page = document_pages.get(
                        page_num=accumulated_page_num)
                    new_document_page = DocumentPage()
                    new_document_page.page_num = new_document_page_num_counter
                    new_document_page.width = document_page.width
                    new_document_page.height = document_page.height
                    new_document_page.xml = document_page.xml
                    new_document_page.document_id = new_document.id
                    new_document_page.preprocessed = False
                    new_document_page.ocred = True
                    new_document_page.postprocessed = False

                    preprocessings = PreProcessing.objects.order_by(
                        "-step").filter(parser_id=document.parser.id)

                    if len(preprocessings) == 0:
                        document_page_file_path = original_image_path(
                            document, accumulated_page_num)
                    else:
                        last_preprocessing = preprocessings[0]
                        document_page_file_path = pre_processed_image_path(
                            document, last_preprocessing, accumulated_page_num)

                    new_document_page_image_file = original_image_path(
                        new_document, new_document_page_num_counter)
                    shutil.copyfile(
                        document_page_file_path, new_document_page_image_file)

                    new_document_ocr_folder_path = ocr_folder_path(
                        new_document)
                    if not os.path.exists(new_document_ocr_folder_path):
                        os.makedirs(new_document_ocr_folder_path)

                    new_document_ocred_image_path = ocred_image_path(
                        new_document, new_document_page_num_counter)
                    document_ocred_image_path = ocred_image_path(
                        document, accumulated_page_num)
                    shutil.copyfile(
                        document_ocred_image_path, new_document_ocred_image_path)

                    new_document_xml_path = xml_path(
                        new_document, new_document_page_num_counter)
                    document_xml_path = xml_path(
                        document, accumulated_page_num)
                    shutil.copyfile(
                        document_xml_path, new_document_xml_path)
                    with open(new_document_xml_path, 'w', encoding="utf-8") as xml_file:
                        xml_file.write(new_document_page.xml)
                    

                    if not ocr_engine == "NO_OCR":

                        new_document_hocr_path = hocr_path(
                            new_document, new_document_page_num_counter)
                        document_hocr_path = hocr_path(
                            document, accumulated_page_num)
                        shutil.copyfile(
                            document_hocr_path, new_document_hocr_path)

                    new_document_page.save()

                # Create queue object in database
                q = Queue()
                q.queue_status = QueueStatus.READY.value
                if parser.type == ParserType.LAYOUT.value:
                    q.parser_id = parser.id
                elif parser.type == ParserType.ROUTING.value:
                    route_to_parser_id = first_page_splitting_rule.route_to_parser_id
                    q.parser_id = route_to_parser_id
                q.document = new_document
                q.queue_class = QueueClass.OCR.value
                q.save()

                accumulated_page_nums = []

    if ocr_engine == "NO_OCR" or (is_searchable and ocr.detect_searchable):

        abs_source_pdf_path = source_file_pdf_path(document)
        abs_ocred_pdf_path = ocred_pdf_path(document)
        shutil.copy(abs_source_pdf_path,
                    abs_ocred_pdf_path)

    else:
        # if splitting is not activated, generate OCR document

        abs_ocred_pdf_path = ocred_pdf_path(document)

        fontname = "invisible"
        pdf = None

        for document_page in document_pages:
            page_num = document_page.page_num

            abs_ocred_image_path = ocred_image_path(
                document, page_num)
            abs_hocr_path = hocr_path(document, page_num)

            # put the image on the page, scaled to fill the page
            im = Image.open(abs_ocred_image_path)
            if 'dpi' in im.info:
                width = float(im.size[0])/im.info['dpi'][0]
                height = float(im.size[1])/im.info['dpi'][1]
            else:
                width = height = None

            # a default, in case we can't find it
            ocr_dpi = (300, 300)
            # get dimensions of the OCR, which may not match the image
            hocr_tree = ET.parse(abs_hocr_path)
            hocr = hocr_tree.getroot()
            if hocr is not None:
                for div in hocr.findall(".//{http://www.w3.org/1999/xhtml}div"):
                    if div.attrib['class'] == 'ocr_page':
                        coords = element_coordinates(div)
                        ocrwidth = coords[2]-coords[0]
                        ocrheight = coords[3]-coords[1]
                    if width is None:
                        # no dpi info with the image
                        # assume OCR was done at 300 dpi
                        width = ocrwidth/300
                        height = ocrheight/300
                    ocr_dpi = (ocrwidth/width, ocrheight/height)
                    break  # there shouldn't be more than one, and if there is, we don't want it

            if width is None:
                # no dpi info with the image, and no help from the hOCR file either
                # this will probably end up looking awful, so issue a warning
                width = float(im.size[0])/96
                height = float(im.size[1])/96

            if page_num == 1:
                pdf = Canvas(abs_ocred_pdf_path, pagesize=(
                    width*inch, height*inch), pageCompression=1)
            else:
                pdf.setPageSize((width*inch, height*inch))
            pdf.drawInlineImage(
                im, 0, 0, width=width*inch, height=height*inch)

            im.close()

            if hocr is not None:
                for word in hocr.findall(".//{http://www.w3.org/1999/xhtml}span"):
                    if word.attrib['class'] == 'ocrx_word':
                        coords = element_coordinates(word)

                        text = pdf.beginText()
                        text.setTextRenderMode(3)  # invisible

                        pdf.setLineWidth(0.2)
                        pdf.setStrokeColor(HexColor(0xff0000))

                        # set cursor to bottom left corner of line bbox (adjust for dpi)
                        if ocr_engine == "DOCTR":
                            x = (float(coords[0])/ocr_dpi[0])*inch
                            y = (height*inch) - \
                                (float(coords[3])/ocr_dpi[1])*inch
                            text_width = (
                                float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                            text_height = (
                                float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                            fontsize = text_height * 0.40
                            text.setFont(fontname, fontsize)
                            text.setTextOrigin(x, y + 4)

                        elif ocr_engine == "PADDLE":
                            x = (
                                float(coords[0])/ocr_dpi[0]) * inch
                            y = (height*inch) - \
                                (float(coords[3])/ocr_dpi[1])*inch
                            text_width = (
                                float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                            text_height = (
                                float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                            fontsize = text_height * 0.30
                            text.setFont(fontname, fontsize)
                            text.setTextOrigin(x, y + 4)

                        elif ocr_engine == "GOOGLE_VISION":
                            x = (
                                float(coords[0])/ocr_dpi[0]) * inch
                            y = (height*inch) - \
                                (float(coords[3])/ocr_dpi[1])*inch
                            text_width = (
                                float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                            text_height = (
                                float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                            fontsize = text_height * 0.75
                            text.setFont(fontname, fontsize)
                            text.setTextOrigin(x, y + 1)

                        elif ocr_engine == "OMNIPAGE":
                            x = (
                                float(coords[0])/ocr_dpi[0]) * inch
                            y = (height*inch) - \
                                (float(coords[3])/ocr_dpi[1])*inch
                            text_width = (
                                float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                            text_height = (
                                float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                            fontsize = text_height * 0.70
                            text.setFont(fontname, fontsize)
                            text.setTextOrigin(x, y + 4)

                        elif ocr_engine == "APPLE_VISION":
                            x = (
                                float(coords[0])/ocr_dpi[0]) * inch
                            y = (height*inch) - \
                                (float(coords[3])/ocr_dpi[1])*inch
                            text_width = (
                                float(coords[2])/ocr_dpi[0])*inch - (float(coords[0])/ocr_dpi[0])*inch
                            text_height = (
                                float(coords[3])/ocr_dpi[0])*inch - (float(coords[1])/ocr_dpi[1])*inch
                            fontsize = text_height * 0.70
                            text.setFont(fontname, fontsize)
                            text.setTextOrigin(x, y + 4)

                        # redline the word
                        if ocr.debug:
                            pdf.rect(x, y, text_width,
                                    text_height, stroke=1, fill=0)

                            # redline the char
                            word_in_line_count = 0
                            word_len = len(word.text)
                            for char in word.text:

                                pdf.setLineWidth(0.1)
                                pdf.setStrokeColor(
                                    HexColor(0x0000ff))

                                char_xmin = text_width / \
                                    word_len * word_in_line_count + x
                                char_xmax = text_width / \
                                    word_len * \
                                    (word_in_line_count+1) + x
                                char_width = char_xmax - char_xmin
                                pdf.rect(char_xmin, y, char_width,
                                        text_height, stroke=1, fill=0)

                                word_in_line_count += 1

                        # scale the width of the text to fill the width of the line's bbox
                        if fontsize == 0.0:
                            fontsize = 10.0
                        if word.text == None:
                            word.text = ""
                            stringWidth = pdf.stringWidth(
                                " ", fontname, fontsize)
                        elif word.text == ' ':
                            stringWidth = pdf.stringWidth(
                                " ", fontname, fontsize)
                        elif word.text.rstrip() == '':
                            stringWidth = pdf.stringWidth(
                                " ", fontname, fontsize)
                        else:
                            stringWidth = pdf.stringWidth(
                                word.text.rstrip(), fontname, fontsize)
                        try:
                            text.setHorizScale(
                                (((float(coords[2])/ocr_dpi[0]*inch)-(float(coords[0])/ocr_dpi[0]*inch))/stringWidth)*100)
                        except Exception as e:
                            traceback.print_exc()
                            raise e

                        # write the text to the page
                        text.textLine(word.text.rstrip())
                        pdf.drawText(text)

            # finish up the page and save it
            pdf.showPage()
        pdf.save()

        # End of generating OCR document

def export_as_hocr(im, result):
    """Export the page as hOCR-format"""
    p_idx = 1
    block_count: int = 1
    line_count: int = 1
    word_count: int = 1
    (height, width, c) = im.shape
    language = "en"
    # Create the XML root element
    page_hocr = ETElement("html", attrib={
                          "xmlns": "http://www.w3.org/1999/xhtml", "xml:lang": str(language)})
    # Create the header / SubElements of the root element
    head = SubElement(page_hocr, "head")
    SubElement(head, "title").text = "Paddle OCR hocr"
    SubElement(head, "meta", attrib={
               "http-equiv": "Content-Type", "content": "text/html; charset=utf-8"})
    SubElement(
        head,
        "meta",
        attrib={"name": "ocr-system", "content": f"paddleocr"},
    )
    SubElement(
        head,
        "meta",
        attrib={"name": "ocr-capabilities",
                "content": "ocr_page ocr_carea ocr_par ocr_line ocrx_word"},
    )
    # Create the body
    body = SubElement(page_hocr, "body")
    page = SubElement(
        body,
        "div",
        attrib={
            "class": "ocr_page",
            "id": f"page_{p_idx}",
            "title": f"image; bbox 0 0 {width} {height}; ppageno 0",
        },
    )

    # iterate over the blocks / lines / words and create the XML elements in body line by line with the attributes
    for line in result[0]:
        xmin = line[0][0][0]
        ymin = line[0][0][1]
        xmax = line[0][2][0]
        ymax = line[0][2][1]

        # NOTE: baseline, x_size, x_descenders, x_ascenders is currently initalized to 0
        block_span = SubElement(
            body,
            "div",
            attrib={
                "class": "ocr_carea",
                "id": f"block_{line_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}",
            },
        )
        paragraph_span = SubElement(
            block_span,
            "p",
            attrib={
                "class": "ocr_par",
                "id": f"par_{line_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}",
            },
        )
        line_span = SubElement(
            paragraph_span,
            "span",
            attrib={
                "class": "ocr_line",
                "id": f"line_{line_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}; baseline 0 0; x_size 0; x_descenders 0; x_ascenders 0",
            },
        )
        line_count += 1
        word_in_line_count = 0
        confs = []
        for word in line[1][0]:
            conf = line[1][1]
            confs.append(conf)
        confs_mean = mean(confs)
        word_div = SubElement(
            line_span,
            "span",
            attrib={
                "class": "ocrx_word",
                "id": f"word_{word_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}; x_wconf {int(round(confs_mean * 100))}",
            },
        )
        word_div.text = ""
        for word in line[1][0]:
            """word_xmin = (xmax - xmin) / \
                len(line[1][0]) * word_in_line_count + xmin
            word_xmax = (xmax - xmin) / \
                len(line[1][0]) * (word_in_line_count+1) + xmin
            word_ymin = ymin
            word_ymax = ymax
            conf = line[1][1]"""
            # set the text
            word_div.text += word
            word_count += 1
            word_in_line_count += 1

    return tostring(page_hocr, encoding="utf-8", method="xml")

def export_apple_vision_result_as_hocr(im, result):
    """Export the page as hOCR-format"""
    p_idx = 1
    block_count: int = 1
    line_count: int = 1
    word_count: int = 1
    (height, width, c) = im.shape
    language = "en"
    # Create the XML root element
    page_hocr = ETElement("html", attrib={
                          "xmlns": "http://www.w3.org/1999/xhtml", "xml:lang": str(language)})
    # Create the header / SubElements of the root element
    head = SubElement(page_hocr, "head")
    SubElement(head, "title").text = "Paddle OCR hocr"
    SubElement(head, "meta", attrib={
               "http-equiv": "Content-Type", "content": "text/html; charset=utf-8"})
    SubElement(
        head,
        "meta",
        attrib={"name": "ocr-system", "content": f"paddleocr"},
    )
    SubElement(
        head,
        "meta",
        attrib={"name": "ocr-capabilities",
                "content": "ocr_page ocr_carea ocr_par ocr_line ocrx_word"},
    )
    # Create the body
    body = SubElement(page_hocr, "body")
    page = SubElement(
        body,
        "div",
        attrib={
            "class": "ocr_page",
            "id": f"page_{p_idx}",
            "title": f"image; bbox 0 0 {width} {height}; ppageno 0",
        },
    )

    # iterate over the blocks / lines / words and create the XML elements in body line by line with the attributes
    for line in result:
        x = line[2][0] * width
        y = line[2][1] * height
        line_width = line[2][2] * width
        line_height = line[2][3] * height
        xmin = x
        ymin = height - y - line_height
        xmax = x + line_width
        ymax = height - y

        # NOTE: baseline, x_size, x_descenders, x_ascenders is currently initalized to 0
        block_span = SubElement(
            body,
            "div",
            attrib={
                "class": "ocr_carea",
                "id": f"block_{line_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}",
            },
        )
        paragraph_span = SubElement(
            block_span,
            "p",
            attrib={
                "class": "ocr_par",
                "id": f"par_{line_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}",
            },
        )
        line_span = SubElement(
            paragraph_span,
            "span",
            attrib={
                "class": "ocr_line",
                "id": f"line_{line_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}; baseline 0 0; x_size 0; x_descenders 0; x_ascenders 0",
            },
        )
        line_count += 1
        word_in_line_count = 0
        confs = []
        for word in line[0]:
            conf = line[1]
            confs.append(conf)
        confs_mean = mean(confs)
        word_div = SubElement(
            line_span,
            "span",
            attrib={
                "class": "ocrx_word",
                "id": f"word_{word_count}",
                "title": f"bbox {int(round(xmin))} {int(round(ymin))} {int(round(xmax))} {int(round(ymax))}; x_wconf {int(round(confs_mean * 100))}",
            },
        )
        word_div.text = ""
        for word in line[0]:
            """word_xmin = (xmax - xmin) / \
                len(line[1][0]) * word_in_line_count + xmin
            word_xmax = (xmax - xmin) / \
                len(line[1][0]) * (word_in_line_count+1) + xmin
            word_ymin = ymin
            word_ymax = ymax
            conf = line[1][1]"""
            # set the text
            word_div.text += word
            word_count += 1
            word_in_line_count += 1

    return tostring(page_hocr, encoding="utf-8", method="xml")


def convert_hocr_to_xml(hocr_path, xml_path):

    xml = ET.fromstring('<pages></pages>')

    with open(hocr_path, encoding="utf8") as f:
        hocr_string = f.read().encode()

        hocr = lxml.html.fromstring(hocr_string)

        for ocr_page in hocr.cssselect('div.ocr_page'):
            page_bbox_str = ocr_page.attrib['title']
            print(page_bbox_str)
            page_bbox_search = re.search(r'image[ \";:\\/\-\&.A-Za-z0-9]*bbox ([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+); ppageno [0-9]+[ ;A-Za-z_0-9]*',
                                         page_bbox_str,
                                         re.IGNORECASE
                                         )
            page_width = int(page_bbox_search.group(3))
            page_height = int(page_bbox_search.group(4))
            # print("page_width: " + str(page_width))
            # print("page_height: " + str(page_height))
            page = SubElement(xml, "page", attrib={
                "bbox": "0.000,0.000," + str(page_width) + "," + str(page_height)})
            
        for ocr_line in hocr.cssselect('span.ocr_line'):
            ocr_line_bbox_str = ocr_line.attrib['title']
            ocr_line_bbox_search = re.search('bbox ([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)(?:;\s+baseline\s+(?:[0-9.]+)\s+(?:[0-9.]+))?',
                                            ocr_line_bbox_str,
                                            re.IGNORECASE
                                            )
            ocr_line_x1 = int(ocr_line_bbox_search.group(1))
            ocr_line_y1 = page_height - int(ocr_line_bbox_search.group(4))
            ocr_line_x2 = int(ocr_line_bbox_search.group(3))
            ocr_line_y2 = page_height - int(ocr_line_bbox_search.group(2))

            for ocrx_word in ocr_line.cssselect('span.ocrx_word'):
                ocrx_word_bbox_str = ocrx_word.attrib['title']
                ocrx_word_bbox_search = re.search('bbox ([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)(?:;\s+x_wconf\s+([0-9.]+))?',
                                                ocrx_word_bbox_str,
                                                re.IGNORECASE
                                                )
                ocrx_word_x1 = int(ocrx_word_bbox_search.group(1))
                ocrx_word_y1 = page_height - int(ocrx_word_bbox_search.group(4))
                ocrx_word_x2 = int(ocrx_word_bbox_search.group(3))
                ocrx_word_y2 = page_height - int(ocrx_word_bbox_search.group(2))
                ocrx_word_conf = ocrx_word_bbox_search.group(5)
            
                textline = SubElement(
                    page,
                    "textline",
                    attrib={
                        "bbox": str(ocrx_word_x1) + "," + str(ocrx_word_y1) + "," + str(ocrx_word_x2) + "," + str(ocrx_word_y2),
                    },
                )

                width_of_word = ocrx_word_x2 - ocrx_word_x1

                if ocrx_word_conf == None:
                    ocrx_word_conf = 1
                ocrx_word_text = ocrx_word.text

                word_in_line_count = 0
                if ocrx_word_text != None:
                    for char in ocrx_word_text:
                        char_x1 = (ocrx_word_x2 - ocrx_word_x1) / \
                            len(ocrx_word_text) * word_in_line_count + ocrx_word_x1
                        char_x2 = (ocrx_word_x2 - ocrx_word_x1) / \
                            len(ocrx_word_text) * \
                            (word_in_line_count + 1) + ocrx_word_x1
                        char_y1 = ocrx_word_y1
                        char_y2 = ocrx_word_y2

                        char_x1 = int(char_x1)
                        char_y1 = int(char_y1)
                        char_x2 = int(char_x2)
                        char_y2 = int(char_y2)

                        text = SubElement(
                            textline,
                            "text",
                            attrib={
                                "font": "AAAAAA+invisible",
                                "bbox": str(char_x1) + "," + str(char_y1) + "," + str(char_x2) + "," + str(char_y2),
                                "conf": str(ocrx_word_conf)
                            },
                        )

                        text.text = char

                        word_in_line_count += 1

    ET.ElementTree(xml).write(xml_path, xml_declaration=True, encoding="utf-8")

    return ET.tostring(xml, encoding='unicode', xml_declaration=True)
