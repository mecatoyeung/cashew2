from django.db import models

from .parser import Parser
from .integration_type import IntegrationType

class Integration(models.Model):
  id = models.AutoField(primary_key=True)
  integration_type = models.CharField(max_length=255, choices=IntegrationType.choices())
  name = models.CharField(max_length=255, null=False)
  parser = models.ForeignKey(Parser, on_delete=models.CASCADE, null=False, related_name='integrations')
  xml_path = models.CharField(max_length=1023, null=True)
  template = models.TextField(null=True)
  pdf_version = models.CharField(max_length=255, null=True)
  pdf_path = models.CharField(max_length=1023, null=True)

  class Meta:
    db_table = 'Integrations'