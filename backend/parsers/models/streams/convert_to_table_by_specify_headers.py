import uuid
import json

from django.db import models
from django.utils import timezone

class ConvertToTableBySpecifyHeaders(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)

  class Meta:
    db_table = 'convert_to_table_by_specify_headers'