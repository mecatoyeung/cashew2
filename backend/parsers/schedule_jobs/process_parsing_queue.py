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
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from parsers.models.rule import Rule
from backend.settings import MEDIA_URL
from parsers.helpers.document_parser import DocumentParser
import sys
import os
from pathlib import Path
import json

from ..helpers.rule_extractor import RuleExtractor
from ..helpers.stream_processor import StreamProcessor


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
        parser = queue_job.parser
        document = queue_job.document

        # Mark the job as in progress
        queue_job.queue_class = QueueClass.PARSING.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        # Do the job
        rules = Rule.objects.filter(parser_id=parser.id)
        parsed_result = []
        document_parser = DocumentParser(parser, document)
        for rule in rules:
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

        queue_job.parsed_result = json.dumps(parsed_result)

        # Mark the job as completed
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.POST_PROCESSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def parsing_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 1})
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 60 seconds
    scheduler.add_job(process_parsing_queue_job, 'interval',
                      seconds=5, name='process_parsing_queue', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Processing Parsing Queue", file=sys.stdout)
