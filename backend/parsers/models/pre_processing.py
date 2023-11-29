import uuid

from django.db import models
from parsers.models.pre_processing_type import PreProcessingType


class PreProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    pre_processing_type = models.CharField(
        max_length=255, choices=PreProcessingType.choices())
    name = models.CharField(max_length=255, null=False)
    step = models.IntegerField(null=True, blank=True)
    parser = models.ForeignKey(
        "Parser", on_delete=models.CASCADE, null=False, related_name='preprocessings')

    class Meta:
        db_table = 'pre_processings'
