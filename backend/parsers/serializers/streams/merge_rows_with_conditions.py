from rest_framework import serializers

from ...models.streams.merge_rows_with_conditions import MergeRowsWithConditions

class MergeRowsWithConditionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MergeRowsWithConditions
        fields = ['id',
                  'guid',
                  'column_conditions']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a merge_rows_with_conditions. """
        merge_rows_with_conditions = MergeRowsWithConditions.objects.create(**validated_data)

        return merge_rows_with_conditions

    def update(self, instance, validated_data):
        """ Update merge_rows_with_conditions. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class MergeRowsWithConditionsDetailSerializer(MergeRowsWithConditionsSerializer):
    """ Serializer for merge_rows_with_conditions detail view. """

    class Meta(MergeRowsWithConditionsSerializer.Meta):
        fields = MergeRowsWithConditionsSerializer.Meta.fields

