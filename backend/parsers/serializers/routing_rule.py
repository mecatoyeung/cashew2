from rest_framework import serializers

from ..models.routing_rule import RoutingRule
from .routing_condition import RoutingConditionSerializer

class RoutingRuleSerializer(serializers.ModelSerializer):
    """ Serializer for routing rules. """
    routing_conditions = RoutingConditionSerializer(many=True, read_only=True)

    class Meta:
        model = RoutingRule
        fields = ['id', 'parser_id', 'route_to_parser_id', 'sort_order', "routing_conditions"]
        read_only_fields = ['id']


