import sys
import os
import traceback
import re
import fitz
from pathlib import Path
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
from parsers.models.post_processing import PostProcessing
from parsers.models.post_processing_type import PostProcessingType

from parsers.schedule_jobs.process_integration_queue import process_single_integration_queue

from backend.settings import MEDIA_ROOT


class Redactor:

    def get_sensitive_data(self, lines, regex):
        """ Function to get all the lines """

        # DOLLAR_AMT_REG = r"(\$?[0-9]+\.(?:[0-9]{2}))"
        for line in lines:

            # matching the regex to each line
            if re.search(self.regex, line, re.IGNORECASE):
                search = re.search(self.regex, line, re.IGNORECASE)

                # yields creates a generator
                # generator is used to return
                # values in between function iterations
                try:
                    yield search.group(1)
                except:
                    pass

    # constructor
    def __init__(self, regex, input_path, output_path):
        self.regex = regex
        self.input_path = input_path
        self.output_path = output_path

    def redaction(self):
        """ main redactor code """

        # opening the pdf
        doc = fitz.open(self.input_path)

        # iterating through pages
        for page in doc:

            sensitive = self.get_sensitive_data(page.get_text("text")
                                                .split('\n'),
                                                self.regex)
            for data in sensitive:
                areas = page.search_for(data)

                # drawing outline over sensitive datas
                [page.add_redact_annot(area, fill=(0, 0, 0)) for area in areas]

            # applying the redaction
            page.apply_redactions()

        # saving it to a new pdf
        doc.save(self.output_path, garbage=4, deflate=True)

def process_single_postprocessing_queue(queue_job):

    # Mark the job as in progress
    queue_job.queue_class = QueueClass.POST_PROCESSING.value
    queue_job.queue_status = QueueStatus.IN_PROGRESS.value
    queue_job.save()

    try:
        parser = queue_job.parser
        document = queue_job.document

        # Do the job
        post_processings = PostProcessing.objects.filter(
            parser_id=parser.id)

        for post_processing_index, post_processing in enumerate(post_processings):

            post_processings_type = post_processing.post_processing_type
            if post_processings_type == PostProcessingType.REDACTION.value:
                redaction_regex = post_processing.redaction_regex

                if post_processing_index == 0:
                    pdf_input_path = os.path.join(MEDIA_ROOT, 'documents', document.guid,
                                                    "ocred.pdf")
                else:
                    pdf_input_path = pdf_out_path

                working_path = os.path.join(
                    MEDIA_ROOT, 'documents', document.guid, "post_processed-" + str(post_processing.id))
                is_working_dir_exist = os.path.exists(working_path)
                if not is_working_dir_exist:
                    os.makedirs(working_path)

                pdf_out_path = os.path.join(MEDIA_ROOT, 'documents', document.guid,
                                            "post_processed-" + str(post_processing.id), "output.pdf")

                redactor = Redactor(redaction_regex,
                                    pdf_input_path,
                                    pdf_out_path)
                redactor.redaction()

            # Update last modified at
            document.last_modified_at = datetime.now()

        document.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.INTEGRATION.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_integration_queue(queue_job)

    except Exception as e:
        print(traceback.format_exc())
        queue_job.queue_class = QueueClass.POST_PROCESSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

def process_postprocessing_queue_job():

    all_in_process_post_processing_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.POST_PROCESSING.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_post_processing_queue_jobs.count() > 0:
        return

    all_ready_postprocessing_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .filter(queue_class=QueueClass.POST_PROCESSING.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_postprocessing_queue_jobs:

        process_single_postprocessing_queue(queue_job)


def process_stopped_postprocessing_queue_job():

    all_stopped_postprocessing_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.POST_PROCESSING.value, queue_status=QueueStatus.STOPPED.value)

    for queue_job in all_stopped_postprocessing_queue_jobs:
        queue_job.queue_class = QueueClass.PROCESSED.value
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        document_pages = DocumentPage.objects.filter(
            document__queue__id=queue_job.pk)
        for document_page in document_pages:
            document_page.preprocessed = False
            document_page.ocred = False
            document_page.postprocessed = False
            document_page.save()


def postprocessing_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "postprocessing_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_postprocessing_queue_job, 'interval', seconds=5)
    scheduler.add_job(process_stopped_postprocessing_queue_job,
                      'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Post-processing Queue", file=sys.stdout)
