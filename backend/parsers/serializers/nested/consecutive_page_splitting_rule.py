from typing import List

from rest_framework import serializers

from parsers.models.consecutive_page_splitting_rule import ConsecutivePageSplittingRule
from parsers.models.consecutive_page_splitting_condition import ConsecutivePageSplittingCondition


class ConsecutivePageSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ConsecutivePageSplittingCondition
        fields = ['id',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']


class ConsecutivePageSplittingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    consecutive_page_splitting_conditions = ConsecutivePageSplittingConditionSerializer(
        many=True, required=False)

    class Meta:
        model = ConsecutivePageSplittingRule
        fields = ['id',
                  'sort_order', 'consecutive_page_splitting_conditions']
        read_only_fields = ['id']