import re
import decimal
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import traceback

from functools import reduce
import operator

from rest_framework import (
    viewsets,
)

from django.db.models import Prefetch
from django.db.models import Q

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import StreamingHttpResponse
from rest_framework.authentication import SessionAuthentication

import requests
import json

from django.contrib.auth.models import User, Group

from parsers.models.parser import Parser
from parsers.models.rule import Rule
from parsers.models.stream import Stream
from parsers.models.table_column_separator import TableColumnSeparator
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.document import Document
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
from parsers.models.consecutive_page_splitting_rule import ConsecutivePageSplittingRule
from parsers.models.last_page_splitting_rule import LastPageSplittingRule
from parsers.models.splitting_condition import SplittingCondition
from parsers.models.consecutive_page_splitting_condition import ConsecutivePageSplittingCondition
from parsers.models.last_page_splitting_condition import LastPageSplittingCondition
from parsers.models.post_processing import PostProcessing

from parsers.serializers.parser import ParserSerializer,\
    ParserCreateSerializer,\
    ParserRetrieveSerializer,\
    ParserListSerializer,\
    ParserUpdateSerializer,\
    ParserDeleteSerializer,\
    ParserExportSerializer,\
    ParserImportSerializer,\
    ProtectedParserSerializer
from parsers.serializers.rule import RuleSerializer
from parsers.serializers.source import SourceSerializer
from parsers.serializers.integration import IntegrationSerializer
from parsers.serializers.splitting import SplittingSerializer

from core.permissions.parser_management import ParserManagementPermission

from parsers.helpers.document_parser import DocumentParser

from parsers.schedule_jobs.get_open_ai_metrics import get_single_parser_open_ai_metrics

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class ParserViewSet(viewsets.ModelViewSet):
    """ View for manage parser APIs. """
    serializer_class = ParserSerializer
    queryset = Parser.objects.all()
    authentication_classes = [
        TokenAuthentication]
    permission_classes = [IsAuthenticated, ParserManagementPermission]

    def _params_to_ints(self, qs):
        """ Convert a list of strings to integers. """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve parsers for authenticated user. """
        queryset = self.queryset

        if self.action == "retrieve":

            queryset = queryset\
                .select_related("owner")\
                .select_related("ocr") \
                .select_related("chatbot") \
                .select_related("open_ai") \
                .select_related("open_ai_metrics_key") \
                .select_related("splitting") \
                .prefetch_related('sources') \
                .prefetch_related('rules') \
                .prefetch_related('rules__table_column_separators') \
                .prefetch_related('rules__streams') \
                .prefetch_related("preprocessings") \
                .prefetch_related("integrations") \
                .prefetch_related("postprocessings") \
                .prefetch_related(Prefetch("splitting__splitting_rules",
                                           queryset=SplittingRule.objects.prefetch_related("splitting_conditions").filter(
                                               splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
                                           .prefetch_related(Prefetch("consecutive_page_splitting_rules",
                                                                      queryset=ConsecutivePageSplittingRule.objects.prefetch_related("consecutive_page_splitting_conditions")))
                                           .prefetch_related(Prefetch("last_page_splitting_rules",
                                                                      queryset=LastPageSplittingRule.objects.prefetch_related("last_page_splitting_conditions")))
                                           ))\
                .prefetch_related("permitted_users")\
                .prefetch_related("permitted_groups")
            
            if not self.request.user.is_superuser:
            
                queryset = queryset.filter(Q(permitted_users=self.request.user) | Q(permitted_groups__pk__in=self.request.user.groups.values_list('id', flat=True)) | Q(owner=self.request.user))
            
            return queryset
        
        else:

            queryset = queryset.prefetch_related("rules") \
                .select_related("owner")\
                .select_related("chatbot") \
                .select_related("ocr") \
                .order_by('id').distinct()

            if not self.request.user.is_superuser:
                queryset = queryset.filter(Q(permitted_users=self.request.user) | Q(permitted_groups__pk__in=self.request.user.groups.values_list('id', flat=True)) | Q(owner=self.request.user))

            return queryset

    def get_serializer_class(self):
        """ Return the serializer class for request """
        if self.action == 'create':
            return ParserCreateSerializer
        elif self.action == "retrieve":
            if self.request.user.is_superuser:
                return ParserRetrieveSerializer
            else:
                if self.request.user.is_superuser:
                    return ParserRetrieveSerializer
                if self.request.user.has_perm("parsers.cashew_parser_management"):
                    obj = self.get_object()
                    if obj.owner.id == self.request.user.id:
                        return ParserRetrieveSerializer
                    for permitted_user in obj.permitted_users.all():
                        if permitted_user.id == self.request.user.id:
                            return ParserRetrieveSerializer
                    for permitted_group in obj.permitted_groups.all():
                        users = User.objects.filter(groups__id=permitted_group.id)
                        for user in users:
                            if user.id == self.request.user.id:
                                return ParserRetrieveSerializer
            return ProtectedParserSerializer
        elif self.action == 'list':
            return ParserListSerializer
        elif self.action == 'update':
            return ParserUpdateSerializer
        elif self.action == 'delete':
            return ParserDeleteSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new parser. """
        serializer.save(owner=self.request.user)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            instance = self.get_object()
            queues_count = Queue.objects.filter(parser_id=pk, queue_status=QueueStatus.IN_PROGRESS.value).count()
            if queues_count > 0:
                raise Exception("Delete cannot be completed. Please make sure there is no queue in progress in this parser.")
            self.perform_destroy(instance)
        except Exception as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
                         queryset=ConsecutivePageSplittingRule.objects.prefetch_related("consecutive_page_splitting_conditions")))
            .prefetch_related(
                Prefetch("last_page_splitting_rules",
                         queryset=LastPageSplittingRule.objects.prefetch_related("last_page_splitting_conditions"))))).get(parser_id=pk)

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
                    .prefetch_related(Prefetch('rules', queryset=Rule.objects.prefetch_related(
                        Prefetch('streams', queryset=Stream.objects.all())
                    ))) \
                    .prefetch_related('rules__table_column_separators') \
                    .prefetch_related("preprocessings") \
                    .prefetch_related("integrations") \
                    .prefetch_related("postprocessings") \
                    .select_related("splitting") \
                    .prefetch_related(Prefetch("splitting__splitting_rules", queryset=SplittingRule.objects.filter(
                        splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
                        .prefetch_related("splitting_conditions")
                        .prefetch_related(Prefetch("consecutive_page_splitting_rules",
                                                   queryset=ConsecutivePageSplittingRule.objects.prefetch_related("consecutive_page_splitting_conditions")))
                        .prefetch_related(Prefetch("last_page_splitting_rules",
                                                   queryset=LastPageSplittingRule.objects.prefetch_related("consecutive_page_splitting_conditions")))
                    )) \
                    .prefetch_related("permitted_users")\
                    .prefetch_related("permitted_groups")\
                    .get(pk=parser_id)

                serializer = ParserExportSerializer(parser)
                data.append(serializer.data)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "ERROR", "detail": str(e)}, status=400)
        
    
    @action(detail=True,
            methods=['GET'],
            name='Get All Texts',
            url_path='documents/(?P<document_id>[^/.]+)/extract_all_text')
    def extract_all_text(self, request, pk, document_id, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(parser, document)

        result = document_parser.extract_all_text_in_all_pages()

        return Response(result, status=200)
    
    @action(detail=True,
            methods=['POST'],
            name='Ask OpenAI about PDF content',
            url_path='documents/(?P<document_id>[^/.]+)/ask_chatbot')
    def ask_openai_about_pdf_content(self, request, pk, document_id, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(parser, document)

        chatbot = ChatBot.objects.get(parser_id=parser.id)

        question = request.data["question"]

        if question == "":
            return Response("Please ask me with meaningful questions.", status=200)
        
        if chatbot.chatbot_type == ChatBotType.NO_CHATBOT.value:

            response_dict = {
                    "Message": "You did not define any chat bot in the settings. Please define Chat Bot in the settings and try again."
                }
            return StreamingHttpResponse(
                    json.dumps(response_dict), status=200,
                    content_type='text/event-stream')

        elif chatbot.chatbot_type == ChatBotType.OPEN_AI.value:

            content_to_be_sent_to_openai = "\n".join(
                document_parser.extract_all_text_in_all_pages())

            content_to_be_sent_to_openai = re.sub(
                ' +', '\n', content_to_be_sent_to_openai)

            try:

                headers = {
                    "Content-Type": "application/json",
                    "api-key": chatbot.open_ai_api_key
                }
                open_ai_content = question + " Please control the output in depth of 3 only. Please return in JSON format.\nInput: " + \
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
                    return Response(response_dict, status.HTTP_400_BAD_REQUEST)

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
                response_dict = {
                        "Message": "Encountered errors. Please try again or contact system administrator."
                    }
                return Response(response_dict, status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['GET'],
            name='Get All Texts in One Page',
            url_path='documents/(?P<document_id>[^/.]+)/pages/(?P<page_num>[^/.]+)/extract_all_text')
    def extract_all_text_in_one_page(self, request, pk, document_id, page_num, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))

        document = Document.objects.get(id=document_id)

        document_parser = DocumentParser(parser, document)

        result = document_parser.extract_all_text_in_one_page(page_num)

        return Response(result, status=200)

    @action(detail=False,
            methods=['GET'],
            name='Open AI Metrics',
            url_path='(?P<pk>[^/.]+)/open_ai_metrics')
    def metrics(self, request, pk, *args, **kwargs):

        parser = Parser \
                    .objects \
                    .select_related("open_ai_metrics") \
                    .get(pk=pk)
        
        tenant_id = parser.open_ai_metrics.open_ai_metrics_tenant_id
        client_id = parser.open_ai_metrics.open_ai_metrics_client_id
        client_secret = parser.open_ai_metrics.open_ai_metrics_client_secret
        resource = "https://management.core.windows.net/"

        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": resource,
        }

        token_response = requests.post(token_url, data=payload)

        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            print(f"Access token: {access_token}")

            subscription_id = parser.open_ai_metrics.open_ai_metrics_subscription_id
            open_ai_service_name = parser.open_ai_metrics.open_ai_metrics_service_name

            metrics_headers = {
                'Authorization': 'Bearer ' + access_token,
            }

            current_datetime = datetime.now()
            one_month_before_datetime = current_datetime - relativedelta(months=1)
            timespan = one_month_before_datetime.strftime("%Y-%m-%dT00:00:00Z/") + current_datetime.strftime("%Y-%m-%dT00:00:00Z")

            generated_tokens_metrics_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/Cashew/providers/Microsoft.CognitiveServices/accounts/{open_ai_service_name}/providers/microsoft.insights/metrics?api-version=2023-10-01&metricnames=GeneratedTokens&interval=P1D&aggregation=Total&timespan={timespan}"
            generated_tokens_metrics_response = requests.get(generated_tokens_metrics_url, headers=metrics_headers)
            generated_tokens_metrics_data = generated_tokens_metrics_response.json()

            processed_tokens_metrics_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/Cashew/providers/Microsoft.CognitiveServices/accounts/{open_ai_service_name}/providers/microsoft.insights/metrics?api-version=2023-10-01&metricnames=ProcessedPromptTokens&interval=P1D&aggregation=Total&timespan={timespan}"
            processed_tokens_metrics_response = requests.get(processed_tokens_metrics_url, headers=metrics_headers)
            processed_tokens_metrics_data = processed_tokens_metrics_response.json()

            processed_tokens_pricing = 0.0005
            generated_tokens_pricing = 0.0015
            processed_tokens_data = processed_tokens_metrics_data['value'][0]['timeseries'][0]['data']
            generated_tokens_data = generated_tokens_metrics_data['value'][0]['timeseries'][0]['data']
            pricing_metrics_data = []
            for i in range(len(generated_tokens_data)):
                price = decimal.Decimal(processed_tokens_data[i]['total'] * processed_tokens_pricing / 1000 + generated_tokens_data[i]['total'] * generated_tokens_pricing / 1000)
                rounded_price = decimal.Decimal(price).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
                remained_value = price - rounded_price
                if remained_value > 0:
                    rounded_price += decimal.Decimal(0.01)
                pricing_metrics_data.append({
                    "timeStamp": generated_tokens_data[i]["timeStamp"],
                    "total": rounded_price
                })

            merged_metrics_data = []
            for i in range(len(generated_tokens_data)):
                merged_metrics_data.append({
                    "timeStamp": generated_tokens_data[i]["timeStamp"],
                    "processed_tokens": processed_tokens_data[i]["total"],
                    "generated_tokens": generated_tokens_data[i]["total"],
                    "price": pricing_metrics_data[i]["total"]
                })

            return Response(merged_metrics_data, status=status.HTTP_200_OK)
        

    

#class ParserGenericViewSet(viewsets.GenericViewSet):

    #authentication_classes = [
    #    TokenAuthentication]
    #permission_classes = [IsAuthenticated, ParserManagementPermission]

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
                parser.type = parser_json_obj["type"]
                parser.name = parser_json_obj["name"]
                parser.last_modified_at = datetime.now()
                parser.total_num_of_pages_processed = parser_json_obj["totalNumOfPagesProcessed"]
                parser.pdf_to_image_dpi = parser_json_obj["pdfToImageDpi"]
                parser.assumed_text_width = parser_json_obj["assumedTextWidth"]
                parser.assumed_text_height = parser_json_obj["assumedTextHeight"]
                parser.same_line_acceptance_range = parser_json_obj["sameLineAcceptanceRange"]
                parser.same_column_acceptance_range = parser_json_obj["sameColumnAcceptanceRange"]
                parser.owner = request.user
                
                parser.save()
                
                parser.permitted_users.set(parser_json_obj["permittedUsers"])
                parser.permitted_groups.set(parser_json_obj["permittedGroups"])
                
                parser.save()

                if splitting_parser_counter < len(json_obj):
                    splitting_parser_ids_mapping[parser_json_obj["id"]] = parser.id

                for source_json_obj in parser_json_obj["sources"]:
                    s = Source(
                        name=source_json_obj["name"],
                        parser_id=parser.id,
                        source_path=source_json_obj["sourcePath"],
                        interval_seconds=source_json_obj["intervalSeconds"],
                        next_run_time=timezone.now(),
                        is_running = False,
                        activated=source_json_obj["activated"],
                    )
                    s.save()

                for preprocessing_json_obj in parser_json_obj["preprocessings"]:
                    pp = PreProcessing(
                        pre_processing_type=preprocessing_json_obj["preProcessingType"],
                        name=preprocessing_json_obj["name"],
                        step=preprocessing_json_obj["step"],
                        parser=parser,
                        orientation_detection_tesseract_confidence_above=preprocessing_json_obj["orientationDetectionTesseractConfidenceAbove"],
                        threshold_binarization=preprocessing_json_obj["thresholdBinarization"],
                        debug=preprocessing_json_obj["debug"],
                    )
                    pp.save()

                ocr = OCR()
                ocr.parser = parser
                ocr.ocr_type = parser_json_obj["ocr"]["ocrType"]
                ocr.ocr_image_layer_type = parser_json_obj["ocr"]["ocrImageLayerType"]
                ocr.image_layer_preprocessing = parser_json_obj["ocr"]["imageLayerPreprocessing"]
                ocr.google_vision_ocr_api_key = parser_json_obj["ocr"]["googleVisionOcrApiKey"]
                ocr.paddle_ocr_language = parser_json_obj["ocr"]["paddleOcrLanguage"]
                ocr.omnipage_ocr_language = parser_json_obj["ocr"]["omnipageOcrLanguage"]
                ocr.apple_vision_ocr_language = parser_json_obj["ocr"]["appleVisionOcrLanguage"]
                ocr.detect_searchable = parser_json_obj["ocr"]["detectSearchable"]
                ocr.debug = parser_json_obj["ocr"]["debug"]
                ocr.save()

                for rule_json_obj in parser_json_obj["rules"]:
                    try:
                        anchor_document = Document.objects.get(pk=rule_json_obj["anchorDocumentId"])
                    except:
                        anchor_document = None
                    r = Rule(
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
                        anchor_document=anchor_document,
                        anchor_page_num=rule_json_obj["anchorPageNum"],
                        acrobat_form_field=rule_json_obj["acrobatFormField"],
                        depends_on_id=rule_json_obj["dependsOn"],
                        last_modified_at=datetime.now()
                    )
                    r.save()
                    for table_column_separator_json_obj in rule_json_obj["tableColumnSeparators"]:
                        table_column_separator = TableColumnSeparator(
                            rule=r.id,
                            x=table_column_separator_json_obj["x"]
                        )
                        table_column_separator.save()

                    for stream_json_obj in rule_json_obj["streams"]:
                        stream = Stream(
                            rule=r,
                            step=stream_json_obj["step"],
                            type=stream_json_obj["type"],
                            stream_class=stream_json_obj["streamClass"],
                            text=stream_json_obj["text"],
                            regex=stream_json_obj["regex"],
                            join_string=stream_json_obj["joinString"],
                            extract_first_n_lines=stream_json_obj["extractFirstNLines"],
                            extract_nth_lines=stream_json_obj["extractNthLines"],
                            combine_first_n_lines=stream_json_obj["combineFirstNLines"],
                            convert_to_table_by_specify_headers=stream_json_obj["convertToTableBySpecifyHeaders"],
                            open_ai_question=stream_json_obj["openAiQuestion"],
                            col_index=stream_json_obj["colIndex"],
                            col_indexes=stream_json_obj["colIndexes"],
                            remove_matched_row_also=stream_json_obj["removeMatchedRowAlso"],
                            unpivot_column_index=stream_json_obj["unpivotColumnIndex"],
                            unpivot_newline_char=stream_json_obj["unpivotNewlineChar"],
                            unpivot_property_assign_char=stream_json_obj["unpivotPropertyAssignChar"],
                            json_extract_code=stream_json_obj["jsonExtractCode"],
                            current_page_regex=stream_json_obj["currentPageRegex"],
                            last_page_regex=stream_json_obj["lastPageRegex"]
                        )
                        stream.save()

                if not parser_json_obj["splitting"] == None:

                    splitting = Splitting()
                    splitting.parser = parser
                    splitting.split_type = parser_json_obj["splitting"]["splitType"]
                    splitting.no_first_page_rules_matched_operation_type = parser_json_obj["splitting"]["noFirstPageRulesMatchedOperationType"]
                    splitting.no_first_page_rules_matched_route_to_parser = parser_json_obj["splitting"]["noFirstPageRulesMatchedRouteToParser"]
                    splitting.activated = parser_json_obj["splitting"]["activated"]
                    splitting.save()

                    for splitting_rule_json_obj in parser_json_obj["splitting"]["splittingRules"]:
                        splitting_rule = SplittingRule()
                        splitting_rule.splitting_rule_type = splitting_rule_json_obj[
                            "splittingRuleType"]
                        splitting_rule.splitting = splitting
                        splitting_rule.route_to_parser = Parser.objects.get(pk=splitting_parser_ids_mapping[
                            splitting_rule_json_obj["routeToParser"]])
                        splitting_rule.sort_order = splitting_rule_json_obj["sortOrder"]
                        splitting_rule.save()

                        for splitting_condition_json_obj in splitting_rule_json_obj["splittingConditions"]:
                            splitting_condition = SplittingCondition()
                            splitting_condition.splitting_rule = splitting_rule
                            splitting_condition.rule = r
                            splitting_condition.operator = splitting_condition_json_obj["operator"]
                            splitting_condition.value = splitting_condition_json_obj["value"]
                            splitting_condition.sort_order = splitting_condition_json_obj["sortOrder"]
                            splitting_condition.save()

                        for consecutive_page_splitting_rule_json_obj in splitting_rule_json_obj["consecutivePageSplittingRules"]:
                            consecutive_page_splitting_rule = ConsecutivePageSplittingRule()
                            consecutive_page_splitting_rule.consecutive_page_splitting_rule_type = consecutive_page_splitting_rule_json_obj[
                                "consecutivePageSplittingRuleType"]
                            consecutive_page_splitting_rule.parent_splitting_rule = splitting_rule
                            consecutive_page_splitting_rule.sort_order = consecutive_page_splitting_rule_json_obj[
                                "sortOrder"]
                            consecutive_page_splitting_rule.save()

                            for consecutive_page_splitting_condition_json_obj in consecutive_page_splitting_rule_json_obj["consecutivePageSplittingConditions"]:
                                consecutive_page_splitting_condition = ConsecutivePageSplittingCondition()
                                consecutive_page_splitting_condition.consecutive_page_splitting_rule = consecutive_page_splitting_rule
                                consecutive_page_splitting_condition.rule = r
                                consecutive_page_splitting_condition.operator = consecutive_page_splitting_condition_json_obj[
                                    "operator"]
                                consecutive_page_splitting_condition.value = consecutive_page_splitting_condition_json_obj[
                                    "value"]
                                consecutive_page_splitting_condition.sort_order = consecutive_page_splitting_condition_json_obj[
                                    "sortOrder"]
                                consecutive_page_splitting_condition.save()

                        for last_page_splitting_rule_json_obj in splitting_rule_json_obj["lastPageSplittingRules"]:
                            last_page_splitting_rule = LastPageSplittingRule()
                            last_page_splitting_rule.last_page_splitting_rule_type = last_page_splitting_rule_json_obj["lastPageSplittingRuleType"]
                            last_page_splitting_rule.parent_splitting_rule = splitting_rule
                            last_page_splitting_rule.sort_order = last_page_splitting_rule_json_obj[
                                "sortOrder"]
                            last_page_splitting_rule.save()

                            for last_page_splitting_condition_json_obj in last_page_splitting_rule_json_obj["lastPageSplittingConditions"]:
                                last_page_splitting_condition = LastPageSplittingCondition()
                                last_page_splitting_condition.last_page_splitting_rule = last_page_splitting_rule
                                last_page_splitting_condition.rule = r
                                last_page_splitting_condition.operator = last_page_splitting_condition[
                                    "operator"]
                                last_page_splitting_condition.value = last_page_splitting_condition_json_obj[
                                    "value"]
                                last_page_splitting_condition.sort_order = last_page_splitting_condition_json_obj[
                                    "sortOrder"]
                                last_page_splitting_condition.save()

                chatbot = ChatBot()
                chatbot.parser = parser
                chatbot.chatbot_type = parser_json_obj["chatbot"]["chatbotType"]
                chatbot.open_ai_resource_name = parser_json_obj["chatbot"]["openAiResourceName"]
                chatbot.open_ai_api_key = parser_json_obj["chatbot"]["openAiApiKey"]
                chatbot.open_ai_default_question = parser_json_obj["chatbot"]["openAiDefaultQuestion"]
                chatbot.open_ai_deployment = parser_json_obj["chatbot"]["openAiDeployment"]
                chatbot.base_url = parser_json_obj["chatbot"]["baseUrl"]
                chatbot.save()

                open_ai = OpenAI()
                open_ai.parser = parser
                open_ai.enabled = parser_json_obj["openAi"]["enabled"]
                open_ai.open_ai_resource_name = parser_json_obj["openAi"]["openAiResourceName"]
                open_ai.open_ai_deployment = parser_json_obj["openAi"]["openAiDeployment"]
                open_ai.open_ai_api_key = parser_json_obj["openAi"]["openAiApiKey"]
                open_ai.save()

                for postprocessing_json_obj in parser_json_obj["postprocessings"]:
                    pp = PostProcessing(
                        name=postprocessing_json_obj["name"],
                        parser=parser,
                        post_processing_type=postprocessing_json_obj["postProcessingType"],
                        step=postprocessing_json_obj["step"],
                        redaction_regex=postprocessing_json_obj["redactionRegex"]
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
            traceback.print_exc()
            return Response({"message": "ERROR", "detail": str(e)}, status=400)

    @action(detail=False,
            methods=['POST'],
            name='Update Statistic',
            url_path='(?P<pk>[^/.]+)/update_statistics')
    def get_rules(self, request, pk, *args, **kwargs):

        parser = Parser.objects.get(pk=pk)
        get_single_parser_open_ai_metrics(parser)

        return Response("Statistics has been updated", status=200)

    @action(detail=False,
            methods=['POST'],
            name='Transfer Owner',
            url_path='(?P<pk>[^/.]+)/transfer_owner/(?P<new_owner_id>[^/.]+)')
    def transfer_owner(self, request, pk, new_owner_id, *args, **kwargs):

        parser = Parser.objects.get(pk=int(pk))
        new_owner = User.objects.get(pk=new_owner_id)

        parser.owner = new_owner
        parser.save()

        return Response("Owner has been transferred", status=200)