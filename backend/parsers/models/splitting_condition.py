import uuid

from django.db import models

from parsers.models.splitting_operator_type import SplittingOperatorType


class SplittingCondition(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    splitting_rule = models.ForeignKey(
        "SplittingRule", on_delete=models.CASCADE, related_name="splitting_conditions", null=True)
    consecutive_page_splitting_rule = models.ForeignKey(
        "ConsecutivePageSplittingRule", on_delete=models.CASCADE, related_name="splitting_conditions", null=True)
    last_page_splitting_rule = models.ForeignKey(
        "LastPageSplittingRule", on_delete=models.CASCADE, related_name="splitting_conditions", null=True)
    rule = models.ForeignKey("Rule", on_delete=models.CASCADE)
    operator = models.CharField(
        max_length=255, null=False, choices=SplittingOperatorType.choices())
    value = models.CharField(max_length=255, null=True)
    sort_order = models.IntegerField(null=False)

    class Meta:
        db_table = 'splitting_conditions'
