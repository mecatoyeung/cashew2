from rest_framework import serializers

from ..models.rule import Rule
from ..models.table_column_separator import TableColumnSeparator

from ..serializers.table_column_separator import TableColumnSeparatorSerializer, TableColumnSeparatorDetailSerializer

class RuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rule
        fields = ['id',
                  'parser',
                  'name',
                  'rule_type',
                  'pages',
                  'table_column_separators',
                  'x1',
                  'y1',
                  'x2',
                  'y2',
                  'anchor_text',
                  'anchor_x1',
                  'anchor_y1',
                  'anchor_x2',
                  'anchor_y2',
                  'last_modified_at']
        read_only_fields = ['id', 'parser']

    table_column_separators = TableColumnSeparatorSerializer(many=True)

    def create(self, validated_data):
        """ Create a rule. """
        table_column_separators = validated_data.pop("table_column_separators", None)

        rule = Rule.objects.create(**validated_data)

        for table_column_separator in table_column_separators:
            table_column_separator_obj, created = TableColumnSeparator.objects.get_or_create(
                **table_column_separator,
            )
            rule.table_column_separators.add(table_column_separator_obj)

        return rule

    def update(self, instance, validated_data):
        table_column_separators = validated_data.pop("table_column_separators", None)

        TableColumnSeparator.objects.filter(rule__id=instance.id).delete()

        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        for table_column_separator in table_column_separators:
            table_column_separator_obj, created = TableColumnSeparator.objects.get_or_create(
                **table_column_separator,
            )
            instance.table_column_separators.add(table_column_separator_obj)

        return instance

class RuleDetailSerializer(RuleSerializer):
    """ Serializer for rule detail view. """

    class Meta(RuleSerializer.Meta):
        fields = RuleSerializer.Meta.fields

