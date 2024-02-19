import uuid

from django.db import models


class OpenAIMetricsKey(models.Model):
    id = models.AutoField(primary_key=True)
    parser = models.OneToOneField(
        "Parser", on_delete=models.CASCADE, related_name="open_ai_metrics_key")

    open_ai_metrics_tenant_id = models.CharField(max_length=1024, null=True, default="")
    open_ai_metrics_client_id  = models.CharField(max_length=1024, null=True, default="")
    open_ai_metrics_client_secret = models.CharField(max_length=1024, null=True, default="")
    open_ai_metrics_subscription_id = models.CharField(max_length=1024, null=True, default="")
    open_ai_metrics_service_name = models.CharField(max_length=1024, null=True, default="")

    class Meta:
        db_table = 'open_ai_metrics_key'
