import re

from rest_framework import (
    viewsets,
)

from django.db.models import Prefetch

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

import requests
import json

from parsers.models.parser import Parser
from parsers.models.rule import Rule
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.source import Source
from parsers.models.chatbot import ChatBot
from parsers.models.integration import Integration
from parsers.models.splitting_type import SplittingType
from parsers.models.splitting import Splitting
from parsers.models.splitting_rule_type import SplittingRuleType
from parsers.models.splitting_rule import SplittingRule

from parsers.serializers.parser import ParserSerializer, ParserUpdateSerializer
from parsers.serializers.rule import RuleSerializer
from parsers.serializers.source import SourceSerializer
from parsers.serializers.integration import IntegrationSerializer
from parsers.serializers.splitting import SplittingSerializer

from parsers.helpers.document_parser import DocumentParser


class ParserViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = ParserSerializer
    queryset = Parser.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """ Convert a list of strings to integers. """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        return queryset.filter(
            user=self.request.user
        ).prefetch_related("rules") \
            .select_related("chatbot") \
            .order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return ParserSerializer
        elif self.action == 'update':
            return ParserUpdateSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new parser. """
        serializer.save(user=self.request.user)

    @action(detail=False,
            methods=['GET'],
            name='Get Sources for this parser',
            url_path='(?P<pk>[^/.]+)/sources')
    def get_sources(self, request, pk, *args, **kwargs):

        sources = Source.objects.filter(parser_id=pk)

        return Response(SourceSerializer(sources, many=True).data, status=200)

    @action(detail=False,
            methods=['GET'],
            name='Get Rules for this parser',
            url_path='(?P<pk>[^/.]+)/rules')
    def get_rules(self, request, pk, *args, **kwargs):

        rules = Rule.objects.filter(parser_id=pk)

        return Response(RuleSerializer(rules, many=True).data, status=200)

    @action(detail=False,
            methods=['GET'],
            name='Get Integrations for this parser',
            url_path='(?P<pk>[^/.]+)/integrations')
    def get_integrations(self, request, pk, *args, **kwargs):

        integrations = Integration.objects.filter(parser_id=pk)

        return Response(IntegrationSerializer(integrations, many=True).data, status=200)

    @action(detail=False,
            methods=['GET'],
            name='Get Splitting for this parser',
            url_path='(?P<pk>[^/.]+)/splitting')
    def get_splitting(self, request, pk, *args, **kwargs):

        if Splitting.objects.filter(parser_id=pk).count() == 0:
            splitting = Splitting()
            splitting.parser_id = pk
            splitting.split_type = SplittingType.SPLIT_BY_CONDITIONS.value
            splitting.save()

        splitting = Splitting.objects.prefetch_related(Prefetch(
            "splitting_rules",
            queryset=SplittingRule.objects.filter(
                splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
            .prefetch_related("splitting_conditions")
            .prefetch_related(
                Prefetch("consecutive_page_splitting_rules",
                         queryset=SplittingRule.objects.prefetch_related("splitting_conditions"))))).get(parser_id=pk)

        return Response(SplittingSerializer(splitting).data, status=200)

    @action(detail=True,
            methods=['GET'],
            name='Get All Texts',
            url_path='document/(?P<document_id>[^/.]+)/pages/(?P<page_num>[^/.]+)/extract_all_text')
    def extract_all_text_in_one_page(self, request, pk, document_id, page_num, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(parser, document)

        result = document_parser.extract_all_text_in_one_page(page_num)

        return Response(result, status=200)

    @action(detail=True,
            methods=['POST'],
            name='Ask OpenAI about PDF content',
            url_path='documents/(?P<document_id>[^/.]+)/pages/(?P<page_num>[^/.]+)/ask_openai')
    def ask_openai_about_pdf_content(self, request, pk, document_id, page_num, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(parser, document)

        chatbot = ChatBot.objects.get(parser_id=parser.id)

        question = request.data["question"]

        if question == "":
            return Response("Please ask me with meaningful questions.", status=200)

        # content_to_be_sent_to_openai = "\n".join(
        #    document_parser.extract_all_text_in_one_page(page_num))

        content_to_be_sent_to_openai = "\n".join(
            document_parser.extract_all_text_in_all_pages())

        content_to_be_sent_to_openai = re.sub(
            ' +', '\n', content_to_be_sent_to_openai)

        try:

            headers = {
                "Content-Type": "application/json",
                "api-key": chatbot.open_ai_api_key
            }
            open_ai_content = question + \
                " Please return in JSON format.\nInput: " + content_to_be_sent_to_openai
            json_data = {
                "messages": [{"role": "user", "content": open_ai_content}],
            }

            response = requests.post('https://' + chatbot.open_ai_resource_name + '.openai.azure.com/openai/deployments/gpt-35/chat/completions?api-version=2023-05-15',
                                     data=json.dumps(json_data), headers=headers)
            response_dict = json.loads(
                response.json()["choices"][0]["message"]['content'].replace("Output:", ""))

            """response_dict = {
                "Document No": "12345",
                "Document Date": "11 Dec 2023",
                "Item Table": [
                    {
                        "Item Description": "Car",
                        "Quantity": 123,
                        "Amount": 123.00
                    },
                    {
                        "Item Description": "Ship",
                        "Quantity": 234,
                        "Amount": 234.00
                    },
                    {
                        "Item Description": "Airplane",
                        "Quantity": 345,
                        "Amount": 345.00
                    }
                ]
            }"""

            return Response(response_dict, status=200)

        except Exception as e:
            raise e
