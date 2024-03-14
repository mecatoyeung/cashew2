import uuid

from django.utils import timezone
from django.db import models

from parsers.models.parser import Parser
from parsers.models.integration_type import IntegrationType
from parsers.models.pdf_integration_type import PDFIntegrationType


class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    integration_type = models.CharField(
        max_length=255, choices=IntegrationType.choices())
    name = models.CharField(max_length=255, null=False)
    parser = models.ForeignKey(
        Parser, on_delete=models.CASCADE, null=False, related_name='integrations')
    xml_path = models.CharField(max_length=1023, null=True)
    template = models.TextField(null=True)
    pdf_integration_type = models.CharField(
        max_length=255, choices=PDFIntegrationType.choices(), null=True)
    pre_processing = models.OneToOneField(
        "PreProcessing", on_delete=models.CASCADE, related_name="pre_processing", null=True)
    post_processing = models.OneToOneField(
        "PostProcessing", on_delete=models.CASCADE, related_name="post_processing", null=True)
    pdf_path = models.CharField(max_length=1023, null=True)
    interval_seconds = models.IntegerField()
    next_run_time = models.DateTimeField(null=False, default=timezone.now)
    activated = models.BooleanField(null=True, default=True)

    class Meta:
        db_table = 'integrations'
