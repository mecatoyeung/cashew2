from rest_framework import serializers

from parsers.models.pre_processing import PreProcessing


class PreProcessingSerializer(serializers.ModelSerializer):

    class Meta:

        model = PreProcessing
        fields = ['id',
                  'pre_processing_type',
                  'name',
                  'parser',
                  'step']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a source. """

        pre_processing = PreProcessing.objects.create(**validated_data)

        return pre_processing

    def update(self, instance, validated_data):
        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class PreProcessingCreateSerializer(PreProcessingSerializer):
    pass
