import os

import fitz

from PIL import Image

from parsers.models.document_page import DocumentPage

from backend.settings import MEDIA_ROOT


def generate_images_from_pdf(document):
    try:
        folder_path = os.path.join(
            MEDIA_ROOT, 'documents/%s/' % (document.guid))
        abs_pdf_path = os.path.join(
            folder_path, 'source_file.pdf')

        dpi = 300  # choose desired dpi here
        zoom = dpi / 72  # zoom factor, standard: 72 dpi

        magnify = fitz.Matrix(zoom, zoom)
        with fitz.open(abs_pdf_path) as doc:  # open document
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                # render page to an image
                pix = page.get_pixmap(matrix=magnify)
                abs_png_path = os.path.join(
                    folder_path, str(page_num) + ".jpg")
                pix.save(abs_png_path)

                im = Image.open(abs_png_path)
                im.thumbnail((3508, 3508), Image.Resampling.LANCZOS)
                im.save(abs_png_path, "JPEG", quality=80)

                width, height = im.size
                # width = pix.width
                # height = pix.height

                # Create document page object in database
                dp = DocumentPage(
                    document=document,
                    page_num=page_num,
                    width=width,
                    height=height
                )
                dp.save()

            # Update total page num
            document.total_page_num = len(doc)
            document.save()
    except Exception as e:
        print(e)
