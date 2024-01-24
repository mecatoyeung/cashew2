from rest_framework import serializers

from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_condition import SplittingCondition
from parsers.models.consecutive_page_splitting_rule import ConsecutivePageSplittingRule
from parsers.models.consecutive_page_splitting_condition import ConsecutivePageSplittingCondition
from parsers.models.last_page_splitting_rule import LastPageSplittingRule
from parsers.models.last_page_splitting_condition import LastPageSplittingCondition

#from parsers.serializers.nested.consecutive_page_splitting_rule import ConsecutivePageSplittingRuleSerializer
#from parsers.serializers.nested.last_page_splitting_rule import LastPageSplittingRuleSerializer


class SplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    """splitting_rule = SplittingRuleSerializer(
        many=False, required=False, allow_null=True)"""
    splitting_rule = serializers.SerializerMethodField()
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['id', 'rule', 'splitting_rule',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']

    def get_splitting_rule(self, obj):
        from parsers.serializers.last_page_splitting_rule import LastPageSplittingRuleSerializer
        return LastPageSplittingRuleSerializer(obj.splitting_rule).data


class PostSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SplittingCondition
        fields = ['rule', 'splitting_rule',
                  'operator', 'value', 'sort_order']
