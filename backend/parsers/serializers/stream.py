from rest_framework import serializers

from parsers.models.stream import Stream
from parsers.models.stream_condition import StreamCondition
from parsers.models.rule import RuleType

from parsers.serializers.stream_condition import StreamConditionSerializer


class StreamSerializer(serializers.ModelSerializer):

    text = serializers.CharField(
        trim_whitespace=False, allow_blank=True, allow_null=True)
    regex = serializers.CharField(
        trim_whitespace=False, allow_blank=True, allow_null=True)
    join_string = serializers.CharField(
        trim_whitespace=False, allow_blank=True, allow_null=True)
    open_ai_question = serializers.CharField(
        trim_whitespace=False, allow_blank=True, allow_null=True)
    stream_conditions = StreamConditionSerializer(many=True, required=False)

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
                  'open_ai_question',
                  'combine_first_n_lines',
                  'convert_to_table_by_specify_headers',
                  'col_index',
                  'col_indexes',
                  'stream_conditions',
                  'remove_matched_row_also',
                  'unpivot_column_index',
                  'unpivot_newline_char',
                  'unpivot_property_assign_char',
                  'json_extract_code',
                  'current_page_regex',
                  'last_page_regex',
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
        model = Stream
        fields = StreamSerializer.Meta.fields
        read_only_fields = StreamSerializer.Meta.read_only_fields


class StreamPostSerializer(StreamSerializer):

    class Meta(StreamSerializer.Meta):
        model = Stream
        fields = StreamSerializer.Meta.fields
        read_only_fields = StreamSerializer.Meta.read_only_fields

    def _get_or_create_stream_conditions(self, stream_conditions, stream):
        """ Handle getting or creating tags as needed. """
        for stream_condition_index in range(len(stream_conditions)):
            stream_condition = stream_conditions[stream_condition_index]
            stream_condition['stream_id'] = stream.id
            stream_condition['sort_order'] = stream_condition_index * 10
            stream_condition_obj, created = StreamCondition.objects.get_or_create(
                **stream_condition,
            )
            stream.streamcondition_set.add(stream_condition_obj)

    def create(self, validated_data):

        stream_conditions = validated_data.pop('stream_conditions', [])

        streams_that_are_after_created_stream = Stream.objects.filter(rule__id=validated_data["rule"].id, step__gte=validated_data["step"])
        for s in streams_that_are_after_created_stream:
            s.step = s.step + 1
            s.save()

        instance = Stream.objects.create(**validated_data)

        self._get_or_create_stream_conditions(stream_conditions, instance)

        instance.save()

        return instance

    def update(self, instance, validated_data):
        """ Update Stream. """
        stream_conditions = validated_data.pop("stream_conditions", None)

        if stream_conditions is not None:
            instance.stream_conditions.clear()
            self._get_or_create_stream_conditions(stream_conditions, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
