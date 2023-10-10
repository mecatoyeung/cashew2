from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
import sys

def process_import_queue_job():
    all_ready_import_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related("document__documentpages_set").filter(
            queue_status=QueueStatus.READY,
            queue_class=QueueClass.IMPORT
        ).all()
    for queue_job in all_ready_import_queue_jobs:
        parser = queue_job.parser
        

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(process_import_queue_job, 'interval', seconds=60, name='clean_accounts', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Processing import queue", file=sys.stdout)