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
from ..helpers.convert_to_searchable_pdf_gcv import convert_to_searchable_pdf_gcv
from ..helpers.convert_to_searchable_pdf_doctr import convert_to_searchable_pdf_doctr
from ..helpers.parse_pdf_to_xml import parse_pdf_to_xml


def process_ocr_queue_job():
    all_ready_import_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                "document_pages"
            )
        )) \
        .filter(queue_class=QueueClass.OCR.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_import_queue_jobs:
        parser = queue_job.parser
        document = queue_job.document
        ocr = OCR.objects.get(parser_id=parser.id)
        # Mark the job as in progress
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        if ocr.ocr_type != OCRType.NO_OCR.value:

            # Do the job
            # Create Working Dir if not exist
            media_folder_path = MEDIA_URL
            documents_folder_path = os.path.join(
                media_folder_path, "documents", str(document.guid))
            source_file_folder_path = os.path.join(
                documents_folder_path, "source_file.pdf")
            working_path = os.path.join(documents_folder_path, "ocr")
            is_working_dir_exist = os.path.exists(working_path)
            if not is_working_dir_exist:
                os.makedirs(working_path)

            searchable_pdf_path = os.path.join(
                documents_folder_path, 'ocred.pdf')
            app_path = Path(__file__).parent.parent
            if ocr.ocr_type == "GOOGLE_VISION":
                convert_to_searchable_pdf_gcv(source_file_folder_path,
                                              searchable_pdf_path,
                                              working_path=working_path,
                                              poppler_path=os.path.join(
                                                  app_path, "poppler", "Library", "bin"),
                                              google_vision_api_key=ocr.google_vision_ocr_api_key)
            elif ocr.ocr_type == "DOCTR":
                convert_to_searchable_pdf_doctr(source_file_folder_path,
                                                searchable_pdf_path,
                                                working_path=working_path,
                                                poppler_path=os.path.join(app_path, "poppler", "Library", "bin"))

        # Extract XML for data parsing later
        parse_pdf_to_xml(document)

        # Mark the job as completed
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.SPLITTING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def ocr_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 1})
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 60 seconds
    scheduler.add_job(process_ocr_queue_job, 'interval',
                      seconds=5, name='process_ocr_queue', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Processing OCR queue", file=sys.stdout)
