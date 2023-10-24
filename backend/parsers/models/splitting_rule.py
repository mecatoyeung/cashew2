import uuid

from django.db import models

from datetime import datetime

from .parser import Parser
from .splitting import Splitting

class SplittingRule(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  splitting = models.ForeignKey(Splitting, on_delete=models.CASCADE, related_name="splitting_rules")
  route_to_parser = models.ForeignKey(Parser, on_delete=models.CASCADE)
  sort_order = models.IntegerField(null=False)

  class Meta:
    db_table = 'splitting_rules'