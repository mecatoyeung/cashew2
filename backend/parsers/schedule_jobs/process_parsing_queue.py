import sys
import os
from pathlib import Path
import json
import traceback
from datetime import datetime
from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from parsers.models.rule import Rule
from parsers.models.rule_type import RuleType
from parsers.helpers.document_parser import DocumentParser

from parsers.schedule_jobs.process_postprocessing_queue import process_single_postprocessing_queue

from ..helpers.rule_extractor import RuleExtractor
from ..helpers.stream_processor import StreamProcessor

def process_single_parsing_queue(queue_job):
    
    all_in_process_parsing_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.PARSING.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_parsing_queue_jobs.count() > 0:
        return

    # Mark the job as in progress
    queue_job.queue_class = QueueClass.PARSING.value
    queue_job.queue_status = QueueStatus.IN_PROGRESS.value
    queue_job.save()

    try:

        parser = queue_job.parser
        document = Document.objects.prefetch_related(Prefetch("document_pages", queryset=DocumentPage.objects.order_by('page_num'))).get(pk=queue_job.document_id)

        # Do the job
        rules = Rule.objects.filter(parser_id=parser.id)
        parsed_result = []
        document_parser = DocumentParser(parser, document)
        for rule in rules:
            extracted = document_parser.extract(rule)
            stream_processor = StreamProcessor(rule)
            processed_streams = stream_processor.process(extracted)

            if rule.rule_type == RuleType.TEXTFIELD.value or \
                rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value or \
                rule.rule_type == RuleType.BARCODE.value or \
                    rule.rule_type == RuleType.ACROBAT_FORM.value:
                if processed_streams[-1]["data"] == None:
                    processed_streams[-1]["data"] = ""
                else:
                    processed_streams[-1]["data"] = " ".join(
                        processed_streams[-1]["data"])

            parsed_result.append({
                "rule": {
                    "id": rule.id,
                    "name": rule.name,
                    "type": processed_streams[-1]["type"]
                },
                "extracted": extracted,
                "streamed": processed_streams[-1]["data"]
            })

        queue_job.parsed_result = json.dumps(parsed_result)

        # Update last modified at
        document.last_modified_at = datetime.now()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.POST_PROCESSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_postprocessing_queue(queue_job)

    except Exception as e:
        queue_job.queue_class = QueueClass.PARSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()
        traceback.print_exc()

def process_parsing_queue_job():

    all_ready_parsing_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .filter(queue_class=QueueClass.PARSING.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_parsing_queue_jobs:

        process_single_parsing_queue(queue_job)


def parsing_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "parsing_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_parsing_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Parsing Queue", file=sys.stdout)
