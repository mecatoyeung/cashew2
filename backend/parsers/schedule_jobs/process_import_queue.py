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
from parsers.schedule_jobs.process_preprocessing_queue import process_single_preprocessing_queue
import sys


def process_import_queue_job():

    all_in_process_import_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.IMPORT.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_import_queue_jobs.count() > 0:
        return

    all_ready_import_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .filter(queue_class=QueueClass.IMPORT.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_import_queue_jobs:
        parser = queue_job.parser
        # Mark the job as in progress
        queue_job.queue_class = QueueClass.IMPORT.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        # Do the job

        # Mark the job as completed
        # queue_job.queue_status = QueueStatus.COMPLETED.value
        # queue_job.save()
        document = queue_job.document
        parser.total_num_of_pages_processed += document.total_page_num
        parser.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.PRE_PROCESSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_preprocessing_queue(queue_job)


def import_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "import_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_import_queue_job, 'interval', seconds=5)
    scheduler.start()
    # scheduler.add_job(process_import_queue_job, 'interval',
    #                  seconds=5, name='process_import_queue', jobstore='import_queue_job_store')
    # register_events(scheduler)
    print("Processing Import Queue", file=sys.stdout)
    # scheduler.shutdown()
