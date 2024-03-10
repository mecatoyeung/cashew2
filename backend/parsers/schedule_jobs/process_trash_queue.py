import sys
import os
import traceback
from pathlib import Path
from datetime import datetime
from jinja2 import Template
import shutil
import json
import glob

from django.db.models import Prefetch
from django.db.models import Q

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_type import DocumentType
from parsers.models.integration import Integration
from parsers.models.integration_type import IntegrationType
from parsers.models.pdf_integration_type import PDFIntegrationType

from django.conf import settings


def process_single_trash_queue(queue_job):

    all_in_process_trash_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.TRASH.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_trash_queue_jobs.count() > 0:
        return

    # Mark the job as in progress
    queue_job.queue_class = QueueClass.TRASH.value
    queue_job.queue_status = QueueStatus.IN_PROGRESS.value
    queue_job.save()

    document = queue_job.document

    try:
        # Delete Files
        document_folder = os.path.join(
            settings.MEDIA_ROOT, 'documents', document.guid)
        shutil.rmtree(document_folder)
        # Delete documents after integration
        Document.objects.filter(id=document.id).delete()
        # Delete queue after integration
        queue_job.delete()
    except Exception as e:
        print(traceback.format_exc())
        queue_job.queue_class = QueueClass.TRASH.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()
        document.document_type = DocumentType.TRASH.value
        document.save()
        pass


def process_trash_queue_job():

    all_ready_trash_queue_jobs = Queue.objects \
        .select_related("document") \
        .filter(queue_class=QueueClass.TRASH.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_trash_queue_jobs:

        process_single_trash_queue(queue_job)


def trash_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "integration_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_trash_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Integration Queue", file=sys.stdout)
