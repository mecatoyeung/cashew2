from rest_framework import serializers

from parsers.models.parser import Parser
from parsers.models.rule import Rule
from parsers.models.table_column_separator import TableColumnSeparator
from parsers.models.document import Document

from parsers.serializers.table_column_separator import TableColumnSeparatorSerializer
from parsers.serializers.document import DocumentSerializer

from parsers.helpers.document_parser import DocumentParser


class AnchorDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = [
            'id',
        ]

class RuleSerializer(serializers.ModelSerializer):

    anchor_text = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    anchor_document = AnchorDocumentSerializer(many=False,
        required=False, allow_null=True)

    class Meta:
        model = Rule
        fields = ['id',
                  'guid',
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
                  'anchor_relative_x1',
                  'anchor_relative_y1',
                  'anchor_relative_x2',
                  'anchor_relative_y2',
                  'anchor_document',
                  'anchor_page_num',
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

    def _set_anchor(self, rule, validated_data):
        anchor_document = validated_data.pop("anchor_document", None)
        anchor_text = validated_data.pop("anchor_text", "")
        if anchor_document and not anchor_document == None:
            parser = Parser.objects.get(pk=rule.parser_id)
            document = Document.objects.get(
                pk=anchor_document.id)
            document_parser = DocumentParser(parser, document)
            relative_anchor_region = document_parser.get_anchor_relative_region(
                rule)
            rule.anchor_relative_x1 = relative_anchor_region.x1
            rule.anchor_relative_y1 = relative_anchor_region.y1
            rule.anchor_relative_x2 = relative_anchor_region.x2
            rule.anchor_relative_y2 = relative_anchor_region.y2
            rule.anchor_text = anchor_text

    def create(self, validated_data):
        """ Create a rule. """
        table_column_separators = validated_data.pop(
            "table_column_separators", [])

        rule = Rule.objects.create(**validated_data)

        self._set_anchor(rule, validated_data)

        rule.save()

        self._get_or_create_table_column_separators(
            table_column_separators, rule)

        return rule

    def update(self, instance, validated_data):

        table_column_separators = validated_data.pop(
            "table_column_separators", None)

        TableColumnSeparator.objects.filter(rule__id=instance.id).delete()

        """ Update rule. """
        for attr, value in validated_data.items():
            if attr == "anchor_document":
                continue
            setattr(instance, attr, value)

        instance.save()

        self._set_anchor(instance, validated_data)

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
