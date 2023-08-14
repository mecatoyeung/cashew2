from rest_framework import serializers

from ...models.streams.column_condition import ColumnCondition

class ColumnConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ColumnCondition
        fields = ['id',
                  'guid',
                  'merge_rows_with_conditions']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a merge_rows_with_conditions. """
        header = ColumnCondition.objects.create(**validated_data)

        return header

    def update(self, instance, validated_data):
        """ Update merge_rows_with_conditions. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ColumnConditionDetailSerializer(ColumnConditionSerializer):
    """ Serializer for merge_rows_with_conditions detail view. """

    class Meta(ColumnConditionSerializer.Meta):
        fields = ColumnConditionSerializer.Meta.fields

