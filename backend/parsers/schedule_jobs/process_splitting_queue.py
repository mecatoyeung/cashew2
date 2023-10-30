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
from backend.settings import MEDIA_URL
import sys
import os
from pathlib import Path
from ..helpers.parse_pdf_to_xml import parse_pdf_to_xml


def process_splitting_queue_job():
    all_ready_splitting_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .filter(queue_class=QueueClass.SPLITTING.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_splitting_queue_jobs:
        parser = queue_job.parser
        document = queue_job.document

        # Mark the job as completed
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.PARSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def splitting_queue_scheduler_start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 60 seconds
    scheduler.add_job(process_splitting_queue_job, 'interval',
                      seconds=5, name='process_splitting_queue', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Processing Splitting Queue", file=sys.stdout)
