import uuid

from django.db import models
from django.utils import timezone

from .rule_type import RuleType

class TableColumnSeparator(models.Model):
  id = models.AutoField(primary_key=True)
  rule = models.ForeignKey("Rule", on_delete=models.CASCADE, related_name="table_column_separators")
  x = models.DecimalField(max_digits=10, decimal_places=2)