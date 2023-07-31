from rest_framework import serializers

from ..models.stream import Stream

class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stream
        fields = ['id',
                  'guid',
                  'rule',
                  'step',
                  'stream_type',
                  'remove_text',
                  'remove_regex',
                  'replace_text',
                  'join_string',
                  'extract_first_n_lines',
                  'extract_nth_line',
                  'combine_first_n_lines',
                  'get_chars_from_next_col_if_regex_not_match',
                  'remove_rows_with_conditions',
                  'merge_rows_with_conditions',
                  'merge_rows_with_same_columns',
                  'remove_rows_before_row_with_conditions',
                  'remove_rows_after_row_with_conditions',
                  'unpivot_table',
                  'convert_to_table_by_specify_headers']
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

