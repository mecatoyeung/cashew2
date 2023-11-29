from rest_framework import serializers

from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_condition import SplittingCondition

from parsers.serializers.nested.splitting_rule import SplittingRuleSerializer


class SplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    splitting_rule = SplittingRuleSerializer(
        many=False, required=False, allow_null=True)
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['id', 'rule', 'splitting_rule',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']


class PostSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['rule', 'splitting_rule',
                  'operator', 'value', 'sort_order']
