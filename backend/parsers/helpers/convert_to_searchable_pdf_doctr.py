import os
from pathlib import Path
import base64
import shutil
from functools import cmp_to_key

import glob
import io
import re
import sys
import zlib
import torch

from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from django.db import transaction

from lxml import etree, html
from PIL import Image

from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus
from parsers.helpers.convert_pdf_to_xml import convert_pdf_to_xml

from django.db import transaction


class StdoutWrapper:
    """
    Wrapper around stdout that ensures 'bytes' data is decoded
    to 'latin1' (0x00 - 0xff) before writing out. This is necessary for
    the invisible font to be injected as bytes but written out as a string.
    """

    def write(self, data, *args, **kwargs):
        if bytes != str and isinstance(data, bytes):
            data = data.decode('latin1')
        sys.stdout.write(data)


def export_pdf_bytes(images, default_dpi, savefile=False):
    buffer = io.BytesIO()
    if len(images) == 0:
        sys.exit(0)
    load_invisible_font()
    pdf = Canvas(buffer)
    pdf.setCreator('hocr-tools')
    pdf.setTitle(os.path.basename("temp file"))
    dpi = default_dpi
    for image in images:
        im = Image.open(image)
        w, h = im.size
        try:
            dpi = im.info['dpi'][0]
        except KeyError:
            pass
        width = w * 72 / dpi
        height = h * 72 / dpi
        pdf.setPageSize((width, height))
        pdf.drawImage(image, 0, 0, width=width, height=height)
        add_text_layer(pdf, image, height, dpi)
        pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer


def export_pdf(playground, default_dpi, savefile=False):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    images = glob.glob(os.path.join(playground, '*.jpg'))
    images.sort(key=lambda x: int(Path(x).stem))
    if len(images) == 0:
        print(f"WARNING: No JPG images found in the folder {playground}"
              "\nScript cannot proceed without them and will terminate now.\n")
        sys.exit(0)
    load_invisible_font()
    pdf = Canvas(savefile if savefile else StdoutWrapper(), pageCompression=1)
    pdf.setCreator('hocr-tools')
    pdf.setTitle(os.path.basename(playground))
    dpi = default_dpi
    for image in images:
        im = Image.open(image)
        w, h = im.size
        try:
            dpi = im.info['dpi'][0]
        except KeyError:
            pass
        width = w * 72 / dpi
        height = h * 72 / dpi
        pdf.setPageSize((width, height))
        pdf.drawImage(image, 0, 0, width=width, height=height)
        add_text_layer(pdf, image, height, dpi)
        pdf.showPage()
    pdf.save()


def add_text_layer(pdf, image, height, dpi):
    """Draw an invisible text layer for OCR data"""
    p1 = re.compile(r'bbox((\s+\d+){4})')
    p2 = re.compile(r'baseline((\s+[\d\.\-]+){2})')
    hocrfile = os.path.splitext(image)[0] + ".hocr"
    hocr = etree.parse(hocrfile, html.XHTMLParser())
    line_infos = []
    for line in hocr.xpath('//*[@class="ocr_line"]'):
        if p1.search(line.attrib['title']) == None:
            continue
        linebox = p1.search(line.attrib['title']).group(1).split()
        linebox = [float(i) for i in linebox]
        line_info = [line, linebox]
        line_infos.append(line_info)

    sorted(line_infos, key=cmp_to_key(
        lambda x, y: x[1][0] - y[1][0] if x[1][1] == y[1][1] else x[1][1] - y[1][1]))

    for line_info in line_infos:
        line = line_info[0]
        linebox = p1.search(line.attrib['title']).group(1).split()
        try:
            baseline = p2.search(line.attrib['title']).group(1).split()
        except AttributeError:
            baseline = [0, 0]
        linebox = [float(i) for i in linebox]
        baseline = [float(i) for i in baseline]
        xpath_elements = './/*[@class="ocrx_word"]'
        if (not (line.xpath('boolean(' + xpath_elements + ')'))):
            # if there are no words elements present,
            # we switch to lines as elements
            xpath_elements = '.'
        for word in line.xpath(xpath_elements):
            rawtext = word.text_content().strip()
            font_width = pdf.stringWidth(rawtext, 'invisible', 7)
            if font_width <= 0:
                continue
            box = p1.search(word.attrib['title']).group(1).split()
            box = [float(i) for i in box]
            b = polyval(baseline,
                        (box[0] + box[2]) / 2 - linebox[0]) + linebox[3]
            text = pdf.beginText()
            text.setTextRenderMode(3)  # double invisible
            text.setFont('invisible', 7)
            text.setTextOrigin(box[0] * 72 / dpi, height - box[3] * 72 / dpi)
            box_width = (box[2] - box[0]) * 72 / dpi
            text.setHorizScale(100.0 * box_width / font_width)
            rawtext = get_display(rawtext)
            text.textLine(rawtext)
            pdf.drawText(text)


def polyval(poly, x):
    return x * poly[0] + poly[1]


# Glyphless variation of vedaal's invisible font retrieved from
# http://www.angelfire.com/pr/pgpf/if.html, which says:
# 'Invisible font' is unrestricted freeware. Enjoy, Improve, Distribute freely
def load_invisible_font():
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


doctr_model = None


def convert_to_searchable_pdf_doctr(document,
                                    searchable_pdf_path,
                                    document_path,
                                    preprocessings=[]):

    from doctr.models import ocr_predictor
    from doctr.io import DocumentFile

    working_path = os.path.join(
        document_path, "ocr")

    if (len(preprocessings) > 0):
        last_preprocessing = preprocessings.order_by('-step')[0]
        last_preprocessing_id = last_preprocessing.id
        last_preprocessing_folder_path = os.path.join(
            document_path, "pre_processed-" + str(last_preprocessing_id))
        for dirpath, _, filenames in os.walk(last_preprocessing_folder_path):
            for filename in filenames:
                if filename.endswith(".jpg") or filename.endswith(".JPG"):
                    ocr_image_path = os.path.join(working_path, filename)
                    if os.path.exists(ocr_image_path):
                        continue
                    preprocessed_image_path = os.path.join(
                        last_preprocessing_folder_path, filename)
                    shutil.copy(preprocessed_image_path,
                                ocr_image_path)
    else:
        for dirpath, _, filenames in os.walk(document_path):
            for filename in filenames:
                if filename.endswith(".jpg") or filename.endswith(".JPG"):
                    ocr_image_path = os.path.join(working_path, filename)
                    if os.path.exists(ocr_image_path):
                        continue
                    preprocessed_image_path = os.path.join(
                        document_path, filename)
                    shutil.copy(preprocessed_image_path,
                                ocr_image_path)

    document_pages = list(document.document_pages.order_by("page_num"))
    for document_page in document_pages:
        # Check if Pre-Processing has been stopped
        queue = Queue.objects.get(
            document_id=document.id
        )
        if queue.queue_status == QueueStatus.STOPPED.value:
            queue.queue_class = QueueClass.PROCESSED.value
            queue.queue_status = QueueStatus.COMPLETED.value
            queue.save()
            break

        if document_page.ocred:
            continue

        filename = str(document_page.page_num) + ".jpg"

        # doctr to ocr image

        os.add_dll_directory(
            r"C:\Program Files\GTK3-Runtime Win64\bin")
        global doctr_model
        if doctr_model == None:
            device = torch.device("cpu")
            doctr_model = ocr_predictor(
                det_arch='db_mobilenet_v3_large', reco_arch='crnn_vgg16_bn', pretrained=True).to(device)
        doc = DocumentFile.from_images(working_path + "\\" + filename)
        result = doctr_model(doc)

        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:

                    geometry_0 = list(line.geometry[0])

                    geometry_0[0] = geometry_0[0] + 0.005
                    if geometry_0[1] < 0.25:
                        geometry_0[1] = geometry_0[1] - 0.00475
                    elif geometry_0[1] < 0.5:
                        geometry_0[1] = geometry_0[1] - 0.005
                    elif geometry_0[1] < 0.75:
                        geometry_0[1] = geometry_0[1] - 0.00525
                    else:
                        geometry_0[1] = geometry_0[1] - 0.0055
                    geometry_1 = list(line.geometry[1])
                    geometry_1[0] = geometry_1[0] - 0.005
                    if geometry_1[1] < 0.25:
                        geometry_1[1] = geometry_1[1] - 0.00475
                    elif geometry_1[1] < 0.5:
                        geometry_1[1] = geometry_1[1] - 0.005
                    elif geometry_1[1] < 0.75:
                        geometry_1[1] = geometry_1[1] - 0.00525
                    else:
                        geometry_1[1] = geometry_1[1] - 0.0055
                    geometry_0[1] = geometry_0[1]

                    geometry_1 = list(line.geometry[1])
                    geometry_1[0] = geometry_1[0]
                    geometry_1[1] = geometry_1[1]

                    geometry_0 = tuple(geometry_0)
                    geometry_1 = tuple(geometry_1)

                    line.geometry = tuple([geometry_0, geometry_1])

                    for word_index in range(len(line.words)):
                        word = line.words[word_index]
                        geometry_0 = list(word.geometry[0])

                        if geometry_0[1] < 0.25:
                            geometry_0[1] = geometry_0[1] - 0.00475
                        elif geometry_0[1] < 0.5:
                            geometry_0[1] = geometry_0[1] - 0.005
                        elif geometry_0[1] < 0.75:
                            geometry_0[1] = geometry_0[1] - 0.00525
                        else:
                            geometry_0[1] = geometry_0[1] - 0.0055
                        geometry_1 = list(word.geometry[1])
                        geometry_1[0] = geometry_1[0] - 0.005
                        if geometry_1[1] < 0.25:
                            geometry_1[1] = geometry_1[1] - 0.00475
                        elif geometry_1[1] < 0.5:
                            geometry_1[1] = geometry_1[1] - 0.005
                        elif geometry_1[1] < 0.75:
                            geometry_1[1] = geometry_1[1] - 0.00525
                        else:
                            geometry_1[1] = geometry_1[1] - 0.0055

                        geometry_0 = tuple(geometry_0)
                        geometry_1 = tuple(geometry_1)

                        word.geometry = tuple([geometry_0, geometry_1])

                        if word_index < len(line.words):
                            word.value = word.value + " "

        hocr_output = result.export_as_xml()[0][1]

        hocr_filename = working_path + "\\" + \
            Path(filename).stem + ".hocr"
        with open(hocr_filename, 'wb') as outfile:
            hocr_output.write(outfile)
            outfile.close()

        # Extract .xml and put into database
        image_path = working_path + "\\" + filename
        temp_pdf_bytes = export_pdf_bytes(
            [image_path], 300)

        single_page_pdf_path = working_path + "\\" + \
            Path(filename).stem + ".pdf"
        with open(single_page_pdf_path, "wb") as pdf_f:
            pdf_f.write(temp_pdf_bytes.read())
            pdf_f.close()

        xml = convert_pdf_to_xml(single_page_pdf_path)

        xml_filename = working_path + "\\" + \
            Path(filename).stem + ".xml"
        with open(xml_filename, "w", encoding="utf-8") as f:
            f.write(xml)

        document_page.xml = xml
        document_page.ocred = True
        document_page.save()

        # lower dpi to reduce file size

    # Convert .hocr to .pdf
    export_pdf(working_path, 72, searchable_pdf_path)
