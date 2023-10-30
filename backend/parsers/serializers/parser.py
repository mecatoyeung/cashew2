from rest_framework import serializers

from ..models.parser import Parser
from ..models.ocr import OCR
from ..models.splitting import Splitting
from .rule import RuleSerializer
from .ocr import OCRSerializer
from .splitting import SplittingSerializer
from .integration import IntegrationSerializer


class ParserSerializer(serializers.ModelSerializer):

    ocr = OCRSerializer(many=False, required=True, allow_null=False)
    # splitting = SplittingSerializer(
    # many=False, required=False, allow_null=False)
    integrations = IntegrationSerializer(
        many=True, required=False, allow_null=False)

    class Meta:
        model = Parser
        fields = ['id', 'type', 'name', 'rules', 'ocr',
                  'integrations',    'last_modified_at']
        read_only_fields = ['id']

    rules = RuleSerializer(many=True, required=False, allow_null=True)

    def _get_or_create_ocr(self, ocr, parser):
        """ Handle getting or creating ocr as needed. """
        ocr["parser"] = parser
        ocr_obj, created = OCR.objects.get_or_create(
            **ocr,
        )

    def _get_or_create_splitting(self, splitting, parser):
        """ Handle getting or creating splitting as needed. """
        if splitting == None:
            return
        splitting["parser"] = parser
        splitting_obj, created = Splitting.objects.get_or_create(
            **splitting,
        )

    def create(self, validated_data):
        """ Create a parser. """
        ocr = validated_data.pop("ocr", None)
        splitting = validated_data.pop("splitting", None)

        parser = Parser.objects.create(**validated_data)

        self._get_or_create_ocr(ocr, parser)
        self._get_or_create_splitting(splitting, parser)

        return parser

    def update(self, instance, validated_data):
        """ Update parser. """
        ocr_validated_data = validated_data.pop("ocr", None)
        splitting = validated_data.pop("splitting", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if ocr_validated_data is not None:
            ocr = OCR.objects.get(parser_id=instance.id)
            for attr, value in ocr_validated_data.items():
                setattr(ocr, attr, value)
            ocr.save()

        if splitting is not None:
            splitting = Splitting.objects.get(parser_id=instance.id)
            instance.splitting.delete()
            self._get_or_create_splitting(splitting, instance)

        instance.save()
        return instance


class ParserUpdateSerializer(ParserSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'type', 'name', 'ocr', 'last_modified_at']
        read_only_fields = ['id']
