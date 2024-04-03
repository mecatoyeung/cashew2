import os

import fitz

from PIL import Image

from parsers.models.document_page import DocumentPage

from backend.settings import MEDIA_ROOT


def generate_images_from_pdf(parser, document):
    try:
        folder_path = os.path.join(
            MEDIA_ROOT, 'documents/%s/' % (document.guid))
        abs_pdf_path = os.path.join(
            folder_path, 'source_file.pdf')

        dpi = parser.pdf_to_image_dpi
        zoom = dpi / 72

        magnify = fitz.Matrix(zoom, zoom)
        with fitz.open(abs_pdf_path) as doc:
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                
                pix = page.get_pixmap(matrix=magnify)
                abs_png_path = os.path.join(
                    folder_path, str(page_num) + ".jpg")
                pix.save(abs_png_path)

                im = Image.open(abs_png_path)
                im.thumbnail((3508, 3508), Image.Resampling.LANCZOS)
                im.save(abs_png_path, "JPEG", quality=80)

                width, height = im.size

                dp = DocumentPage(
                    document=document,
                    page_num=page_num,
                    width=width,
                    height=height
                )
                dp.save()

            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        print(e)
