from rest_framework import serializers

from ..models.parser import Parser

from .routing_rule import RoutingRuleSerializer

class ParserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'type', 'name', 'rules', 'last_modified_at']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a parser. """
        parser = Parser.objects.create(**validated_data)

        return parser

    def update(self, instance, validated_data):
        """ Update parser. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ParserDetailSerializer(ParserSerializer):
    """ Serializer for parser detail view. """
    routing_rules = RoutingRuleSerializer(many=True, read_only=True)

    class Meta(ParserSerializer.Meta):
        fields = ParserSerializer.Meta.fields + ["routing_rules"]

