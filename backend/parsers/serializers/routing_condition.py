from rest_framework import serializers

from ..models.routing_condition import RoutingCondition

class RoutingConditionSerializer(serializers.ModelSerializer):
    """ Serializer for routing rules. """

    class Meta:
        model = RoutingCondition
        fields = ['id', 'routing_rule_id', 'rule_id', 'operator', 'value', 'sort_order']
        read_only_fields = ['id']