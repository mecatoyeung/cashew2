from rest_framework import serializers

from ..models.post_processing import PostProcessing


class PostProcessingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostProcessing
        fields = ['id',
                  'post_processing_type',
                  'name',
                  'parser',
                  'step']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a source. """

        pre_processing = PostProcessing.objects.create(**validated_data)

        return pre_processing

    def update(self, instance, validated_data):
        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class PostProcessingCreateSerializer(PostProcessingSerializer):
    pass
