import uuid

from django.db import models


class LastPageSplittingRule(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    parent_splitting_rule = models.ForeignKey(
        "SplittingRule", on_delete=models.CASCADE, related_name="last_page_splitting_rules", null=True)
    sort_order = models.IntegerField(null=False)

    class Meta:
        db_table = 'last_page_splitting_rules'