import cv2
import numpy as np
import math
import os
import shutil
from PIL import Image
from reportlab.pdfgen.canvas import Canvas
import pytesseract

from parsers.models.document_page import DocumentPage

from backend.settings import MEDIA_URL

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def detect_orientation_opencv(document, preprocessing, last_preprocessing=None):

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
        page_num = page_idx + 1
        document_page = DocumentPage.objects.get(
            document_id=document.id, page_num=page_num)
        if document_page.preprocessed:
            continue
        png_path = os.path.join(str(page_num) + ".jpg")
        new_preprocessed_image_path = os.path.join(working_path, png_path)
        if last_preprocessing == None:
            last_preprocessed_image_path = os.path.join(
                documents_folder_path, str(page_num) + ".jpg")
        else:
            last_preprocessed_image_path = os.path.join(
                documents_folder_path, "pre_processed-" + str(last_preprocessing.id), str(page_num) + ".jpg")
        shutil.copy(last_preprocessed_image_path, new_preprocessed_image_path)

        im = cv2.imread(new_preprocessed_image_path)

        scores = []
        im = cv2.imread(new_preprocessed_image_path)
        img_gray = cv2.imread(new_preprocessed_image_path,
                              cv2.IMREAD_GRAYSCALE)
        cropped_gray = crop_image_center(img_gray)

        (thresh, im_bw) = cv2.threshold(cropped_gray, 128,
                                        255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Let numpy do the heavy lifting for converting pixels to pure black or white
        thresh = 127
        bw = cv2.threshold(cropped_gray, thresh, 255, cv2.THRESH_BINARY)[1]

        # Pixel range is 0...255, 256/2 = 128
        bw[bw < 128] = 0    # Black
        bw[bw >= 128] = 255  # White

        img_bw = cv2.resize(bw, (0, 0), fx=0.3, fy=0.3)

        angle = 0
        while angle <= 180:
            # Rotate the source image
            img = rotate_without_crop(img_bw, angle)
            # Crop the center 1/3rd of the image (roi is filled with text)
            h, w = img.shape
            # buffer = min(h, w) - int(min(h,w)/1.15)
            # roi = img[int(h/2-buffer):int(h/2+buffer), int(w/2-buffer):int(w/2+buffer)]
            # Create background to draw transform on
            # bg = np.zeros((buffer*2, buffer*2), np.uint8)
            # Compute the sums of the rows
            row_sums = sum_rows(img)
            # High score --> Zebra stripes
            score = np.count_nonzero(row_sums)
            scores.append(score)
            # Image has best rotation
            if score <= min(scores):
                # Save the rotatied image
                # best_rotation = img.copy()
                best_rotation_angle = angle
            # k = display_data(img, row_sums, buffer)
            # if k == 27: break
            # Increment angle and try again
            angle += 90

        # Flip image and try again

        """result = rotate_without_crop(im, best_rotation_angle)
        result_flipped = rotate_without_crop(im, best_rotation_angle + 180)

        if (top_bot_margin_ratio(result) < top_bot_margin_ratio(result_flipped)):
            best_rotation_angle = best_rotation_angle
        else:
            best_rotation_angle = best_rotation_angle + 180"""

        if best_rotation_angle == 0 or best_rotation_angle == 180 or best_rotation_angle == 360:
            try:
                osd = pytesseract.image_to_osd(
                    im, output_type='dict')
            except Exception as e:
                osd = {"orientation": 0}
            best_rotation_angle = osd["orientation"]

        rotated_im = rotate_without_crop(im, best_rotation_angle)

        cv2.imwrite(new_preprocessed_image_path, rotated_im,
                    [cv2.IMWRITE_JPEG_QUALITY, 50])

        image_paths.append(new_preprocessed_image_path)

        document_page.preprocessed = True
        document_page.save()

    output_pdf_path = os.path.join(
        documents_folder_path, "pre_processed-" + str(preprocessing.id), "output.pdf")
    convert_images_to_pdf(image_paths, output_pdf_path)


def crop_image_center(image):
    center = image.shape
    h = center[0]
    w = center[1]
    if h > w:
        x = 0
        y = h/2 - w/2
        cropped_image = image[int(y):int(y+w), int(x):int(x+w)]
    else:
        x = w/2 - h/2
        y = 0
        cropped_image = image[int(y):int(y+h), int(x):int(x+h)]

    return cropped_image


def convert_images_to_pdf(images, output_file_path):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    pdf = Canvas(output_file_path, pageCompression=1)
    dpi = 300
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


def rotate_without_crop(mat, angle):
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


def rotate(img, angle):
    rows, cols = img.shape
    M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
    dst = cv2.warpAffine(img, M, (cols, rows))
    return dst


def sum_rows(img):
    # Create a list to store the row sums
    row_sums = []
    # Iterate through the rows
    for r in range(img.shape[0]-1):
        # Sum the row
        row_sum = sum(sum(img[r:r+1, :]))
        # Add the sum to the list
        row_sums.append(row_sum)
    # Normalize range to (0,255)
    row_sums = (row_sums/max(row_sums)) * 255
    # Return
    return row_sums


def display_data(roi, row_sums, buffer):
    # Create background to draw transform on
    bg = np.zeros((buffer*2, buffer*2), np.uint8)
    # Iterate through the rows and draw on the background
    for row in range(roi.shape[0]-1):
        row_sum = row_sums[row]
        bg[row:row+1, :] = row_sum
    left_side = int(buffer/3)
    bg[:, buffer:] = roi[:, buffer:]
    cv2.imshow('bg1', bg)
    k = cv2.waitKey(1)
    return k

# Save aligned image


def top_bot_margin_ratio(image: np.ndarray) -> float:
    if len(image.shape) > 2 and image.shape[2] > 1:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    above = 0
    below = 0
    for x in range(image.shape[1]):
        col = np.argwhere(image[:, x] < 128)
        if col.shape[0] > 0:
            above += col[0, 0]
            below += image.shape[0] - 1 - col[-1, 0]

    try:
        return math.log(above/below)
    except:
        return 0
