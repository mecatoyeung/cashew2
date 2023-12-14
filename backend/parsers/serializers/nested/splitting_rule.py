from typing import List

from rest_framework import serializers

from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_condition import SplittingCondition


class SplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['id', 'splitting_rule',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']


class SplittingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    splitting_conditions = SplittingConditionSerializer(
        many=True, required=False)

    class Meta:
        model = SplittingRule
        fields = ['id', 'splitting', 'route_to_parser', 'splitting_rule_type', 'parent_splitting_rule',
                  'sort_order', 'splitting_conditions']
        read_only_fields = ['id']

    def _get_or_create_splitting_conditions(self, splitting_conditions, splitting_rule):
        """ Handle getting or creating ocr as needed. """
        sort_order = 1
        for splitting_condition in splitting_conditions:
            splitting_condition["splitting_rule_id"] = splitting_rule.id
            splitting_condition["sort_order"] = sort_order
            SplittingCondition.objects.get_or_create(
                **splitting_condition,
            )
            sort_order += 1

    def create(self, validated_data):
        """ Create a splitting rule. """
        splitting_id = validated_data.get("splitting").id
        all_splitting_rules = SplittingRule.objects.order_by("-sort_order").filter(
            splitting_id=splitting_id).all()
        if len(all_splitting_rules) == 0:
            sort_order = 1
        else:
            lastest_all_splitting_rule = all_splitting_rules[0]
            sort_order = lastest_all_splitting_rule.sort_order + 1

        validated_data["sort_order"] = sort_order

        splitting_conditions = validated_data.pop("splitting_conditions", [])

        splitting_rule = SplittingRule.objects.create(
            **validated_data)
        self._get_or_create_splitting_conditions(
            splitting_conditions, splitting_rule)

        return splitting_rule
