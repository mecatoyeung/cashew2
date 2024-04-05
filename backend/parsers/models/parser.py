from django.db import models

from datetime import datetime
from django.utils import timezone
import uuid

from enum import Enum

from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model

from parsers.models.parser_type import ParserType


class Parser(models.Model):

    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    type = models.CharField(
        max_length=255, choices=ParserType.choices(), default=ParserType.LAYOUT.value)
    name = models.CharField(max_length=255, null=False)
    total_num_of_pages_processed = models.IntegerField(default=0)
    pdf_to_image_dpi = models.DecimalField(null=True, default=300, decimal_places=0, max_digits=10)
    assumed_text_width = models.DecimalField(null=True, default=0.3, decimal_places=2, max_digits=10)
    assumed_text_height = models.DecimalField(null=True, default=0.6, decimal_places=2, max_digits=10)
    same_line_acceptance_range = models.DecimalField(null=True, default=0.35, decimal_places=2, max_digits=10)
    same_column_acceptance_range = models.DecimalField(null=True, default=0.25, decimal_places=2, max_digits=10)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="parser")
    permitted_users = models.ManyToManyField(get_user_model(), related_name="permitted_parsers")
    permitted_groups = models.ManyToManyField(Group, related_name="permitted_parsers")

    last_modified_at = models.DateTimeField(null=False, default=timezone.now)

    class Meta:
        db_table = 'parsers'
