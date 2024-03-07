import os
from backend.settings import MEDIA_ROOT

def source_file_pdf_path(document):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    pdf_path = os.path.join(document_path, "source_file.pdf")

    return pdf_path

def pre_processing_folder_path(document, pre_processing):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    folder_path = os.path.join(
            document_path, "pre_processed-" + str(pre_processing.id))

    return folder_path

def ocr_folder_path(document):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    folder_path = os.path.join(document_path, "ocr")

    return folder_path

def ocred_pdf_path(document):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    pdf_path = os.path.join(document_path, "ocred.pdf")

    return pdf_path

def original_image_path(document, page_num=1):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    image_path = os.path.join(document_path, str(page_num) + ".jpg")

    return image_path

def pre_processed_image_path(document, pre_processing, page_num=1):

    abs_preprocessed_folder_path = os.path.join(
        MEDIA_ROOT, "documents", str(document.guid),
            "pre_processed-" + str(pre_processing.id))
    image_path = os.path.join(abs_preprocessed_folder_path, str(page_num) + ".jpg")

    return image_path

def pre_processed_pdf_path(document, pre_processing):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    preprocessed_folder_path = os.path.join(
            document_path, "pre_processed-" + str(pre_processing.id))
    image_path = os.path.join(preprocessed_folder_path, "output.pdf")

    return image_path

def pre_processed_rotated_image_path(document, pre_processing, page_num=1):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    preprocessed_folder_path = os.path.join(
            document_path, "pre_processed-" + str(pre_processing.id))
    image_path = os.path.join(preprocessed_folder_path, str(page_num) + "-rotated.jpg")

    return image_path

def ocred_image_path(document, page_num=1):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    ocred_folder_path = os.path.join(
            document_path, "ocr")
    image_path = os.path.join(ocred_folder_path, str(page_num) + ".jpg")

    return image_path

def gcv_path(document, page_num=1):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    preprocessed_folder_path = os.path.join(
            document_path, "ocr")
    gcv_path = os.path.join(preprocessed_folder_path, str(page_num) + ".gcv")

    return gcv_path

def hocr_path(document, page_num=1):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    preprocessed_folder_path = os.path.join(
            document_path, "ocr")
    hocr_path = os.path.join(preprocessed_folder_path, str(page_num) + ".hocr")

    return hocr_path

def xml_path(document, page_num=1):

    document_path = os.path.join(
            MEDIA_ROOT, "documents", str(document.guid))
    ocr_folder_path = os.path.join(
            document_path, "ocr")
    xml_path = os.path.join(ocr_folder_path, str(page_num) + ".xml")

    return xml_path