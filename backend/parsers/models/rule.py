import uuid

from django.db import models
from django.utils import timezone

from parsers.models.rule_type import RuleType
from parsers.models.parser import Parser


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    parser = models.ForeignKey(
        Parser, on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=255, null=False)
    rule_type = models.CharField(max_length=255, choices=RuleType.choices())
    pages = models.CharField(max_length=255, null=False)
    x1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    y1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    x2 = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    y2 = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    anchor_text = models.CharField(max_length=255, null=True, default="")
    anchor_x1 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    anchor_y1 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    anchor_x2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=100)
    anchor_y2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=100)
    anchor_relative_x1 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    anchor_relative_y1 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    anchor_relative_x2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=100)
    anchor_relative_y2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=100)
    anchor_document = models.ForeignKey(
        "Document", null=True, related_name='rule', on_delete=models.CASCADE)
    anchor_page_num = models.IntegerField(null=True)
    acrobat_form_field = models.CharField(max_length=255, null=True, default="")
    last_modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'rules'
