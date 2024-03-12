import os
import cv2
import numpy as np
import math
from statistics import median_low
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union
import statistics

import imutils

from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue
from parsers.models.queue_class import QueueClass
from parsers.models.queue_status import QueueStatus

from parsers.helpers.path_helpers import original_image_path, pre_processing_folder_path, pre_processed_image_path, pre_processed_rotated_image_path


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(
        image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


doctr_model = None


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(
        image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def detect_orientation_doctr(document, page_num, pre_processing, last_preprocessing=None, debug=False):

    document_page = document.document_pages.get(
        page_num=page_num)

    abs_pre_processing_folder_path = pre_processing_folder_path(
        document, pre_processing)

    is_pre_processing_dir_exist = os.path.exists(
        abs_pre_processing_folder_path)
    if not is_pre_processing_dir_exist:
        os.makedirs(abs_pre_processing_folder_path)

    page_num = document_page.page_num

    abs_pre_processed_rotated_image_path = pre_processed_rotated_image_path(
        document, pre_processing, page_num)

    if document_page.preprocessed:
        return
    abs_new_pre_processed_image_path = pre_processed_image_path(
        document, pre_processing, page_num)
    if last_preprocessing == None:
        last_preprocessed_image_path = original_image_path(document, page_num)
    else:
        last_preprocessed_image_path = pre_processed_image_path(
            document, last_preprocessing, page_num)
    shutil.copy(last_preprocessed_image_path, abs_new_pre_processed_image_path)

    from doctr.models import ocr_predictor
    from doctr.io import DocumentFile
    global doctr_model
    if doctr_model == None:
        doctr_model = ocr_predictor(
            det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True, detect_orientation=True)

    scores = []
    im = cv2.imread(abs_new_pre_processed_image_path)
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    (threshi, img_bw) = cv2.threshold(
        im_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    (h, w, c) = im.shape
    four_cropped_areas = [[0, int(h/2), 0, int(w/2)],
                          [0, int(h/2), int(w/2), int(w)],
                          [int(h/2), int(h), 0, int(w/2)],
                          [int(h/2), int(h), int(w/2), int(w)]
                          ]
    highest_black_pixel_index = 0
    highest_black_pixel_count = 0
    index = 0
    for cropped_area in four_cropped_areas:
        cropped_image = img_bw[cropped_area[0]                               :cropped_area[1], cropped_area[2]:cropped_area[3]]

        ret, thresh = cv2.threshold(cropped_image, 0, 255, cv2.THRESH_BINARY)

        (thresh_h, thresh_w) = thresh.shape
        black_pixel_count = thresh_h * thresh_w - cv2.countNonZero(thresh)

        if black_pixel_count > highest_black_pixel_count:
            highest_black_pixel_count = black_pixel_count
            highest_black_pixel_index = index

        index += 1

    cropped_area = four_cropped_areas[highest_black_pixel_index]
    cropped_image = img_bw[cropped_area[0]                           :cropped_area[1], cropped_area[2]:cropped_area[3]]
    cropped_image_rotated_90 = imutils.rotate_bound(cropped_image, 90)

    # Judge whether it is rotated 90
    row_means_of_cropped_image = np.mean(cropped_image, axis=1)

    sd_cropped_image = statistics.pstdev(row_means_of_cropped_image)

    row_means_of_cropped_image_rotated_90 = np.mean(
        cropped_image_rotated_90, axis=1)

    sd_cropped_image_rotated_90 = statistics.pstdev(
        row_means_of_cropped_image_rotated_90)

    if sd_cropped_image_rotated_90 > sd_cropped_image:
        angle = 90
        cropped_image = imutils.rotate_bound(cropped_image, 90)
    else:
        angle = 0

    cv2.imwrite(abs_pre_processed_rotated_image_path, cropped_image)

    doc = DocumentFile.from_images(abs_pre_processed_rotated_image_path)

    result = doctr_model(doc)

    highest_total_confidence_index = 0
    highest_total_confidence = 0

    total_confidence = 0
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    total_confidence += word.confidence

    if total_confidence > highest_total_confidence:
        highest_total_confidence = total_confidence
        highest_total_confidence_index = 0

    cropped_image = rotate_image(cropped_image, 180)
    cv2.imwrite(abs_pre_processed_rotated_image_path, cropped_image)

    doc = DocumentFile.from_images(abs_pre_processed_rotated_image_path)

    result = doctr_model(doc)

    total_confidence = 0
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    total_confidence += word.confidence

    if total_confidence > highest_total_confidence:
        highest_total_confidence = total_confidence
        highest_total_confidence_index = 1

    if highest_total_confidence_index == 0:
        angle += 0
    elif highest_total_confidence_index == 1:
        angle += 180

    im_corrected = imutils.rotate_bound(im, angle)
    cv2.imwrite(abs_new_pre_processed_image_path, im_corrected)

    try:
        os.remove(abs_pre_processed_rotated_image_path)
    except:
        pass

    document_page.save()
