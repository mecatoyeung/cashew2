import uuid

from django.db import models

from parsers.models.post_processing_type import PostProcessingType


class PostProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    name = models.CharField(max_length=255, null=False)
    parser = models.ForeignKey(
        "Parser", on_delete=models.CASCADE, null=False, related_name='postprocessings')
    step = models.IntegerField(null=True, blank=True)
    post_processing_type = models.CharField(
        max_length=255, choices=PostProcessingType.choices())
    redaction_regex = models.CharField(max_length=1023, null=True)

    class Meta:
        db_table = 'post_processings'
