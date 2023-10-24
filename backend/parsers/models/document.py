import os
from enum import Enum
from django.utils import timezone
import uuid

from django.conf import settings
from django.db import models

from backend.settings import MEDIA_URL
from .document_type import DocumentType
from .parser import Parser


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    parser = models.ForeignKey(Parser, on_delete=models.CASCADE)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)

    def file_upload_to(instance, filename):
        return os.path.join(MEDIA_URL, 'documents/%s/%s.%s' % (instance.guid, 'original', instance.extension))
    file = models.FileField(null=True, upload_to=file_upload_to)
    document_type = models.CharField(
        max_length=255, choices=DocumentType.choices())
    filename_without_extension = models.CharField(max_length=255, null=False)
    extension = models.CharField(max_length=255, null=False)
    total_page_num = models.IntegerField()
    last_modified_at = models.DateTimeField(null=False, default=timezone.now)

    class Meta:
        db_table = 'documents'
