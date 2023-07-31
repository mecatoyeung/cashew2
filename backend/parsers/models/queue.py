import uuid

from django.db import models

from .queue_class import QueueClass
from .document import Document

class Queue(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  document = models.OneToOneField("Document", related_name="document", null=True, on_delete=models.CASCADE)
  parser = models.ForeignKey("Parser", null=True, default=None, on_delete=models.SET_NULL)
  queue_class = models.CharField(max_length=255, choices=QueueClass.choices())
  input_result = models.TextField(null=True, default="{}")
  parsed_result = models.TextField(null=True, default="{}")

