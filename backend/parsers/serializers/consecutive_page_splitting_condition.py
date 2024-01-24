from rest_framework import serializers

from parsers.models.consecutive_page_splitting_condition import ConsecutivePageSplittingCondition



class ConsecutivePageSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    consecutive_page_splitting_rule = serializers.SerializerMethodField()
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ConsecutivePageSplittingCondition
        fields = ['id', 'rule', 'consecutive_page_splitting_rule',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']

    def get_consecutive_page_splitting_rule(self, obj):
        from parsers.serializers.nested.consecutive_page_splitting_rule import ConsecutivePageSplittingRuleSerializer
        return ConsecutivePageSplittingRuleSerializer(obj.consecutive_page_splitting_rule).data


class ConsecutivePagePostSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    consecutive_page_splitting_rule = serializers.SerializerMethodField()
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ConsecutivePageSplittingCondition
        fields = ['rule', 'consecutive_page_splitting_rule',
                  'operator', 'value', 'sort_order']
                  
    def get_consecutive_page_splitting_rule(self, obj):
        from parsers.serializers.nested.consecutive_page_splitting_rule import ConsecutivePageSplittingRuleSerializer
        return ConsecutivePageSplittingRuleSerializer(obj.consecutive_page_splitting_rule).data
