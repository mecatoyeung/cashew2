from rest_framework import serializers

from parsers.models.stream_condition import StreamCondition


class StreamConditionSerializer(serializers.ModelSerializer):
    """ Serializer for stream condition. """

    value = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = StreamCondition
        fields = ['id', 'guid', 'column', 'operator', 'value']
        read_only_fields = ['id']
