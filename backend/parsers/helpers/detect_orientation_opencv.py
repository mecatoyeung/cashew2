import os
import cv2
import numpy as np
import math
from statistics import median_low
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

from scipy import ndimage

from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus

from parsers.helpers.path_helpers import original_image_path, pre_processing_folder_path, pre_processed_image_path

def get_max_width_length_ratio(contour: np.ndarray) -> float:
    _, (w, h), _ = cv2.minAreaRect(contour)
    if w == 0 or h == 0: return 1
    return max(w / h, h / w)

def detect_orientation_opencv(document, page_num, pre_processing, last_preprocessing=None, debug=False):

    document_page = document.document_pages.get(
                                page_num=page_num)

    abs_pre_processing_folder_path = pre_processing_folder_path(document, pre_processing)

    is_pre_processing_dir_exist = os.path.exists(abs_pre_processing_folder_path)
    if not is_pre_processing_dir_exist:
        os.makedirs(abs_pre_processing_folder_path)

    page_num = document_page.page_num

    if document_page.preprocessed:
        return
    abs_new_pre_processed_image_path = pre_processed_image_path(document, pre_processing, page_num)
    if last_preprocessing == None:
        last_preprocessed_image_path = original_image_path(document, page_num)
    else:
        last_preprocessed_image_path = pre_processed_image_path(document, last_preprocessing, page_num)
    shutil.copy(last_preprocessed_image_path, abs_new_pre_processed_image_path)

    im = cv2.imread(abs_new_pre_processed_image_path)

    gray_im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gray_im = cv2.medianBlur(gray_im, 5)
    thresh = cv2.threshold(gray_im, thresh=0, maxval=255, type=cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # try to merge words in lines
    (h, w) = im.shape[:2]
    k_x = max(1, (math.floor(w / 100)))
    k_y = max(1, (math.floor(h / 100)))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (math.floor(k_x), math.floor(k_y / 2)))
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    angle = 0

    # extract contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours
    contours = sorted(contours, key=get_max_width_length_ratio, reverse=True)

    contours_counter = 0

    for contour in contours:
        (x,y,w,h) = cv2.boundingRect(contour)
        if w > (k_x * 4) and y > (k_y * 2):
            contours_counter = contours_counter + 1

    rotated_90 = cv2.rotate(thresh, cv2.ROTATE_90_CLOCKWISE)

    rotated_90_contours, _ = cv2.findContours(rotated_90, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    rotated_90_contours = sorted(rotated_90_contours, key=get_max_width_length_ratio, reverse=True)

    rotated_90_contours_counter = 0

    for contour in rotated_90_contours:
        (x,y,w,h) = cv2.boundingRect(contour)
        if w > (k_x * 4) and y > (k_y * 2):
            rotated_90_contours_counter = rotated_90_contours_counter + 1

    if rotated_90_contours_counter > contours_counter:
        angle = 270
        rotated_im = ndimage.rotate(im, angle)
    else:
        angle = 0
        rotated_im = im

    best_rotation_angle = angle

    gray_rotated_im = ndimage.rotate(gray_im, angle)
    ret, bw_img = cv2.threshold(gray_rotated_im, 127, 255, cv2.THRESH_BINARY)

    total_area_of_space_in_upper = 0

    # Find the first non-black pixel
    height, width = bw_img.shape
    for x in range(width):
        for y in range(height):
            if bw_img[y, x] != 255:
                total_area_of_space_in_upper = total_area_of_space_in_upper + y
                # Fill in the area above this pixel
                if pre_processing.debug:
                    cv2.rectangle(rotated_im, (x, 0), (x, y), (255, 0, 0), -1)
                break

    total_area_of_space_in_lower = 0

    for x in range(width):
        for y in reversed(range(height)):
            if bw_img[y, x] != 255:
                total_area_of_space_in_lower = total_area_of_space_in_lower + height - y
                # Fill in the area above this pixel
                if pre_processing.debug:
                    cv2.rectangle(rotated_im, (x, y), (x, height), (0, 255, 0), -1)
                break

    if total_area_of_space_in_upper > total_area_of_space_in_lower:
        angle = 180
    else:
        angle = 0

    best_rotation_angle += angle

    final = ndimage.rotate(rotated_im, best_rotation_angle)

    cv2.imwrite(abs_new_pre_processed_image_path, final)

    document_page.save()