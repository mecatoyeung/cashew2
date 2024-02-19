from rest_framework import serializers

from parsers.models.open_ai_metrics import OpenAIMetrics


class OpenAIMetricsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpenAIMetrics
        fields = ['id', 'date', 'processed_tokens',
                  'generated_tokens', 'price']
        read_only_fields = ['id', 'parser']

    def create(self, validated_data):
        """ Create a Open AI. """
        open_ai_metrics = OpenAIMetrics.objects.create(**validated_data)

        return open_ai_metrics

    def update(self, instance, validated_data):
        """ Update AI Chat. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
