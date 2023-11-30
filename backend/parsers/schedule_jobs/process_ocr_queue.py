from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from django.db.models import Q

from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.pre_processing import PreProcessing
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from backend.settings import MEDIA_URL
import sys
import os
from pathlib import Path
import shutil
from parsers.helpers.convert_to_searchable_pdf_gcv import convert_to_searchable_pdf_gcv
from parsers.helpers.convert_to_searchable_pdf_doctr import convert_to_searchable_pdf_doctr
from parsers.helpers.convert_to_searchable_pdf_paddleocr import convert_to_searchable_pdf_paddleocr
from parsers.helpers.parse_pdf_to_xml import parse_pdf_to_xml


def process_ocr_queue_job():

    all_in_process_ocr_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.OCR.value, queue_status=QueueStatus.IN_PROGRESS.value). \
        exclude(parser__ocr__ocr_type=OCRType.NO_OCR.value)
    if all_in_process_ocr_queue_jobs.count() > 0:
        return

    all_ready_ocr_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                Prefetch(
                    "document_pages",
                    queryset=DocumentPage.objects.order_by("page_num")
                )
            )
        )) \
        .filter(queue_class=QueueClass.OCR.value, queue_status=QueueStatus.READY.value) \
        .exclude(parser__ocr__ocr_type=OCRType.NO_OCR.value) \
        .all()
    for queue_job in all_ready_ocr_queue_jobs:
        parser = queue_job.parser
        document = queue_job.document
        preprocessings = PreProcessing.objects.filter(parser_id=parser.id)
        ocr = OCR.objects.get(parser_id=parser.id)

        # Mark the job as in progress
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        try:
            # Do the job
            # Create Working Dir if not exist
            media_folder_path = MEDIA_URL
            documents_path = os.path.join(
                media_folder_path, "documents", str(document.guid))
            working_path = os.path.join(documents_path, "ocr")
            is_working_dir_exist = os.path.exists(working_path)
            if not is_working_dir_exist:
                os.makedirs(working_path)

            searchable_pdf_path = os.path.join(
                documents_path, 'ocred.pdf')
            if ocr.ocr_type == OCRType.GOOGLE_VISION.value:
                convert_to_searchable_pdf_gcv(document,
                                              searchable_pdf_path,
                                              documents_path,
                                              google_vision_api_key=ocr.google_vision_ocr_api_key,
                                              preprocessings=preprocessings)
            elif ocr.ocr_type == OCRType.DOCTR.value:
                convert_to_searchable_pdf_doctr(document,
                                                searchable_pdf_path,
                                                documents_path,
                                                preprocessings=preprocessings)
            elif ocr.ocr_type == OCRType.PADDLE_OCR.value:
                convert_to_searchable_pdf_paddleocr(document,
                                                    searchable_pdf_path,
                                                    documents_path,
                                                    preprocessings=preprocessings,
                                                    lang=ocr.paddle_ocr_language)
            """elif ocr.ocr_type == OCRType.NO_OCR.value:
                parse_pdf_to_xml(document)
                source_file_path = os.path.join(
                    documents_path, 'source_file.pdf')
                shutil.copy(source_file_path,
                            searchable_pdf_path)"""

            # Mark the job as preprocessing in progress
            queue_job.queue_class = QueueClass.SPLITTING.value
            queue_job.queue_status = QueueStatus.READY.value
            queue_job.save()
        except Exception as e:
            queue_job.queue_class = QueueClass.OCR.value
            queue_job.queue_status = QueueStatus.READY.value
            queue_job.save()
            raise e


def process_no_ocr_queue_job():

    all_in_process_no_ocr_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.OCR.value, queue_status=QueueStatus.IN_PROGRESS.value,
        parser__ocr__ocr_type=OCRType.NO_OCR.value)
    if all_in_process_no_ocr_queue_jobs.count() > 0:
        return

    all_ready_no_ocr_queue_jobs = Queue.objects \
        .select_related("document") \
        .prefetch_related(Prefetch(
            "document",
            queryset=Document.objects.prefetch_related(
                Prefetch(
                    "document_pages",
                    queryset=DocumentPage.objects.order_by("page_num")
                )
            )
        )) \
        .filter(queue_class=QueueClass.OCR.value,
                queue_status=QueueStatus.READY.value,
                parser__ocr__ocr_type=OCRType.NO_OCR.value) \
        .all()
    for queue_job in all_ready_no_ocr_queue_jobs:
        parser = queue_job.parser
        document = queue_job.document
        ocr = OCR.objects.get(parser_id=parser.id)

        # Mark the job as in progress
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        try:
            # Do the job
            # Create Working Dir if not exist
            media_folder_path = MEDIA_URL
            documents_path = os.path.join(
                media_folder_path, "documents", str(document.guid))
            working_path = os.path.join(documents_path, "ocr")
            is_working_dir_exist = os.path.exists(working_path)
            if not is_working_dir_exist:
                os.makedirs(working_path)

            searchable_pdf_path = os.path.join(
                documents_path, 'ocred.pdf')
            if ocr.ocr_type == OCRType.NO_OCR.value:
                parse_pdf_to_xml(document)
                source_file_path = os.path.join(
                    documents_path, 'source_file.pdf')
                shutil.copy(source_file_path,
                            searchable_pdf_path)

            # Mark the job as preprocessing in progress
            queue_job.queue_class = QueueClass.SPLITTING.value
            queue_job.queue_status = QueueStatus.READY.value
            queue_job.save()
        except Exception as e:
            queue_job.queue_class = QueueClass.OCR.value
            queue_job.queue_status = QueueStatus.READY.value
            queue_job.save()
            raise e


def ocr_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "ocr_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_ocr_queue_job, 'interval', seconds=5)
    scheduler.add_job(process_no_ocr_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing OCR Queue", file=sys.stdout)
