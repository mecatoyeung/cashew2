import uuid

from django.db import models

from parsers.models.consecutive_page_splitting_rule_type import ConsecutivePageSplittingRuleType


class ConsecutivePageSplittingRule(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    consecutive_page_splitting_rule_type = models.CharField(
        max_length=255, choices=ConsecutivePageSplittingRuleType.choices(), null=True, default=ConsecutivePageSplittingRuleType.BY_CONDITIONS.value)
    parent_splitting_rule = models.ForeignKey(
        "SplittingRule", on_delete=models.CASCADE, related_name="consecutive_page_splitting_rules", null=True)
    sort_order = models.IntegerField(null=False)

    class Meta:
        db_table = 'consecutive_page_splitting_rules'
