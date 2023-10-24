import os

from backend import settings

def upload_document(document, file):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'documents', document.guid)
    is_folder_exist = os.path.exists(folder_path)
    if not is_folder_exist:
        os.makedirs(folder_path)
    abs_file_path = os.path.join(folder_path, "source_file.pdf")
    with open(abs_file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)