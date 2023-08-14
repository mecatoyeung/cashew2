from rest_framework import serializers

from ...models.streams.convert_to_table_by_specify_headers import ConvertToTableBySpecifyHeaders
from ...models.streams.header import Header

from ...serializers.streams.header import HeaderDetailSerializer

class ConvertToTableBySpecifyHeadersSerializer(serializers.ModelSerializer):

    headers = HeaderDetailSerializer(many=True)

    class Meta:
        model = ConvertToTableBySpecifyHeaders
        fields = ['id',
                  'guid',
                  'headers']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a convert_to_table_by_specify_headers. """
        headers = validated_data.pop('headers', [])
        convert_to_table_by_specify_headers = ConvertToTableBySpecifyHeaders.objects.create(**validated_data)

        for header in headers:
            #header.convert_to_table_by_specify_headers = convert_to_table_by_specify_headers.id
            header_obj, created = Header.objects.get_or_create(
                **header,
            )
            convert_to_table_by_specify_headers.headers.add(header_obj)

        return convert_to_table_by_specify_headers

    def update(self, instance, validated_data):
        """ Update convert_to_table_by_specify_headers. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ConvertToTableBySpecifyHeadersDetailSerializer(ConvertToTableBySpecifyHeadersSerializer):
    """ Serializer for convert_to_table_by_specify_headers detail view. """

    class Meta(ConvertToTableBySpecifyHeadersSerializer.Meta):
        fields = ConvertToTableBySpecifyHeadersSerializer.Meta.fields

