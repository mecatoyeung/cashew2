from rest_framework import serializers

from ..models.table_column_separator import TableColumnSeparator

class TableColumnSeparatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = TableColumnSeparator
        fields = ['id',
                  'rule',
                  'x']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a rule. """
        table_column_separator = TableColumnSeparator.objects.create(**validated_data)

        return table_column_separator

    def update(self, instance, validated_data):
        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class TableColumnSeparatorDetailSerializer(TableColumnSeparatorSerializer):
    """ Serializer for rule detail view. """

    class Meta(TableColumnSeparatorSerializer.Meta):
        fields = TableColumnSeparatorSerializer.Meta.fields

