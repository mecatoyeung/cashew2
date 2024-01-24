from typing import List

from rest_framework import serializers

from parsers.models.last_page_splitting_rule import LastPageSplittingRule
from parsers.models.last_page_splitting_condition import LastPageSplittingCondition


class LastPageSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = LastPageSplittingCondition
        fields = ['id',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']


class LastPageSplittingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    last_page_splitting_conditions = LastPageSplittingConditionSerializer(
        many=True, required=False)

    class Meta:
        model = LastPageSplittingRule
        fields = ['id',
                  'sort_order', 'last_page_splitting_conditions']
        read_only_fields = ['id']
