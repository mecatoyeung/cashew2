import uuid

from django.db import models
from django.utils import timezone

from .rule_type import RuleType
from .parser import Parser

class Rule(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  parser = models.ForeignKey(Parser, on_delete=models.CASCADE, related_name="rules")
  name = models.CharField(max_length=255, null=False)
  rule_type = models.CharField(max_length=255, choices=RuleType.choices())
  pages = models.CharField(max_length=255, null=False)
  x1 = models.DecimalField(max_digits=10, decimal_places=2)
  y1 = models.DecimalField(max_digits=10, decimal_places=2)
  x2 = models.DecimalField(max_digits=10, decimal_places=2)
  y2 = models.DecimalField(max_digits=10, decimal_places=2)
  anchor_text = models.CharField(max_length=255, null=True)
  anchor_x1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  anchor_y1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  anchor_x2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  anchor_y2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  last_modified_at = models.DateTimeField(default=timezone.now)

  class Meta:
    db_table = 'rules'