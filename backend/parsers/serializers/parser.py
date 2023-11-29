from rest_framework import serializers

from parsers.models.parser import Parser
from parsers.models.ocr import OCR
from parsers.models.chatbot import ChatBot
from parsers.models.open_ai import OpenAI
from parsers.models.splitting import Splitting

from parsers.serializers.rule import RuleSerializer
from parsers.serializers.source import SourceSerializer
from parsers.serializers.pre_processing import PreProcessingSerializer
from parsers.serializers.ocr import OCRSerializer
from parsers.serializers.chatbot import ChatBotSerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.serializers.open_ai import OpenAISerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.serializers.post_processing import PostProcessingSerializer
from parsers.serializers.integration import IntegrationSerializer


class ParserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'type', 'guid', 'name', 'last_modified_at']
        read_only_fields = ['id']


class ParserSerializer(serializers.ModelSerializer):

    sources = SourceSerializer(
        many=True, required=False, allow_null=False)
    preprocessings = PreProcessingSerializer(
        many=True, required=False, allow_null=False)
    ocr = OCRSerializer(
        many=False, required=True, allow_null=True)
    splitting = SplittingSerializer(
        many=False, required=False, allow_null=True)
    rules = RuleSerializer(many=True, required=False, allow_null=True)
    chatbot = ChatBotSerializer(
        many=False, required=True, allow_null=True)
    open_ai = OpenAISerializer(
        many=False, required=True, allow_null=False)
    postprocessings = PostProcessingSerializer(
        many=True, required=False, allow_null=False)
    integrations = IntegrationSerializer(
        many=True, required=False, allow_null=False)

    class Meta:
        model = Parser
        fields = ['id', 'type', 'guid', 'name', 'sources', 'preprocessings',
                  'rules', 'ocr', 'splitting', 'chatbot', 'open_ai',
                  'postprocessings', 'integrations', 'last_modified_at']
        read_only_fields = ['id']

    def _get_or_create_ocr(self, ocr, parser):
        """ Handle getting or creating ocr as needed. """
        ocr["parser"] = parser
        ocr_obj, created = OCR.objects.get_or_create(
            **ocr,
        )

    def _get_or_create_chatbot(self, chatbot, parser):
        """ Handle getting or creating ai chat as needed. """
        chatbot["parser"] = parser
        chatbot_obj, created = ChatBot.objects.get_or_create(
            **chatbot,
        )

    def _get_or_create_open_ai(self, open_ai, parser):
        """ Handle getting or creating open ai as needed. """
        open_ai["parser"] = parser
        open_ai_obj, created = OpenAI.objects.get_or_create(
            **open_ai,
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
        chatbot = validated_data.pop("chatbot", None)
        open_ai = validated_data.pop("open_ai", None)
        splitting = validated_data.pop("splitting", None)

        parser = Parser.objects.create(**validated_data)

        self._get_or_create_ocr(ocr, parser)
        self._get_or_create_chatbot(chatbot, parser)
        self._get_or_create_open_ai(open_ai, parser)
        self._get_or_create_splitting(splitting, parser)

        return parser

    def update(self, instance, validated_data):
        """ Update parser. """
        ocr_validated_data = validated_data.pop("ocr", None)
        chatbot_validated_data = validated_data.pop("chatbot", None)
        open_ai_validated_data = validated_data.pop("open_ai", None)
        splitting = validated_data.pop("splitting", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if ocr_validated_data is not None:
            ocr = OCR.objects.get(parser_id=instance.id)
            for attr, value in ocr_validated_data.items():
                setattr(ocr, attr, value)
            ocr.save()

        if chatbot_validated_data is not None:
            chatbot = ChatBot.objects.get(parser_id=instance.id)
            for attr, value in chatbot_validated_data.items():
                setattr(chatbot, attr, value)
            chatbot.save()

        if open_ai_validated_data is not None:
            open_ai = OpenAI.objects.get(parser_id=instance.id)
            for attr, value in open_ai_validated_data.items():
                setattr(open_ai, attr, value)
            open_ai.save()

        if splitting is not None:
            splitting = Splitting.objects.get(parser_id=instance.id)
            instance.splitting.delete()
            self._get_or_create_splitting(splitting, instance)

        instance.save()
        return instance


class ParserUpdateSerializer(ParserSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'guid', 'type', 'name', 'ocr',
                  'chatbot', 'open_ai', 'last_modified_at']
        read_only_fields = ['id']


class ParserExportSerializer(ParserSerializer):

    pass


class ParserImportSerializer(ParserSerializer):

    pass
