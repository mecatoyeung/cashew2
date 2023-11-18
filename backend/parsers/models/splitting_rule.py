import uuid

from django.db import models

from datetime import datetime

from parsers.models.splitting_rule_type import SplittingRuleType
from parsers.models.parser import Parser
from parsers.models.splitting import Splitting


class SplittingRule(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    splitting_rule_type = models.CharField(
        max_length=255, choices=SplittingRuleType.choices())
    parent_splitting_rule = models.ForeignKey(
        "SplittingRule", on_delete=models.CASCADE, related_name="consecutive_page_splitting_rules", null=True)
    splitting = models.ForeignKey(
        "Splitting", on_delete=models.CASCADE, related_name="splitting_rules")
    route_to_parser = models.ForeignKey(
        "Parser", on_delete=models.CASCADE, null=True)
    sort_order = models.IntegerField(null=False)

    class Meta:
        db_table = 'splitting_rules'
