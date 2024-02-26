import sys
import os
from pathlib import Path
import shutil
import traceback

from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import Q

from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.pre_processing import PreProcessing
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType

from parsers.helpers.parse_pdf_to_xml import parse_pdf_to_xml

from parsers.schedule_jobs.process_splitting_queue import process_single_splitting_queue

from backend.settings import MEDIA_ROOT

from parsers.helpers.convert_to_searchable_pdf import convert_to_searchable_pdf

def process_single_ocr_queue(queue_job):

    all_in_process_ocr_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.OCR.value, queue_status=QueueStatus.IN_PROGRESS.value). \
        exclude(parser__ocr__ocr_type=OCRType.NO_OCR.value)
    if all_in_process_ocr_queue_jobs.count() > 0:
        return
    
    parser = queue_job.parser
    document = Document.objects.prefetch_related(Prefetch("document_pages", queryset=DocumentPage.objects.order_by('page_num'))).get(pk=queue_job.document_id)
    preprocessings = PreProcessing.objects.filter(parser_id=parser.id)
    ocr = OCR.objects.get(parser_id=parser.id)

    # Mark the job as in progress
    queue_job.queue_class = QueueClass.OCR.value
    queue_job.queue_status = QueueStatus.IN_PROGRESS.value
    queue_job.save()

    try:
        # Do the job
        # Create Working Dir if not exist
        """media_folder_path = MEDIA_ROOT
        documents_path = os.path.join(
            media_folder_path, "documents", str(document.guid))
        working_path = os.path.join(documents_path, "ocr")
        is_working_dir_exist = os.path.exists(working_path)
        if not is_working_dir_exist:
            os.makedirs(working_path)

        searchable_pdf_path = os.path.join(
            documents_path, 'ocred.pdf')
        if ocr.ocr_type == OCRType.GOOGLE_VISION.value:
            from parsers.helpers.convert_to_searchable_pdf_gcv import convert_to_searchable_pdf_gcv
            convert_to_searchable_pdf_gcv(document,
                                            searchable_pdf_path,
                                            documents_path,
                                            google_vision_api_key=ocr.google_vision_ocr_api_key,
                                            preprocessings=preprocessings)
        elif ocr.ocr_type == OCRType.DOCTR.value:
            from parsers.helpers.convert_to_searchable_pdf_doctr import convert_to_searchable_pdf_doctr
            convert_to_searchable_pdf_doctr(document,
                                            searchable_pdf_path,
                                            documents_path,
                                            preprocessings=preprocessings)
        elif ocr.ocr_type == OCRType.PADDLE_OCR.value:
            from parsers.helpers.convert_to_searchable_pdf_paddleocr import convert_to_searchable_pdf_paddleocr
            convert_to_searchable_pdf_paddleocr(document,
                                                searchable_pdf_path,
                                                documents_path,
                                                preprocessings=preprocessings,
                                                lang=ocr.paddle_ocr_language)
        elif ocr.ocr_type == OCRType.OMNIPAGE_OCR.value:
            from parsers.helpers.convert_to_searchable_pdf_omnipage import convert_to_searchable_pdf_omnipage
            convert_to_searchable_pdf_omnipage(document,
                                                searchable_pdf_path,
                                                documents_path,
                                                preprocessings=preprocessings,
                                                lang=ocr.omnipage_ocr_language)"""
        convert_to_searchable_pdf(parser, document, ocr)

        # Mark the job as preprocessing in progress
        updated_queue_job = Queue.objects.get(pk=queue_job.id)
        if updated_queue_job.queue_class == QueueClass.PROCESSED.value and updated_queue_job.queue_status == QueueStatus.READY.value:
            return

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.SPLITTING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_splitting_queue(queue_job)
        
    except Exception as e:
        print(traceback.format_exc())
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def process_ocr_queue_job():

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
        process_single_ocr_queue(queue_job)

def process_single_no_ocr_queue(queue_job):

    all_in_process_no_ocr_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.OCR.value, queue_status=QueueStatus.IN_PROGRESS.value,
        parser__ocr__ocr_type=OCRType.NO_OCR.value)
    if all_in_process_no_ocr_queue_jobs.count() > 0:
        return
    
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
        media_folder_path = MEDIA_ROOT
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
        updated_queue_job = Queue.objects.get(pk=queue_job.id)
        if updated_queue_job.queue_class == QueueClass.PROCESSED.value and updated_queue_job.queue_status == QueueStatus.READY.value:
            return
        queue_job.queue_class = QueueClass.SPLITTING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

        process_single_splitting_queue(queue_job)

    except Exception as e:
        print(traceback.format_exc())
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

def process_no_ocr_queue_job():

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
        process_single_no_ocr_queue(queue_job)


def process_stopped_ocr_queue_job():

    all_stopped_ocr_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.OCR.value, queue_status=QueueStatus.STOPPED.value)

    for queue_job in all_stopped_ocr_queue_jobs:
        queue_job.queue_class = QueueClass.PROCESSED.value
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

def process_inprogress_ocr_queue_job():

    all_inprogress_ocr_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.OCR.value, queue_status=QueueStatus.IN_PROGRESS.value)

    for queue_job in all_inprogress_ocr_queue_jobs:
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def ocr_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "ocr_queue_job_store")
    # run this job every 60 seconds
    process_inprogress_ocr_queue_job()
    scheduler.add_job(process_ocr_queue_job, 'interval', seconds=5)
    scheduler.add_job(process_no_ocr_queue_job, 'interval', seconds=5)
    scheduler.add_job(process_stopped_ocr_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing OCR Queue", file=sys.stdout)
