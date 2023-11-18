from rest_framework import serializers

from parsers.models.source import Source


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id',
                  'parser',
                  'name',
                  'source_path',
                  'interval_seconds',
                  'next_run_time',
                  'activated']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a source. """

        source = Source.objects.create(**validated_data)

        return source

    def update(self, instance, validated_data):
        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class SourceCreateSerializer(SourceSerializer):
    pass
