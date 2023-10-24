import pytesseract
import matplotlib.pyplot as plt
import torch
import os
import shutil
from pathlib import Path

import argparse
import glob
import io
import re
import sys
import zlib
import cv2
from reportlab.pdfgen.canvas import Canvas

import numpy as np
import cv2

from pdf2image import convert_from_path

from PIL import Image

from backend.settings import MEDIA_URL

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def convert_images_to_pdf(images, output_file_path):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    pdf = Canvas(output_file_path, pageCompression=1)
    dpi = 144
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
        pdf.showPage()
    pdf.save()


def rotate_image(mat, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """

    height, width = mat.shape[:2]  # image shape has 3 dimensions
    # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape
    image_center = (width/2, height/2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def detect_orientation(document, preprocessing, last_preprocessing=None):

    media_folder_path = MEDIA_URL
    documents_folder_path = os.path.join(
        media_folder_path, "documents", str(document.guid))
    working_path = os.path.join(
        documents_folder_path, "pre_processed-" + str(preprocessing.id))
    is_working_dir_exist = os.path.exists(working_path)
    if not is_working_dir_exist:
        os.makedirs(working_path)

    image_paths = []

    for page_idx in range(document.total_page_num):
        page_no = page_idx + 1
        png_path = os.path.join(str(page_no) + ".png")
        new_preprocessed_image_path = os.path.join(working_path, png_path)
        if last_preprocessing == None:
            last_preprocessed_image_path = os.path.join(
                documents_folder_path, "source_file-" + str(page_no) + ".png")
        else:
            last_preprocessed_image_path = os.path.join(
                documents_folder_path, "pre_processed-" + str(last_preprocessing.id), str(page_no) + ".png")
        shutil.copy(last_preprocessed_image_path, new_preprocessed_image_path)

        im = cv2.imread(new_preprocessed_image_path)

        osd = pytesseract.image_to_osd(im, output_type='dict')

        if osd["orientation"] == 0:
            rotated_im = im
        elif osd["orientation"] == 90:
            rotated_im = rotate_image(im, 270)
        elif osd["orientation"] == 180:
            rotated_im = rotate_image(im, 180)
        elif osd["orientation"] == 270:
            rotated_im = rotate_image(im, 90)

        cv2.imwrite(new_preprocessed_image_path, rotated_im)

        image_paths.append(new_preprocessed_image_path)

    output_pdf_path = os.path.join(
        documents_folder_path, "pre_processed-" + str(preprocessing.id), "output.pdf")
    convert_images_to_pdf(image_paths, output_pdf_path)
