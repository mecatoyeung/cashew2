from rest_framework import serializers

from parsers.models.open_ai import OpenAI


class OpenAISerializer(serializers.ModelSerializer):

    open_ai_resource_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_api_key = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_deployment = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = OpenAI
        fields = ['id', 'guid', 'parser_id', 'enabled',
                  'open_ai_resource_name', 'open_ai_api_key', 'open_ai_deployment']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a Open AI. """
        open_ai = OpenAI.objects.create(**validated_data)

        return open_ai

    def update(self, instance, validated_data):
        """ Update AI Chat. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
