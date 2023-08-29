import uuid

from django.db import models
from django.utils import timezone

from .stream_type import StreamType
from .stream_class import StreamtClass

class Stream(models.Model):
  id = models.AutoField(primary_key=True)
  guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
  rule = models.ForeignKey("Rule", related_name='streams', on_delete=models.CASCADE)
  step = models.IntegerField()
  type = models.CharField(max_length=255, choices=StreamType.choices())
  stream_class = models.CharField(max_length=255, choices=StreamtClass.choices())
  text = models.TextField(null=True, blank=True, max_length=1023, default="")
  regex = models.TextField(null=True, blank=True, max_length=1023, default="")
  join_string = models.TextField(null=True, blank=True, max_length=1023, default="")
  extract_first_n_lines = models.IntegerField(default=1)
  extract_nth_lines = models.TextField(null=True, blank=True, default="")
  combine_first_n_lines = models.IntegerField(null=True, blank=True, default=2)
  convert_to_table_by_specify_headers = models.OneToOneField("ConvertToTableBySpecifyHeaders", on_delete=models.CASCADE, null=True, blank=True)
  #get_chars_from_next_col_if_regex_not_match = models.TextField(null=True, default="{'col_index': '', 'regex': ''}")
  #remove_rows_with_conditions = models.TextField(null=True, default="[]")
  #merge_rows_with_conditions = models.TextField(null=True, default="[]")
  #merge_rows_with_same_columns = models.TextField(null=True, default="")
  #remove_rows_before_row_with_conditions = models.TextField(
  #    null=True, default="{'include_matched_row': True, 'conditions': [] }")
  #remove_rows_after_row_with_conditions = models.TextField(
  #    null=True, default="{'include_matched_row': True, 'conditions': [] }")
  #unpivot_table = models.TextField(null=True, default="{'col_index': '', 'assignment_separator': ':', 'new_line_separator': '\n' }")
  #convert_to_table_by_specify_headers = models.TextField(null=True, default="")

  class Meta:
    db_table = 'streams'