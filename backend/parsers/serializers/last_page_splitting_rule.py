from typing import List

from rest_framework import serializers

from parsers.models.last_page_splitting_condition import LastPageSplittingCondition
from parsers.models.last_page_splitting_rule import LastPageSplittingRule

from parsers.serializers.last_page_splitting_condition import LastPageSplittingConditionSerializer


class LastPageSplittingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    last_page_splitting_conditions = LastPageSplittingConditionSerializer(
        many=True, required=False)

    class Meta:
        model = LastPageSplittingRule
        fields = ['id',
                  'sort_order', "last_page_splitting_rule_type", "last_page_splitting_conditions"]
        read_only_fields = ['id']

    def _get_or_create_last_page_splitting_conditions(self, last_page_splitting_conditions, splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_condition in last_page_splitting_conditions:
            splitting_condition["splitting_rule_id"] = splitting_rule.id
            splitting_condition["sort_order"] = sort_order
            LastPageSplittingCondition.objects.get_or_create(
                **splitting_condition,
            )
            sort_order += 1

    def create(self, validated_data):
        """ Create a splitting rule. """
        splitting_id = validated_data.get("splitting").id
        all_splitting_rules = LastPageSplittingRule.objects.order_by("-sort_order").filter(
            splitting_id=splitting_id).all()
        if len(all_splitting_rules) == 0:
            sort_order = 1
        else:
            lastest_all_splitting_rule = all_splitting_rules[0]
            sort_order = lastest_all_splitting_rule.sort_order + 1

        validated_data["sort_order"] = sort_order

        splitting_conditions = validated_data.pop("splitting_conditions", [])

        splitting_rule = LastPageSplittingRule.objects.create(
            **validated_data)
        self._get_or_create_last_page_splitting_conditions(
            splitting_conditions, splitting_rule)

        return splitting_rule
