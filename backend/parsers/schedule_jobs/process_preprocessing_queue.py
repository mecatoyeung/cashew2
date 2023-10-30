
import sys
import os
from pathlib import Path

from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from parsers.models.parser import Parser
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.pre_processing_type import PreProcessingType
from parsers.models.pre_processing import PreProcessing
from parsers.helpers.detect_orientation import detect_orientation

from backend.settings import MEDIA_URL


def process_preprocessing_queue_job():
    all_ready_preprocessing_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .filter(queue_class=QueueClass.PRE_PROCESSING.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_preprocessing_queue_jobs:
        parser = queue_job.parser
        document = queue_job.document
        # Mark the job as in progress
        queue_job.queue_class = QueueClass.PRE_PROCESSING.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        # Do the job

        pre_processings = PreProcessing.objects.filter(
            parser_id=parser.id).order_by("-step")

        last_pre_processing = None

        for pre_processing_index, pre_processing in enumerate(pre_processings):

            pre_processings_type = pre_processing.pre_processing_type
            if pre_processings_type == PreProcessingType.ORIENTATION_DETECTION.value:

                detect_orientation(document, pre_processing,
                                   last_pre_processing)

            last_pre_processing = pre_processing

        # Mark the job as completed
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def preprocessing_queue_scheduler_start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 60 seconds
    scheduler.add_job(process_preprocessing_queue_job, 'interval',
                      seconds=5, name='process_preprocessing_queue', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Processing Pre-processing Queue", file=sys.stdout)
