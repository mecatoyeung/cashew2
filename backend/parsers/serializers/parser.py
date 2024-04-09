from rest_framework import serializers

from django.contrib.auth.models import User, Group

from parsers.models.parser import Parser
from parsers.models.ocr import OCR
from parsers.models.chatbot import ChatBot
from parsers.models.open_ai import OpenAI
from parsers.models.open_ai_metrics_key import OpenAIMetricsKey
from parsers.models.splitting import Splitting

from core.serializers.users import UsersSerializer
from core.serializers.group import GroupSerializer

from parsers.serializers.rule import RuleSerializer
from parsers.serializers.source import SourceSerializer
from parsers.serializers.pre_processing import PreProcessingSerializer
from parsers.serializers.ocr import OCRSerializer, ProtectedOCRSerializer
from parsers.serializers.chatbot import ChatBotSerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.serializers.open_ai import OpenAISerializer
from parsers.serializers.open_ai_metrics_key import OpenAIMetricsKeySerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.serializers.post_processing import PostProcessingSerializer
from parsers.serializers.integration import IntegrationSerializer


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
        many=False, required=False, allow_null=True)
    open_ai_metrics_key = OpenAIMetricsKeySerializer(
        many=False, required=False, allow_null=True)
    postprocessings = PostProcessingSerializer(
        many=True, required=False, allow_null=False)
    integrations = IntegrationSerializer(
        many=True, required=False, allow_null=False)
    owner = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),
        default=None)
    permitted_users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all())
    permitted_groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all())

    class Meta:
        model = Parser
        fields = ['id', 'type', 'guid', 'name', 'sources', 'preprocessings',
                  'rules', 'ocr', 'splitting', 'chatbot', 'open_ai', 'open_ai_metrics_key',
                  'postprocessings', 'integrations', 'total_num_of_pages_processed', 
                  'pdf_to_image_dpi',
                  'assumed_text_height', 'assumed_text_width', 'same_column_acceptance_range', 'same_line_acceptance_range',
                  'owner', 'permitted_users', 'permitted_groups',
                  'last_modified_at']
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
    
    def _get_or_create_open_ai_metrics_key(self, open_ai_metrics_key, parser):
        """ Handle getting or creating open ai as needed. """
        open_ai_metrics_key = {}
        open_ai_metrics_key["parser"] = parser
        open_ai_metrics_key["open_ai_metrics_tenant_id"] = ""
        open_ai_metrics_key["open_ai_metrics_client_id"] = ""
        open_ai_metrics_key["open_ai_metrics_client_secret"] = ""
        open_ai_metrics_key["open_ai_metrics_subscription_id"] = ""
        open_ai_metrics_key["open_ai_metrics_service_name"] = ""
        open_ai_metrics_key_obj, created = OpenAIMetricsKey.objects.get_or_create(
            **open_ai_metrics_key,
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
        open_ai_metrics_key = validated_data.pop("open_ai_metrics_key", None)
        splitting = validated_data.pop("splitting", None)

        parser = Parser.objects.create(**validated_data)

        self._get_or_create_ocr(ocr, parser)
        self._get_or_create_chatbot(chatbot, parser)
        self._get_or_create_open_ai(open_ai, parser)
        self._get_or_create_open_ai_metrics_key(open_ai_metrics_key, parser)
        self._get_or_create_splitting(splitting, parser)

        return parser

    def update(self, instance, validated_data):
        """ Update parser. """
        ocr_validated_data = validated_data.pop("ocr", None)
        chatbot_validated_data = validated_data.pop("chatbot", None)
        open_ai_validated_data = validated_data.pop("open_ai", None)
        open_ai_metrics_key_validated_data = validated_data.pop("open_ai_metrics_key", None)
        splitting = validated_data.pop("splitting", None)
        owner =  validated_data.pop("owner", None)
        permitted_users =  validated_data.pop("permitted_users", None)
        permitted_groups =  validated_data.pop("permitted_groups", None)

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

        if open_ai_metrics_key_validated_data is not None:
            open_ai_metrics_key = OpenAIMetricsKey.objects.get(parser_id=instance.id)
            for attr, value in open_ai_metrics_key_validated_data.items():
                setattr(open_ai_metrics_key, attr, value)
            open_ai_metrics_key.save()

        if splitting is not None:
            splitting = Splitting.objects.get(parser_id=instance.id)
            instance.splitting.delete()
            self._get_or_create_splitting(splitting, instance)

        if permitted_users is not None:
            instance.permitted_users.set(permitted_users)

        if permitted_groups is not None:
            instance.permitted_groups.set(permitted_groups)

        instance.save()
        return instance

class ParserCreateSerializer(ParserSerializer):

    pass

class ParserRetrieveSerializer(ParserSerializer):

    pass

class ParserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'type', 'guid', 'name', 'last_modified_at']
        read_only_fields = ['id']

class ParserUpdateSerializer(ParserSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'guid', 'type', 'name', 'ocr',
                  'chatbot', 'open_ai', 'open_ai_metrics_key', 
                  'pdf_to_image_dpi',
                  'assumed_text_height', 'assumed_text_width', 'same_column_acceptance_range', 'same_line_acceptance_range',
                  'owner', 'permitted_users', 'permitted_groups',
                  'last_modified_at']
        read_only_fields = ['id']

class ParserDeleteSerializer(ParserSerializer):

    class Meta:
        model = Parser
        fields = ['id', 'guid', 'type', 'name', 'ocr',
                  'chatbot', 'open_ai', 'open_ai_metrics_key', 
                  'pdf_to_image_dpi',
                  'assumed_text_height', 'assumed_text_width', 'same_column_acceptance_range', 'same_line_acceptance_range',
                  'owner', 'permitted_users', 'permitted_groups',
                  'last_modified_at']
        read_only_fields = ['id']


class ParserExportSerializer(ParserSerializer):

    pass


class ParserImportSerializer(ParserSerializer):

    pass

class ProtectedParserSerializer(ParserSerializer):

    ocr = ProtectedOCRSerializer(
        many=False, required=True, allow_null=True)