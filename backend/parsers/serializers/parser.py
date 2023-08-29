from rest_framework import serializers

from ..models.parser import Parser
from .rule import RuleSerializer

class ParserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'type', 'name', 'rules', 'last_modified_at']
        read_only_fields = ['id']

    rules = RuleSerializer(many=True, required=False, allow_null=True)

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
