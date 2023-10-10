from rest_framework import serializers

from ..models.parser import Parser
from ..models.ocr import OCR
from .rule import RuleSerializer
from .ocr import OCRSerializer

class ParserSerializer(serializers.ModelSerializer):

    ocr = OCRSerializer(many=False, required=True, allow_null=False)

    class Meta:
        model = Parser
        fields = ['id', 'type', 'name', 'rules', 'ocr', 'last_modified_at']
        read_only_fields = ['id']

    rules = RuleSerializer(many=True, required=False, allow_null=True)

    def _get_or_create_ocr(self, ocr, parser):
        """ Handle getting or creating ocr as needed. """
        ocr["parser"] = parser
        ocr_obj, created = OCR.objects.get_or_create(
            **ocr,
        )

    def create(self, validated_data):
        """ Create a parser. """
        ocr = validated_data.pop("ocr", None)

        parser = Parser.objects.create(**validated_data)

        self._get_or_create_ocr(ocr, parser)

        return parser

    def update(self, instance, validated_data):
        """ Update parser. """
        ocr = validated_data.pop("ocr", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if ocr is not None:
            instance.ocr.clear()
            self._get_or_create_table_column_separators(ocr, instance)

        instance.save()
        return instance
