import uuid

from django.db import models

from .stream_operator_type import StreamOperatorType

class StreamCondition(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  stream = models.ForeignKey("Stream", on_delete=models.CASCADE)
  column = models.CharField(max_length=255, null=False)
  operator = models.CharField(max_length=255, null=False, choices=StreamOperatorType.choices())
  value = models.CharField(max_length=255, null=True)
  sort_order = models.IntegerField(null=False)

  class Meta:
    db_table = 'stream_conditions'