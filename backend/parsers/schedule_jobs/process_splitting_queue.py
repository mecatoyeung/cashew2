import uuid
from datetime import datetime
from io import BytesIO
import sys
import os
import re
from pathlib import Path

from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from django.core.files import File

from PyPDF2 import PdfWriter, PdfReader

from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.parser import Parser
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from parsers.models.chatbot_type import ChatBotType
from parsers.models.splitting import Splitting
from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_rule_type import SplittingRuleType
from parsers.models.rule import Rule
from parsers.models.splitting_operator_type import SplittingOperatorType
from parsers.models.document_type import DocumentType

from parsers.serializers.document import DocumentUploadSerializer

from ..helpers.parse_pdf_to_xml import parse_pdf_to_xml
from ..helpers.document_parser import DocumentParser
from ..helpers.stream_processor import StreamProcessor

from backend.settings import MEDIA_URL


def get_streamed_by_rule(rule_id, parsed_result):
    for r in parsed_result:
        if r["rule"]["id"] == rule_id:
            return r["streamed"]
    raise Exception("Cannot find streamed by rule from parsed result.")


def process_splitting_queue_job():
    all_ready_splitting_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .select_related("parser") \
        .prefetch_related(Prefetch(
            "parser",
            queryset=Parser.objects.select_related(
                "aichat"
            )
        )) \
        .filter(queue_class=QueueClass.SPLITTING.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_splitting_queue_jobs:
        parser = queue_job.parser
        rules = Rule.objects.filter(parser_id=parser.id).all()
        document = queue_job.document
        document_pages = document.document_pages.all()
        if Splitting.objects.filter(parser_id=parser.id).count() > 0:

            # splitting = Splitting.objects.prefetch_related("").get(parser_id=parser.id)
            splitting = Splitting.objects.prefetch_related(Prefetch(
                "splitting_rules",
                queryset=SplittingRule.objects.filter(
                    splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
                .prefetch_related("splitting_conditions")
                .prefetch_related(
                    Prefetch("consecutive_page_splitting_rules",
                             queryset=SplittingRule.objects.prefetch_related("splitting_conditions"))))).get(parser_id=parser.id)

            # Do the job
            accumulated_page_nums = []
            previous_pages_parsed_result = {}
            document_page_index = 0
            while document_page_index < len(document_pages):
                page_num = document_page_index + 1

                document_parser = DocumentParser(parser, document)

                parsed_result = []
                for rule in rules:
                    rule.pages = str(page_num)
                    extracted = document_parser.extract(rule)
                    stream_processor = StreamProcessor(rule)
                    processed_streams = stream_processor.process(extracted)

                    parsed_result.append({
                        "rule": {
                            "id": rule.id,
                            "name": rule.name,
                            "type": processed_streams[-1]["type"]
                        },
                        "extracted": extracted,
                        "streamed": processed_streams[-1]["data"]
                    })

                previous_pages_parsed_result[page_num] = parsed_result

                for first_page_splitting_rule in splitting.splitting_rules.all():
                    first_page_conditions_passed = True
                    for splitting_condition in first_page_splitting_rule.splitting_conditions.all():
                        streamed_rule_value = ' '.join(get_streamed_by_rule(
                            splitting_condition.rule.id, parsed_result))
                        if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                            if not splitting_condition.value in streamed_rule_value:
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                            if not splitting_condition.value == streamed_rule_value:
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                            if not re.match(splitting_condition.value, streamed_rule_value):
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                            if not streamed_rule_value.strip() == "":
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                            if streamed_rule_value.strip() == "":
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                            if page_num == 1:
                                continue
                            previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                                splitting_condition.rule.id,
                                previous_pages_parsed_result[page_num - 1]))
                            if streamed_rule_value == previous_streamed_rule_value:
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                            if page_num == 1:
                                continue
                            previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                                splitting_condition.rule.id, previous_pages_parsed_result[page_num - 1]))
                            if not streamed_rule_value == previous_streamed_rule_value:
                                first_page_conditions_passed = False

                    if first_page_conditions_passed:

                        accumulated_page_nums.append(page_num)

                        # if it is not the last page, identify consecutive pages also
                        while (document_page_index + 1) < len(document_pages):

                            document_page_index += 1
                            page_num = document_page_index + 1

                            parsed_result = []
                            for rule in rules:
                                rule.pages = str(page_num)
                                extracted = document_parser.extract(rule)
                                stream_processor = StreamProcessor(rule)
                                processed_streams = stream_processor.process(
                                    extracted)

                                parsed_result.append({
                                    "rule": {
                                        "id": rule.id,
                                        "name": rule.name,
                                        "type": processed_streams[-1]["type"]
                                    },
                                    "extracted": extracted,
                                    "streamed": processed_streams[-1]["data"]
                                })

                            previous_pages_parsed_result[page_num] = parsed_result

                            any_consecutive_page_rules_passed = False
                            for consecutive_page_splitting_rule in first_page_splitting_rule.consecutive_page_splitting_rules.all():
                                consecutive_page_conditions_passed = True
                                for splitting_condition in consecutive_page_splitting_rule.splitting_conditions.all():
                                    streamed_rule_value = ' '.join(get_streamed_by_rule(
                                        splitting_condition.rule.id, parsed_result))
                                    if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                                        if not splitting_condition.value in streamed_rule_value:
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                                        if not splitting_condition.value == streamed_rule_value:
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                                        if not re.match(splitting_condition.value, streamed_rule_value):
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                                        if not streamed_rule_value.strip() == "":
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                                        if streamed_rule_value.strip() == "":
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                                        if page_num == 1:
                                            continue
                                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                                            splitting_condition.rule.id, previous_pages_parsed_result[page_num - 1]))
                                        if streamed_rule_value == previous_streamed_rule_value:
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                                        if page_num == 1:
                                            continue
                                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                                            splitting_condition.rule.id, previous_pages_parsed_result[page_num - 1]))
                                        if not streamed_rule_value == previous_streamed_rule_value:
                                            consecutive_page_conditions_passed = False

                                if consecutive_page_conditions_passed:

                                    any_consecutive_page_rules_passed = True
                                    break

                            if any_consecutive_page_rules_passed:

                                accumulated_page_nums.append(page_num)

                            # if no consecutive_page passed, decrement page_index, and restart finding accumulated pages
                            else:

                                document_page_index -= 1
                                page_num = document_page_index + 1
                                break

                    if first_page_conditions_passed:

                        document_upload_serializer_data = {}

                        media_folder_path = MEDIA_URL
                        documents_path = os.path.join(
                            media_folder_path, "documents", str(document.guid))

                        searchable_pdf_path = os.path.join(
                            documents_path, 'ocred.pdf')

                        new_searchable_pdf_in_bytes = BytesIO()
                        searchable_pdf = PdfReader(
                            open(searchable_pdf_path, "rb"))
                        pdf_writer = PdfWriter()
                        for page_num in accumulated_page_nums:
                            pdf_writer.add_page(
                                searchable_pdf.pages[page_num-1])
                        pdf_writer.write(new_searchable_pdf_in_bytes)
                        new_searchable_pdf_in_bytes.seek(0)

                        filename_without_extension = document.filename_without_extension + \
                            "_pages_" + \
                            str(accumulated_page_nums[0]) + \
                            "-" + str(accumulated_page_nums[-1])

                        document_upload_serializer_data["file"] = File(
                            new_searchable_pdf_in_bytes, filename_without_extension + ".pdf")

                        route_to_parser_id = first_page_splitting_rule.route_to_parser_id
                        document_upload_serializer_data["parser"] = route_to_parser_id

                        document_upload_serializer_data["guid"] = str(
                            uuid.uuid4())

                        document_upload_serializer_data["document_type"] = DocumentType.PDF.value

                        document_upload_serializer_data["filename_without_extension"] = filename_without_extension
                        document_upload_serializer_data["extension"] = "pdf"

                        document_upload_serializer = DocumentUploadSerializer(
                            data=document_upload_serializer_data)

                        if document_upload_serializer.is_valid():
                            document_upload_serializer.save()

                        accumulated_page_nums = []

                document_page_index += 1
                page_num = document_page_index + 1

        # Mark the job as completed
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        # Mark the job as preprocessing in progress
        if parser.chatbot.chatbot_type == ChatBotType.NO_CHATBOT.value:
            queue_job.queue_class = QueueClass.AICHAT.value
        else:
            queue_job.queue_class = QueueClass.PARSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def splitting_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 1})
    # scheduler.add_jobstore(DjangoJobStore(), "splitting_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_splitting_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Splitting Queue", file=sys.stdout)
