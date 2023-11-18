from rest_framework import serializers

from parsers.models.parser import Parser
from parsers.models.rule import Rule
from parsers.models.table_column_separator import TableColumnSeparator

from parsers.serializers.table_column_separator import TableColumnSeparatorSerializer


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
        read_only_fields = ['id']

    table_column_separators = TableColumnSeparatorSerializer(
        many=True, required=False, allow_null=True)

    def _get_or_create_table_column_separators(self, table_column_separators, rule):
        """ Handle getting or creating tags as needed. """
        for table_column_separator in table_column_separators:
            table_column_separator.rule = rule
            table_column_separator_obj, created = TableColumnSeparator.objects.get_or_create(
                **table_column_separator,
            )
            rule.table_column_separators.add(table_column_separator_obj)

    def create(self, validated_data):
        """ Create a rule. """
        table_column_separators = validated_data.pop(
            "table_column_separators", [])

        rule = Rule.objects.create(**validated_data)

        self._get_or_create_table_column_separators(
            table_column_separators, rule)

        return rule

    def update(self, instance, validated_data):

        table_column_separators = validated_data.pop(
            "table_column_separators", None)

        TableColumnSeparator.objects.filter(rule__id=instance.id).delete()

        """ Update rule. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if table_column_separators is not None:
            instance.table_column_separators.all().delete()
            self._get_or_create_table_column_separators(
                table_column_separators, instance)

        return instance


class RuleCreateSerializer(RuleSerializer):
    pass


class RuleUpdateSerializer(RuleSerializer):
    pass
