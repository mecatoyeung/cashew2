import os
from pdf2image import convert_from_path
from PIL import Image

max_width = 1000
max_height = 1000


def convert_pdf_to_image(pdf_path, working_path, poppler_path):
    pdf_images = convert_from_path(
        pdf_path, poppler_path=poppler_path, dpi=300)
    for page_idx, pdf_image in enumerate(pdf_images):
        pdf_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        page_num = page_idx + 1
        png_path = os.path.join(str(page_num) + ".jpg")
        full_png_path = os.path.join(working_path, png_path)
        pdf_image.save(full_png_path, format='jpg')

