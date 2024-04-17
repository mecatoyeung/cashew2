from typing import List

from rest_framework import serializers

from parsers.models.consecutive_page_splitting_condition import ConsecutivePageSplittingCondition
from parsers.models.consecutive_page_splitting_rule import ConsecutivePageSplittingRule

from parsers.serializers.consecutive_page_splitting_condition import ConsecutivePageSplittingConditionSerializer


class ConsecutivePageSplittingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    consecutive_page_splitting_conditions = ConsecutivePageSplittingConditionSerializer(
        many=True, required=False)

    class Meta:
        model = ConsecutivePageSplittingRule
        fields = ['id',
                  'sort_order', "consecutive_page_splitting_rule_type", "consecutive_page_splitting_conditions"]
        read_only_fields = ['id']

    def _get_or_create_consecutive_page_splitting_conditions(self, consecutive_page_splitting_conditions, splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_condition in consecutive_page_splitting_conditions:
            splitting_condition["splitting_rule_id"] = splitting_rule.id
            splitting_condition["sort_order"] = sort_order
            ConsecutivePageSplittingCondition.objects.get_or_create(
                **splitting_condition,
            )
            sort_order += 1

    def create(self, validated_data):
        """ Create a splitting rule. """
        splitting_id = validated_data.get("splitting").id
        all_splitting_rules = ConsecutivePageSplittingRule.objects.order_by("-sort_order").filter(
            splitting_id=splitting_id).all()
        if len(all_splitting_rules) == 0:
            sort_order = 1
        else:
            lastest_all_splitting_rule = all_splitting_rules[0]
            sort_order = lastest_all_splitting_rule.sort_order + 1

        validated_data["sort_order"] = sort_order

        splitting_conditions = validated_data.pop("splitting_conditions", [])

        splitting_rule = ConsecutivePageSplittingRule.objects.create(
            **validated_data)
        self._get_or_create_consecutive_page_splitting_conditions(
            splitting_conditions, splitting_rule)

        return splitting_rule

