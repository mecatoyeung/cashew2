import os
from pdf2image import convert_from_path


def convert_pdf_to_image(pdf_path, working_path, poppler_path):
    pdf_images = convert_from_path(
        pdf_path, poppler_path=poppler_path, dpi=300)
    for page_idx, pdf_image in enumerate(pdf_images):
        page_no = page_idx + 1
        png_path = os.path.join(str(page_no) + ".png")
        full_png_path = os.path.join(working_path, png_path)
        pdf_image.save(full_png_path, 'PNG')
