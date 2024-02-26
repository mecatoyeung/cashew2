import uuid
from datetime import datetime
from io import BytesIO
import sys
import os
import re
from pathlib import Path
import shutil
import traceback

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
from parsers.models.document_type import DocumentType
from parsers.models.document_extension import DocumentExtension
from parsers.models.document_page import DocumentPage
from parsers.models.pre_processing import PreProcessing
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from parsers.models.chatbot_type import ChatBotType
from parsers.models.splitting import Splitting
from parsers.models.splitting_rule import SplittingRule
from parsers.models.splitting_rule_type import SplittingRuleType
from parsers.models.consecutive_page_splitting_rule import ConsecutivePageSplittingRule
from parsers.models.last_page_splitting_rule import LastPageSplittingRule
from parsers.models.rule import Rule
from parsers.models.splitting_operator_type import SplittingOperatorType

from parsers.serializers.document import DocumentUploadSerializer

from parsers.helpers.create_queue_when_upload_document import create_queue_when_upload_document
from parsers.helpers.parse_pdf_to_xml import parse_pdf_to_xml
from parsers.helpers.document_parser import DocumentParser
from parsers.helpers.stream_processor import StreamProcessor

from parsers.schedule_jobs.process_parsing_queue import process_single_parsing_queue

from backend.settings import MEDIA_ROOT


def get_streamed_by_rule(rule_id, parsed_result):
    for r in parsed_result:
        if r["rule"]["id"] == rule_id:
            return r["streamed"]
    raise Exception("Cannot find streamed by rule from parsed result.")

def process_single_splitting_queue(queue_job):

    all_in_process_splitting_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.SPLITTING.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_splitting_queue_jobs.count() > 0:
        return
    
    # Mark the job as in progress
    queue_job.queue_class = QueueClass.SPLITTING.value
    queue_job.queue_status = QueueStatus.IN_PROGRESS.value
    queue_job.save()

    try:
        parser = queue_job.parser
        rules = Rule.objects.filter(parser_id=parser.id).all()
        document = queue_job.document
        document_pages = document.document_pages.all()
        if Splitting.objects.filter(parser_id=parser.id).count() > 0:

            # splitting = Splitting.objects.prefetch_related("").get(parser_id=parser.id)
            splitting = Splitting.objects.prefetch_related(Prefetch(
                "splitting_rules",
                queryset=SplittingRule.objects.order_by("sort_order").filter(
                    splitting_rule_type=SplittingRuleType.FIRST_PAGE.value)
                .prefetch_related("splitting_conditions")
                .prefetch_related(
                    Prefetch("consecutive_page_splitting_rules",
                                queryset=ConsecutivePageSplittingRule.objects.
                                order_by("sort_order").prefetch_related("consecutive_page_splitting_conditions")))
                .prefetch_related(
                    Prefetch("last_page_splitting_rules",
                                queryset=LastPageSplittingRule.objects
                                .order_by("sort_order").prefetch_related("last_page_splitting_conditions"))))).get(parser_id=parser.id)

            if splitting.activated == False:
                queue_job.queue_class = QueueClass.PARSING.value
                queue_job.queue_status = QueueStatus.READY.value
                queue_job.save()
                return

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
                        elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                            if splitting_condition.value in streamed_rule_value:
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                            if not splitting_condition.value == streamed_rule_value:
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                            if not re.match(splitting_condition.value, streamed_rule_value):
                                first_page_conditions_passed = False
                        elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                            if re.match(splitting_condition.value, streamed_rule_value):
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

                            any_last_page_rules_passed = False
                            for last_page_splitting_rule in first_page_splitting_rule.last_page_splitting_rules.all():
                                last_page_conditions_passed = True
                                for splitting_condition in last_page_splitting_rule.last_page_splitting_conditions.all():
                                    streamed_rule_value = ' '.join(get_streamed_by_rule(
                                        splitting_condition.rule.id, parsed_result))
                                    if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                                        if not splitting_condition.value in streamed_rule_value:
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                                        if splitting_condition.value in streamed_rule_value:
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                                        if not splitting_condition.value == streamed_rule_value:
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                                        if not re.match(splitting_condition.value, streamed_rule_value):
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                                        if re.match(splitting_condition.value, streamed_rule_value):
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.IS_EMPTY.value:
                                        if not streamed_rule_value.strip() == "":
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.IS_NOT_EMPTY.value:
                                        if streamed_rule_value.strip() == "":
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.CHANGED.value:
                                        if page_num == 1:
                                            continue
                                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                                            splitting_condition.rule.id, previous_pages_parsed_result[page_num - 1]))
                                        if streamed_rule_value == previous_streamed_rule_value:
                                            last_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.NOT_CHANGED.value:
                                        if page_num == 1:
                                            continue
                                        previous_streamed_rule_value = ' '.join(get_streamed_by_rule(
                                            splitting_condition.rule.id, previous_pages_parsed_result[page_num - 1]))
                                        if not streamed_rule_value == previous_streamed_rule_value:
                                            last_page_conditions_passed = False

                                if last_page_conditions_passed:

                                    any_last_page_rules_passed = True
                                    break

                            if any_last_page_rules_passed:

                                document_page_index -= 1
                                page_num = document_page_index + 1
                                break

                            any_consecutive_page_rules_passed = False
                            for consecutive_page_splitting_rule in first_page_splitting_rule.consecutive_page_splitting_rules.all():
                                consecutive_page_conditions_passed = True
                                for splitting_condition in consecutive_page_splitting_rule.consecutive_page_splitting_conditions.all():
                                    streamed_rule_value = ' '.join(get_streamed_by_rule(
                                        splitting_condition.rule.id, parsed_result))
                                    if splitting_condition.operator == SplittingOperatorType.CONTAINS.value:
                                        if not splitting_condition.value in streamed_rule_value:
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.DOES_NOT_CONTAINS.value:
                                        if splitting_condition.value in streamed_rule_value:
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.EQUALS.value:
                                        if not splitting_condition.value == streamed_rule_value:
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.REGEX.value:
                                        if not re.match(splitting_condition.value, streamed_rule_value):
                                            consecutive_page_conditions_passed = False
                                    elif splitting_condition.operator == SplittingOperatorType.NOT_REGEX.value:
                                        if re.match(splitting_condition.value, streamed_rule_value):
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

                        """document_upload_serializer_data = {}"""

                        media_folder_path = MEDIA_ROOT
                        documents_path = os.path.join(
                            media_folder_path, "documents", str(document.guid))
                        searchable_pdf_path = os.path.join(
                            documents_path, 'ocred.pdf')

                        new_document = Document()
                        new_document.document_type = document.document_type
                        new_document.guid = str(uuid.uuid4())
                        new_document.filename_without_extension = document.filename_without_extension + \
                            "_pages_" + \
                            str(accumulated_page_nums[0]) + \
                            "-" + str(accumulated_page_nums[-1])
                        new_document.document_extension = DocumentExtension.PDF.value
                        new_document.extension = "pdf"
                        new_document.total_page_num = len(
                            accumulated_page_nums)
                        route_to_parser_id = first_page_splitting_rule.route_to_parser_id
                        new_document.parser_id = route_to_parser_id
                        new_document.last_modified_at = datetime.now()
                        new_parser_ocr = OCR.objects.get(
                            parser_id=route_to_parser_id)

                        new_documents_path = os.path.join(
                            media_folder_path, "documents", str(new_document.guid))
                        if not os.path.exists(new_documents_path):
                            os.makedirs(new_documents_path)

                        new_documents_path = os.path.join(
                            media_folder_path, "documents", str(new_document.guid))
                        new_searchable_pdf_path = os.path.join(
                            new_documents_path, 'source_file.pdf')
                        new_searchable_pdf_in_bytes = BytesIO()
                        searchable_pdf_f = open(searchable_pdf_path, "rb")
                        searchable_pdf = PdfReader(searchable_pdf_f)
                        pdf_writer = PdfWriter()
                        for page_num in accumulated_page_nums:
                            pdf_writer.add_page(
                                searchable_pdf.pages[page_num-1])
                        pdf_writer.write(new_searchable_pdf_in_bytes)
                        new_searchable_pdf_in_bytes.seek(0)
                        with open(new_searchable_pdf_path, "wb") as new_searchable_pdf_file:
                            new_searchable_pdf_file.write(
                                new_searchable_pdf_in_bytes.read())

                        searchable_pdf_f.close()

                        new_document.save()

                        new_document_page_num_counter = 0
                        for accumulated_page_num in accumulated_page_nums:
                            new_document_page_num_counter += 1
                            document_page = document_pages.get(
                                page_num=accumulated_page_num)
                            new_document_page = DocumentPage()
                            new_document_page.page_num = new_document_page_num_counter
                            new_document_page.width = document_page.width
                            new_document_page.height = document_page.height
                            new_document_page.xml = document_page.xml
                            new_document_page.document_id = new_document.id
                            new_document_page.preprocessed = False
                            if new_parser_ocr.ocr_type == OCRType.NO_OCR.value:
                                new_document_page.ocred = True
                            else:
                                new_document_page.ocred = False
                            new_document_page.postprocessed = False
                            new_document_page.chatbot_completed = False

                            preprocessings = PreProcessing.objects.order_by(
                                "-step").filter(parser_id=document.parser.id)

                            if len(preprocessings) == 0:
                                document_page_file_path = os.path.join(
                                    media_folder_path, "documents", str(document.guid), str(accumulated_page_num) + ".jpg")
                            else:
                                last_preprocessing = preprocessings[0]
                                document_page_file_path = os.path.join(
                                    media_folder_path, "documents", str(document.guid), "pre_processed-" + str(last_preprocessing.id), str(accumulated_page_num) + ".jpg")
                                if not os.path.exists(document_page_file_path):
                                    document_page_file_path = os.path.join(
                                        media_folder_path, "documents", str(document.guid), str(accumulated_page_num) + ".jpg")

                            new_document_page_image_file = os.path.join(
                                media_folder_path, "documents", new_document.guid, str(new_document_page_num_counter) + ".jpg")
                            shutil.copyfile(
                                document_page_file_path, new_document_page_image_file)

                            new_document_page.save()

                        create_queue_when_upload_document(new_document)

                        accumulated_page_nums = []

                        break

                document_page_index += 1
                page_num = document_page_index + 1

        # Mark the job as completed
        # queue_job.queue_status = QueueStatus.COMPLETED.value
        # queue_job.save()

        # Mark the job as complete
        queue_job.queue_class = QueueClass.PARSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_parsing_queue(queue_job)

    except Exception as e:
        print(traceback.format_exc())
        queue_job.queue_class = QueueClass.SPLITTING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()
        print(e)

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
        
        process_single_splitting_queue(queue_job)

def splitting_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "splitting_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_splitting_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Splitting Queue", file=sys.stdout)
