from rest_framework import serializers

from ..models.splitting_rule import SplittingRule
from .splitting_condition import SplittingConditionSerializer

class SplittingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for splitting rules. """
    splitting_conditions = SplittingConditionSerializer(many=True, read_only=True)

    class Meta:
        model = SplittingRule
        fields = ['id', 'splitting_id', 'route_to_parser_id', 'sort_order', "splitting_conditions"]
        read_only_fields = ['id']


