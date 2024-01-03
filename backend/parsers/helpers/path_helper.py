import os
from backend.settings import MEDIA_ROOT


def xml_path(document, page_num):
    media_folder_path = MEDIA_ROOT
    documents_folder_path = os.path.join(
        media_folder_path, "documents", document.guid)
    working_path = os.path.join(documents_folder_path, "working_dir")
    xml_path = os.path.join(working_path, str(page_num) + ".xml")
    return xml_path
