import uuid

from django.db import models
from .ocr_type import OCRType

class OCR(models.Model):
  id = models.AutoField(primary_key=True)
  parser = models.OneToOneField("Parser", on_delete=models.CASCADE)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  ocr_type = models.CharField(max_length=255, choices=OCRType.choices(), null=True)
  google_vision_ocr_api_key = models.CharField(max_length=1024, null=True)
  activated = models.BooleanField(default=True)

  class Meta:
    db_table = 'ocrs'