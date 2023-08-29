import uuid

from django.db import models

class Header(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=256, null=False, default=uuid.uuid4)
  convert_to_table_by_specify_headers = models.ForeignKey("ConvertToTableBySpecifyHeaders", related_name='headers', on_delete=models.CASCADE, null=True, blank=True)
  header = models.CharField(null=True, blank=True, max_length=1024, default="")

  class Meta:
    db_table = 'headers'