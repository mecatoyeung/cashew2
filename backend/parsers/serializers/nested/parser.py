from rest_framework import serializers

from parsers.models.parser import Parser
from parsers.models.ocr import OCR
from parsers.models.chatbot import ChatBot
from parsers.models.open_ai import OpenAI
from parsers.models.open_ai_metrics_key import OpenAIMetricsKey
from parsers.models.splitting import Splitting

from parsers.serializers.rule import RuleSerializer
from parsers.serializers.source import SourceSerializer
from parsers.serializers.pre_processing import PreProcessingSerializer
from parsers.serializers.ocr import OCRSerializer
from parsers.serializers.chatbot import ChatBotSerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.serializers.open_ai import OpenAISerializer
from parsers.serializers.open_ai_metrics_key import OpenAIMetricsKeySerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.serializers.post_processing import PostProcessingSerializer
from parsers.serializers.integration import IntegrationSerializer


class ParserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parser
        fields = ['id']
        read_only_fields = ['id']

