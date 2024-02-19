from rest_framework import serializers

from parsers.models.open_ai_metrics_key import OpenAIMetricsKey


class OpenAIMetricsKeySerializer(serializers.ModelSerializer):

    open_ai_metrics_tenant_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_metrics_client_id  = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_metrics_client_secret = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_metrics_subscription_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    open_ai_metrics_service_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = OpenAIMetricsKey
        fields = ['id', 'open_ai_metrics_tenant_id', 'open_ai_metrics_client_id',
                  'open_ai_metrics_client_secret', 'open_ai_metrics_subscription_id', 'open_ai_metrics_service_name']
        read_only_fields = ['id', 'parser']

    def create(self, validated_data):
        """ Create a Open AI. """
        open_ai_metrics_key = OpenAIMetricsKey.objects.create(**validated_data)

        return open_ai_metrics_key

    def update(self, instance, validated_data):
        """ Update AI Chat. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
