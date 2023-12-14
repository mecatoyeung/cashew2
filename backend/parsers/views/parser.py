import re
from datetime import datetime
import traceback

from rest_framework import (
    viewsets,
)

from django.db.models import Prefetch

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication

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
from parsers.models.table_column_separator import TableColumnSeparator
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.source import Source
from parsers.models.pre_processing import PreProcessing
from parsers.models.ocr import OCR
from parsers.models.chatbot import ChatBot
from parsers.models.chatbot_type import ChatBotType
from parsers.models.open_ai import OpenAI
from parsers.models.integration import Integration
from parsers.models.splitting_type import SplittingType
from parsers.models.splitting import Splitting
from parsers.models.splitting_rule_type import SplittingRuleType
from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_condition import SplittingCondition
from parsers.models.post_processing import PostProcessing

from parsers.serializers.parser import ParserSerializer, ParserListSerializer, ParserUpdateSerializer, ParserExportSerializer, ParserImportSerializer
from parsers.serializers.rule import RuleSerializer
from parsers.serializers.source import SourceSerializer
from parsers.serializers.integration import IntegrationSerializer
from parsers.serializers.splitting import SplittingSerializer
from parsers.helpers.document_parser import DocumentParser


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class ParserViewSet(viewsets.ModelViewSet):
    """ View for manage recipe APIs. """
    serializer_class = ParserSerializer
    queryset = Parser.objects.all()
    """authentication_classes = [
        TokenAuthentication]
    permission_classes = [IsAuthenticated]"""

    def _params_to_ints(self, qs):
        """ Convert a list of strings to integers. """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        if self.action == "retrieve":
            return queryset.filter(
                user=self.request.user
            ).prefetch_related('sources') \
                .select_related("ocr") \
                .select_related("chatbot") \
                .select_related("open_ai") \
                .prefetch_related('rules') \
                .prefetch_related('rules__table_column_separators') \
                .prefetch_related('rules__streams') \
                .prefetch_related("preprocessings") \
                .prefetch_related("integrations") \
                .prefetch_related("postprocessings") \
                .select_related("splitting") \
                .prefetch_related(Prefetch("splitting__splitting_rules", queryset=SplittingRule.objects.filter(
                    splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
                    .prefetch_related("splitting_conditions")
                    .prefetch_related(Prefetch("consecutive_page_splitting_rules",
                                               queryset=SplittingRule.objects.prefetch_related("splitting_conditions").filter(
                                                   splitting_rule_type=SplittingRuleType.CONSECUTIVE_PAGE.value)))
                ))

        return queryset.filter(
            user=self.request.user
        ).prefetch_related("rules") \
            .select_related("chatbot") \
            .select_related("ocr") \
            .order_by('id').distinct()

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'list':
            return ParserListSerializer
        elif self.action == "retrieve":
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
            queryset=SplittingRule.objects.prefetch_related("splitting_conditions").filter(
                splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
            .prefetch_related(
                Prefetch("consecutive_page_splitting_rules",
                         queryset=SplittingRule.objects.prefetch_related("splitting_conditions"))))).get(parser_id=pk)

        return Response(SplittingSerializer(splitting).data, status=200)

    @action(detail=False,
            methods=['GET'],
            name='Export parser',
            url_path='(?P<pk>[^/.]+)/export')
    def export(self, request, pk, *args, **kwargs):

        serializer_class = ParserExportSerializer

        try:

            data = []
            all_parser_ids = []
            try:
                splitting = Splitting.objects.prefetch_related(
                    "splitting_rules").get(parser__id=pk)
                splitting_rules = splitting.splitting_rules.all()
                if len(splitting_rules) > 0:
                    for splitting_rule in splitting_rules:
                        if splitting_rule.route_to_parser == None:
                            continue
                        all_parser_ids.append(
                            splitting_rule.route_to_parser.id)

            except Splitting.DoesNotExist:
                pass

            all_parser_ids.append(pk)

            for parser_id in all_parser_ids:
                parser = Parser \
                    .objects \
                    .prefetch_related('sources') \
                    .select_related("ocr") \
                    .select_related("chatbot") \
                    .select_related("open_ai") \
                    .prefetch_related('rules') \
                    .prefetch_related('rules__table_column_separators') \
                    .prefetch_related('rules__streams') \
                    .prefetch_related("preprocessings") \
                    .prefetch_related("integrations") \
                    .prefetch_related("postprocessings") \
                    .select_related("splitting") \
                    .prefetch_related(Prefetch("splitting__splitting_rules", queryset=SplittingRule.objects.filter(
                        splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
                        .prefetch_related("splitting_conditions")
                        .prefetch_related(Prefetch("consecutive_page_splitting_rules",
                                                   queryset=SplittingRule.objects.prefetch_related("splitting_conditions").filter(
                                                       splitting_rule_type=SplittingRuleType.CONSECUTIVE_PAGE.value)))
                    )) \
                    .get(pk=parser_id)

                serializer = ParserExportSerializer(parser)
                data.append(serializer.data)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "ERROR", "detail": str(e)}, status=400)

    @action(detail=False,
            methods=['POST'],
            name='Import parser',
            url_path='import')
    def import_parsers(self, request, *args, **kwargs):

        serializer_class = ParserImportSerializer

        try:

            import_json_file_obj = request.FILES['import_parsers.json']

            json_obj = json.load(import_json_file_obj)

            splitting_parser_ids_mapping = {}

            splitting_parser_counter = 0
            for parser_json_obj in json_obj:

                splitting_parser_counter += 1

                parser = Parser()
                parser.guid = parser_json_obj["guid"]
                parser.type = parser_json_obj["type"]
                parser.name = parser_json_obj["name"]
                parser.last_modified_at = datetime.now()
                parser.user = request.user

                parser.save()

                if splitting_parser_counter < len(json_obj):
                    splitting_parser_ids_mapping[parser_json_obj["id"]] = parser.id

                for source_json_obj in parser_json_obj["sources"]:
                    s = Source(
                        name=source_json_obj["name"],
                        guid=source_json_obj["guid"],
                        parser_id=parser.id,
                        source_path=source_json_obj["sourcePath"],
                        interval_seconds=source_json_obj["intervalSeconds"],
                        next_run_time=source_json_obj["nextRunTime"],
                        activated=source_json_obj["activated"]
                    )
                    s.save()

                for preprocessing_json_obj in parser_json_obj["preprocessings"]:
                    pp = PreProcessing(
                        guid=preprocessing_json_obj["guid"],
                        name=preprocessing_json_obj["name"],
                        pre_processing_type=preprocessing_json_obj["preProcessingType"],
                        parser=parser,
                        step=preprocessing_json_obj["step"]
                    )
                    pp.save()

                ocr = OCR()
                ocr.guid = parser_json_obj["ocr"]["guid"]
                ocr.parser = parser
                ocr.ocr_type = parser_json_obj["ocr"]["ocrType"]
                ocr.google_vision_ocr_api_key = parser_json_obj["ocr"]["googleVisionOcrApiKey"]
                ocr.paddle_ocr_language = parser_json_obj["ocr"]["paddleOcrLanguage"]
                ocr.save()

                for rule_json_obj in parser_json_obj["rules"]:
                    r = Rule(
                        guid=rule_json_obj["guid"],
                        parser_id=parser.id,
                        name=rule_json_obj["name"],
                        rule_type=rule_json_obj["ruleType"],
                        pages=rule_json_obj["pages"],
                        x1=rule_json_obj["x1"],
                        y1=rule_json_obj["y1"],
                        x2=rule_json_obj["x2"],
                        y2=rule_json_obj["y2"],
                        anchor_text=rule_json_obj["anchorText"],
                        anchor_x1=rule_json_obj["anchorX1"],
                        anchor_y1=rule_json_obj["anchorY1"],
                        anchor_x2=rule_json_obj["anchorX2"],
                        anchor_y2=rule_json_obj["anchorY2"],
                        anchor_relative_x1=rule_json_obj["anchorRelativeX1"],
                        anchor_relative_y1=rule_json_obj["anchorRelativeY1"],
                        anchor_relative_x2=rule_json_obj["anchorRelativeX2"],
                        anchor_relative_y2=rule_json_obj["anchorRelativeY2"],
                        anchor_document=None,
                        anchor_page_num=rule_json_obj["anchorPageNum"],
                        last_modified_at=datetime.now()
                    )
                    r.save()
                    for table_column_separator_json_obj in rule_json_obj["tableColumnSeparators"]:
                        table_column_separator = TableColumnSeparator(
                            rule=r.id,
                            x=table_column_separator_json_obj["x"]
                        )
                        table_column_separator.save()

                if not parser_json_obj["splitting"] == None:

                    splitting = Splitting()
                    splitting.guid = parser_json_obj["splitting"]["guid"]
                    splitting.parser = parser
                    splitting.split_type = parser_json_obj["splitting"]["splitType"]
                    splitting.activated = parser_json_obj["splitting"]["activated"]
                    splitting.save()

                    for splitting_rule_json_obj in parser_json_obj["splitting"]["splittingRules"]:
                        splitting_rule = SplittingRule()
                        splitting_rule.splitting = splitting
                        splitting_rule.route_to_parser = Parser.objects.get(pk=splitting_parser_ids_mapping[
                            splitting_rule_json_obj["routeToParser"]])
                        splitting_rule.splitting_rule_type = splitting_rule_json_obj[
                            "splittingRuleType"]
                        splitting_rule.parent_splitting_rule = splitting_rule_json_obj[
                            "parentSplittingRule"]
                        splitting_rule.sort_order = splitting_rule_json_obj["sortOrder"]
                        splitting_rule.save()

                        for splitting_condition_json_obj in splitting_rule_json_obj["splittingConditions"]:
                            splitting_condition = SplittingCondition()
                            splitting_condition.rule = r
                            splitting_condition.splitting_rule = splitting_rule
                            splitting_condition.operator = splitting_condition_json_obj["operator"]
                            splitting_condition.value = splitting_condition_json_obj["value"]
                            splitting_condition.sort_order = splitting_condition_json_obj["sortOrder"]
                            splitting_condition.save()

                        for consecutive_splitting_rule_json_obj in splitting_rule_json_obj["consecutivePageSplittingRules"]:
                            consecutive_splitting_rule = SplittingRule()
                            consecutive_splitting_rule.splitting = splitting
                            consecutive_splitting_rule.splitting_rule_type = consecutive_splitting_rule_json_obj[
                                "splittingRuleType"]
                            consecutive_splitting_rule.parent_splitting_rule = splitting_rule
                            consecutive_splitting_rule.sort_order = consecutive_splitting_rule_json_obj[
                                "sortOrder"]
                            consecutive_splitting_rule.save()

                            for consecutive_splitting_condition_json_obj in consecutive_splitting_rule_json_obj["splittingConditions"]:
                                consecutive_splitting_condition = SplittingCondition()
                                consecutive_splitting_condition.rule = r
                                consecutive_splitting_condition.splitting_rule = consecutive_splitting_rule
                                consecutive_splitting_condition.operator = consecutive_splitting_condition_json_obj[
                                    "operator"]
                                consecutive_splitting_condition.value = consecutive_splitting_condition_json_obj[
                                    "value"]
                                consecutive_splitting_condition.sort_order = consecutive_splitting_condition_json_obj[
                                    "sortOrder"]
                                consecutive_splitting_condition.save()

                chatbot = ChatBot()
                chatbot.guid = parser_json_obj["chatbot"]["guid"]
                chatbot.parser = parser
                chatbot.chatbot_type = parser_json_obj["chatbot"]["chatbotType"]
                chatbot.open_ai_resource_name = parser_json_obj["chatbot"]["openAiResourceName"]
                chatbot.open_ai_api_key = parser_json_obj["chatbot"]["openAiApiKey"]
                chatbot.open_ai_default_question = parser_json_obj["chatbot"]["openAiDefaultQuestion"]
                chatbot.save()

                open_ai = OpenAI()
                open_ai.guid = parser_json_obj["openAi"]["guid"]
                open_ai.parser = parser
                open_ai.enabled = parser_json_obj["openAi"]["enabled"]
                open_ai.open_ai_resource_name = parser_json_obj["openAi"]["openAiResourceName"]
                open_ai.open_ai_api_key = parser_json_obj["openAi"]["openAiApiKey"]
                open_ai.save()

                for postprocessing_json_obj in parser_json_obj["postprocessings"]:
                    pp = PostProcessing(
                        guid=postprocessing_json_obj["guid"],
                        name=postprocessing_json_obj["name"],
                        post_processing_type=postprocessing_json_obj["postProcessingType"],
                        parser=parser,
                        redaction_regex=postprocessing_json_obj["redactionRegex"],
                        step=postprocessing_json_obj["step"]
                    )
                    pp.save()

                for integration_json_obj in parser_json_obj["integrations"]:
                    integration = Integration()
                    integration.integration_type = integration_json_obj["integrationType"]
                    integration.name = integration_json_obj["name"]
                    integration.parser = parser
                    integration.xml_path = integration_json_obj["xmlPath"]
                    integration.template = integration_json_obj["template"]
                    integration.pdf_integration_type = integration_json_obj["pdfIntegrationType"]
                    integration.pre_processing = integration_json_obj["preProcessing"]
                    integration.post_processing = integration_json_obj["postProcessing"]
                    integration.pdf_path = integration_json_obj["pdfPath"]
                    integration.interval_seconds = integration_json_obj["intervalSeconds"]
                    integration.next_run_time = integration_json_obj["nextRunTime"]
                    integration.activated = integration_json_obj["activated"]
                    integration.save()

            return Response({}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "ERROR", "detail": str(e)}, status=400)

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
            url_path='documents/(?P<document_id>[^/.]+)/pages/(?P<page_num>[^/.]+)/ask_chatbot')
    def ask_openai_about_pdf_content(self, request, pk, document_id, page_num, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(parser, document)

        chatbot = ChatBot.objects.get(parser_id=parser.id)

        question = request.data["question"]

        if question == "":
            return Response("Please ask me with meaningful questions.", status=200)

        if chatbot.chatbot_type == ChatBotType.OPEN_AI.value:

            content_to_be_sent_to_openai = "\n".join(
                document_parser.extract_all_text_in_all_pages())

            content_to_be_sent_to_openai = re.sub(
                ' +', '\n', content_to_be_sent_to_openai)

            try:

                headers = {
                    "Content-Type": "application/json",
                    "api-key": chatbot.open_ai_api_key
                }
                open_ai_content = question + " Please return in JSON format.\nInput: " + \
                    content_to_be_sent_to_openai
                json_data = {
                    "messages": [{"role": "user", "content": open_ai_content}],
                    "temperature": 0.2
                }

                response = requests.post('https://' + chatbot.open_ai_resource_name + '.openai.azure.com/openai/deployments/' + chatbot.open_ai_deployment + '/chat/completions?api-version=2023-05-15',
                                         data=json.dumps(json_data), headers=headers)
                if response.status_code == 400:
                    raise Exception(response.json()["error"]["message"])
                try:
                    s = response.json()["choices"][0]["message"]['content'].replace(
                        "Output:", "")
                    while True:
                        try:
                            # try to parse...
                            response_dict = json.loads(s)
                            break                    # parsing worked -> exit loop
                        except Exception as e:
                            # "Expecting , delimiter: line 34 column 54 (char 1158)"
                            # position of unexpected character after '"'
                            unexp = int(re.findall(
                                r'\(char (\d+)\)', str(e))[0])
                            # position of unescaped '"' before that
                            second_unesc = s.rfind(r'"', 0, unexp)
                            first_unesc = s.rfind(r'"', 0, second_unesc)
                            s = s[:first_unesc] + s[second_unesc+3:]

                except:
                    print(traceback.format_exc())
                    response_dict = {
                        "Message": "Encountered errors. Please try again or contact system administrator."
                    }

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

                return StreamingHttpResponse(
                    json.dumps(response_dict), status=200,
                    content_type='text/event-stream')

            except Exception as e:
                print(traceback.format_exc())
                return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

        elif chatbot.chatbot_type == ChatBotType.ON_PREMISE_AI.value:

            try:

                content_to_be_sent_to_openai = "\n".join(
                    document_parser.extract_all_text_in_all_pages())
                chatbot_content = question + " Please return in JSON format.\nInput: " + \
                    content_to_be_sent_to_openai

                def generate_response(content):
                    s = requests.Session()
                    headers = {}
                    payload = {
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": content}],
                        "stream": True,
                        "temperature": 0.7
                    }
                    with s.post(chatbot.base_url,
                                headers=headers,
                                json=payload,
                                stream=True) as resp:

                        for line in resp.iter_lines():
                            if line:
                                try:
                                    line = line.decode("utf-8")
                                    if line.startswith("data: "):
                                        line = line.replace('data: ', '', 1)
                                    print(line)
                                    if line == None:
                                        continue
                                    json_line = json.loads(line)
                                    data = json_line["choices"][0]["delta"]["content"]
                                    yield data
                                except:
                                    print(traceback.format_exc())
                                    pass

                return StreamingHttpResponse(
                    generate_response(chatbot_content), status=200, content_type='text/event-stream')

            except Exception as e:
                print(traceback.format_exc())
                pass
