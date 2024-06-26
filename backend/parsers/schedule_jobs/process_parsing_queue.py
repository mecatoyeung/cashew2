import sys
import os
from pathlib import Path
import json
import traceback
from datetime import datetime
from django.db.models import Prefetch
from django.db.models import Q

from apscheduler.schedulers.background import BackgroundScheduler

from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.ocr import OCR
from parsers.models.rule import Rule
from parsers.models.rule_type import RuleType
from parsers.helpers.document_parser import DocumentParser

from parsers.schedule_jobs.process_postprocessing_queue import process_single_postprocessing_queue


def sort_rules_for_depending_rules(rules, parent_id=None, sorted_rules=[]):
    if (len(rules) == 0):
        return sorted_rules
    children_rules = rules.filter(depends_on_id=parent_id)
    remaining_rules = rules.exclude(depends_on_id=parent_id) 
    for r in children_rules:
        sorted_rules.append(r)
        sort_rules_for_depending_rules(remaining_rules, r.id, sorted_rules=sorted_rules)
    return sorted_rules


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

        # Calculate the sequence to parse rules considering dependent rules
        sorted_rules = sort_rules_for_depending_rules(rules, parent_id=None, sorted_rules=[])

        for rule in sorted_rules:
            result = document_parser.extract_and_stream(rule, parsed_result=parsed_result)

            if result["streamed"]["value"] == None:
                result["streamed"]["value"] = [""]

            parsed_result.append(result)

        queue_job.parsed_result = json.dumps(parsed_result)

        # Update last modified at
        document.last_modified_at = datetime.now()
        document.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.POST_PROCESSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_postprocessing_queue(queue_job)

    except Exception as e:
        queue_job.queue_class = QueueClass.PARSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()
        print(traceback.print_exc())

def process_stopped_parsing_queue_job():

    all_stopped_parsing_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.PARSING.value, queue_status=QueueStatus.STOPPED.value)

    for queue_job in all_stopped_parsing_queue_jobs:
        queue_job.queue_class = QueueClass.PROCESSED.value
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

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
    scheduler.add_job(process_stopped_parsing_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Parsing Queue", file=sys.stdout)
