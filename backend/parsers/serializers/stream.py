from rest_framework import serializers

from ..models.stream import Stream
from ..models.rule import RuleType
from ..models.streams.convert_to_table_by_specify_headers import ConvertToTableBySpecifyHeaders
from ..models.streams.header import Header

from ..serializers.streams.convert_to_table_by_specify_headers import ConvertToTableBySpecifyHeadersDetailSerializer
from ..serializers.streams.header import HeaderDetailSerializer

class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stream
        fields = ['id',
                  'guid',
                  'rule',
                  'step',
                  'type',
                  'stream_class',
                  'text',
                  'regex',
                  'join_string',
                  'extract_first_n_lines',
                  'extract_nth_lines',
                  'combine_first_n_lines',
                  'convert_to_table_by_specify_headers',
                  #'get_chars_from_next_col_if_regex_not_match',
                  #'remove_rows_with_conditions',
                  #'merge_rows_with_conditions',
                  #'merge_rows_with_same_columns',
                  #'remove_rows_before_row_with_conditions',
                  #'remove_rows_after_row_with_conditions',
                  #'unpivot_table'
                  ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a stream. """
        stream = Stream.objects.create(**validated_data)

        return stream

    def update(self, instance, validated_data):
        """ Update stream. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class StreamDetailSerializer(StreamSerializer):
    """ Serializer for stream detail view. """

    class Meta(StreamSerializer.Meta):
        fields = StreamSerializer.Meta.fields


class StreamPostSerializer(StreamSerializer):

    class Meta(StreamSerializer.Meta):
        fields = StreamSerializer.Meta.fields

    convert_to_table_by_specify_headers = ConvertToTableBySpecifyHeadersDetailSerializer(many=False)

    def create(self, validated_data):

        convert_to_table_by_specify_headers = validated_data.pop("convert_to_table_by_specify_headers", None)
        #headers = convert_to_table_by_specify_headers.pop("headers")

        stream_instance = Stream.objects.create(**validated_data)
        if convert_to_table_by_specify_headers is not None:
            convert_to_table_by_specify_headers_serializer = ConvertToTableBySpecifyHeadersDetailSerializer(data=convert_to_table_by_specify_headers)
            if convert_to_table_by_specify_headers_serializer.is_valid():
                convert_to_table_by_specify_headers_obj = convert_to_table_by_specify_headers_serializer.save()

        stream_instance.convert_to_table_by_specify_headers = convert_to_table_by_specify_headers_obj
        stream_instance.save()

        return stream_instance