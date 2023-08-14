from rest_framework import serializers

from ...models.streams.header import Header

class HeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Header
        fields = ['id',
                  'guid',
                  'header']
        read_only_fields = ['id']

class HeaderDetailSerializer(HeaderSerializer):
    """ Serializer for convert_to_table_by_specify_headers detail view. """

    class Meta(HeaderSerializer.Meta):
        fields = HeaderSerializer.Meta.fields

