import uuid

from django.db import models

from .routing_operator_type import RoutingOperatorType

class RoutingCondition(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  routing_rule = models.ForeignKey("RoutingRule", on_delete=models.CASCADE)
  rule = models.ForeignKey("Rule", on_delete=models.CASCADE)
  operator = models.CharField(max_length=255, null=False, choices=RoutingOperatorType.choices())
  value = models.CharField(max_length=255, null=True)
  sort_order = models.IntegerField(null=False)

