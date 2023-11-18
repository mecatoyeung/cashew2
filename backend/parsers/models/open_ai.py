import uuid

from django.db import models


class OpenAI(models.Model):
    id = models.AutoField(primary_key=True)
    parser = models.OneToOneField(
        "Parser", on_delete=models.CASCADE, related_name="open_ai")
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    enabled = models.BooleanField(null=False, default=False)
    open_ai_resource_name = models.CharField(
        max_length=1024, null=True, blank=True)
    open_ai_api_key = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        db_table = 'open_ais'
