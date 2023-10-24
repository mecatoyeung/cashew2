from rest_framework import serializers

from ..models.integration import Integration


class IntegrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Integration
        fields = ['id',
                  'integration_type',
                  'name',
                  'parser',
                  'xml_path',
                  'template',
                  'pdf_integration_type',
                  'pre_processing',
                  'post_processing',
                  'pdf_path',
                  'interval_seconds',
                  'next_run_time',
                  'activated']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a source. """

        integration = Integration.objects.create(**validated_data)

        return integration

    def update(self, instance, validated_data):
        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class IntegrationCreateSerializer(IntegrationSerializer):
    pass
