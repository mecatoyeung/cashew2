from django.db import models

from datetime import datetime
from django.utils import timezone
import uuid

from enum import Enum

from django.contrib.auth.models import User
from .parser_type import ParserType

class Parser(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  type = models.CharField(max_length=255, choices=ParserType.choices())
  name = models.CharField(max_length=255, null=False)
  last_modified_at = models.DateTimeField(null=False, default=timezone.now)

  class Meta:
    db_table = 'parsers'