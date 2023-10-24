from django.db import models
from .post_processing_type import PostProcessingType


class PostProcessing(models.Model):
    id = models.AutoField(primary_key=True)
    post_processing_type = models.CharField(
        max_length=255, choices=PostProcessingType.choices())
    name = models.CharField(max_length=255, null=False)
    step = models.IntegerField(null=True, blank=True)
    parser = models.ForeignKey(
        "Parser", on_delete=models.CASCADE, null=False, related_name='postprocessings')
    redaction_regex = models.CharField(max_length=1023, null=True)

    class Meta:
        db_table = 'post_processings'
