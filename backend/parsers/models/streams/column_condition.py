import uuid

from django.db import models

class ColumnCondition(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  merge_rows_with_conditions = models.ForeignKey("MergeRowsWithConditions", on_delete=models.CASCADE, related_name="column_conditions", null=True)

  class Meta:
    db_table = 'column_conditions'