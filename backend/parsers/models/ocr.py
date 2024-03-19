import uuid

from django.db import models

from parsers.models.ocr_type import OCRType
from parsers.models.ocr_text_layer_type import OCRTextLayerType
from parsers.models.ocr_image_layer_type import OCRImageLayerType


class OCR(models.Model):
    id = models.AutoField(primary_key=True)
    parser = models.OneToOneField(
        "Parser", on_delete=models.CASCADE, related_name="ocr")
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    ocr_type = models.CharField(max_length=255, choices=OCRType.choices(
    ), null=True, default=OCRType.NO_OCR.value)
    ocr_image_layer_type = models.CharField(max_length=255, choices=OCRImageLayerType.choices(
    ), null=True, default=OCRImageLayerType.SOURCE.value)
    image_layer_preprocessing = models.OneToOneField(
        "PreProcessing", on_delete=models.CASCADE, null=True, related_name="image_layer_preprocessing")
    google_vision_ocr_api_key = models.CharField(
        max_length=1024, null=True, blank=True)
    paddle_ocr_language = models.CharField(
        max_length=256, null=True, blank=True, default="cn")
    omnipage_ocr_language = models.CharField(
        max_length=256, null=True, blank=True, default="LANG_ENG")
    detect_searchable = models.BooleanField(
        default=False
    )
    debug = models.BooleanField(default=False)

    class Meta:
        db_table = 'ocrs'
