import uuid

from django.db import models
from .splitting_type import SplittingType

class Splitting(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  parser = models.OneToOneField("Parser", on_delete=models.CASCADE)
  split_type = models.CharField(max_length=255, choices=SplittingType.choices(), null=True, default=SplittingType.NO_SPLIT.value)

  class Meta:
    db_table = 'splittings'