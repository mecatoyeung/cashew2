import os
from pathlib import Path
import requests
import json
import base64
from functools import cmp_to_key
from .convert_pdf_to_image import convert_pdf_to_image
from .gcv2hocr import fromResponse

import argparse
import glob
import io
import re
import sys
import zlib
import cv2

from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import torch

from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from lxml import etree, html
from PIL import Image

GOOGLE_VISION_API_KEY = "AIzaSyDoNvelJ3f7-dtCuNAnCry8IeBXqJ2rAmk"

WORKING_DIR = os.getcwd() + "/imgdir/"


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


def export_pdf(playground, default_dpi, savefile=False):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    images = sorted(glob.glob(os.path.join(playground, '*.jpg')))
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
            font_width = pdf.stringWidth(rawtext, 'invisible', 8)
            if font_width <= 0:
                continue
            box = p1.search(word.attrib['title']).group(1).split()
            box = [float(i) for i in box]
            b = polyval(baseline,
                        (box[0] + box[2]) / 2 - linebox[0]) + linebox[3]
            text = pdf.beginText()
            text.setTextRenderMode(3)  # double invisible
            text.setFont('invisible', 8)
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


def convert_to_searchable_pdf_doctr(pdf_path,
                                    searchable_pdf_path,
                                    working_path,
                                    poppler_path):
    convert_pdf_to_image(pdf_path, working_path=working_path,
                         poppler_path=poppler_path)
    for dirpath, _, filenames in os.walk(working_path):
        for filename in filenames:
            if filename.endswith(".jpg") or filename.endswith(".JPG"):

                # doctr to ocr image

                os.add_dll_directory(
                    r"C:\Program Files\GTK3-Runtime Win64\bin")
                device = torch.device("cpu")
                model = ocr_predictor(
                    det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True).to(device)
                doc = DocumentFile.from_images(working_path + "\\" + filename)
                result = model(doc)
                xml_output = result.export_as_xml()[0][1]

                hocr_filename = working_path + "\\" + \
                    Path(filename).stem + ".hocr"
                with open(hocr_filename, 'wb') as outfile:
                    xml_output.write(outfile)
                    outfile.close()

        # Convert .hocr to .pdf
        export_pdf(working_path, 144, searchable_pdf_path)

# current_path = Path(__file__)

# convert_to_searchable_pdf(".\\香港常用字.pdf", ".\\OCRed.pdf",
        # working_path=WORKING_DIR,
        # poppler_path=os.path.join(os.path.join(current_path.parent, "app", "poppler", "Library", "bin")))
