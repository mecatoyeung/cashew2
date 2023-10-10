import uuid

from django.db import models
from django.utils import timezone

from .stream_type import StreamType
from .stream_class import StreamtClass

class Stream(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=256, null=False, default=uuid.uuid4)
  rule = models.ForeignKey("Rule", related_name='streams', on_delete=models.CASCADE)
  step = models.IntegerField()
  type = models.CharField(max_length=256, choices=StreamType.choices())
  stream_class = models.CharField(max_length=256, choices=StreamtClass.choices())
  text = models.TextField(null=True, blank=True, max_length=1024, default="")
  regex = models.TextField(null=True, blank=True, max_length=1024, default="")
  join_string = models.TextField(null=True, blank=True, max_length=1024, default="")
  extract_first_n_lines = models.IntegerField(default=1)
  extract_nth_lines = models.TextField(null=True, blank=True, default="")
  combine_first_n_lines = models.IntegerField(null=True, blank=True, default=2)
  convert_to_table_by_specify_headers = models.TextField(null=True, blank=True, max_length=4096, default="")
  col_index = models.IntegerField(null=True, blank=True, default=1)
  col_indexes = models.TextField(null=True, blank=True, max_length=1024, default="")
  remove_matched_row_also = models.BooleanField(null=True, blank=True, default=False)
  unpivot_column_index = models.TextField(null=True, blank=True, max_length=1024, default="")
  unpivot_newline_char = models.TextField(null=True, blank=True, max_length=1024, default="")
  unpivot_property_assign_char = models.TextField(null=True, blank=True, max_length=1024, default="")

  class Meta:
    db_table = 'streams'