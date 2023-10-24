from rest_framework import serializers

from ..models.splitting_condition import SplittingCondition

class SplittingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """

    class Meta:
        model = SplittingCondition
        fields = ['id', 'splitting_rule_id', 'rule_id', 'operator', 'value', 'sort_order']
        read_only_fields = ['id']