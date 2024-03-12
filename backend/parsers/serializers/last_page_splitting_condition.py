from rest_framework import serializers

from parsers.models.last_page_splitting_condition import LastPageSplittingCondition

        
class LastPageSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    last_page_splitting_rule = serializers.SerializerMethodField()
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = LastPageSplittingCondition
        fields = ['id', 'rule', 'last_page_splitting_rule',
                  'operator', 'value', 'sort_order']
        read_only_fields = ['id']

    def get_last_page_splitting_rule(self, obj):
        from parsers.serializers.nested.last_page_splitting_rule import LastPageSplittingRuleSerializer
        return LastPageSplittingRuleSerializer(obj.last_page_splitting_rule).data


class LastPagePostSplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    last_page_splitting_rule = serializers.SerializerMethodField()
    sort_order = serializers.IntegerField(required=False)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = LastPageSplittingCondition
        fields = ['rule', 'last_page_splitting_rule',
                  'operator', 'value', 'sort_order']
        
    def get_last_page_splitting_rule(self, obj):
        from parsers.serializers.nested.last_page_splitting_rule import LastPageSplittingRuleSerializer
        return LastPageSplittingRuleSerializer(obj.last_page_splitting_rule).data