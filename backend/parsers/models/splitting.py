import uuid

from django.db import models
from parsers.models.splitting_type import SplittingType
from parsers.models.splitting_no_first_page_rules_matched_operation_type import SplittingNoFirstPageRulesMatchedOperationType


class Splitting(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=255, null=False, default=uuid.uuid4)
    parser = models.OneToOneField(
        "Parser", on_delete=models.CASCADE, related_name="splitting")
    split_type = models.CharField(max_length=255, choices=SplittingType.choices(
    ), null=True, default=SplittingType.NO_SPLIT.value)
    no_first_page_rules_matched_operation_type = models.CharField(
        max_length=255, choices=SplittingNoFirstPageRulesMatchedOperationType.choices(), null=True, default=SplittingNoFirstPageRulesMatchedOperationType.REMOVE_THE_PAGE.value)
    no_first_page_rules_matched_route_to_parser = models.OneToOneField(
        "Parser", on_delete=models.CASCADE, related_name="no_first_page_rules_matched_route_to_parser", null=True)
    activated = models.BooleanField(null=False, default=False)

    class Meta:
        db_table = 'splittings'
