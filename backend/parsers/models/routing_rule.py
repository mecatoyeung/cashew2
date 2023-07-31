import uuid

from django.db import models

from datetime import datetime

class RoutingRule(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  parser = models.ForeignKey("Parser", on_delete=models.CASCADE, related_name="parser")
  route_to_parser = models.ForeignKey("Parser", on_delete=models.CASCADE, related_name="route_to_parser")
  sort_order = models.IntegerField(null=False)
