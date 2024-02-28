
import sys
import os
from pathlib import Path
import traceback
import glob

from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job

from reportlab.pdfgen.canvas import Canvas
from PIL import Image

from parsers.models.parser import Parser
from parsers.models.ocr import OCR
from parsers.models.ocr_type import OCRType
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.pre_processing_type import PreProcessingType
from parsers.models.pre_processing import PreProcessing

from parsers.helpers.detect_orientation_opencv import detect_orientation_opencv
from parsers.helpers.detect_orientation_tesseract import detect_orientation_tesseract
from parsers.helpers.threshold_binarization import threshold_binarization

from parsers.schedule_jobs.process_ocr_queue import process_single_no_ocr_queue, process_single_ocr_queue

from backend.settings import MEDIA_ROOT

def process_single_preprocessing_queue(queue_job):

    all_in_process_pre_processing_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.PRE_PROCESSING.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_pre_processing_queue_jobs.count() > 0:
        return
    
    # Mark the job as in progress
    queue_job.queue_class = QueueClass.PRE_PROCESSING.value
    queue_job.queue_status = QueueStatus.IN_PROGRESS.value
    queue_job.save()

    try:
        parser = queue_job.parser
        document = Document.objects.prefetch_related(Prefetch("document_pages", queryset=DocumentPage.objects.order_by('page_num'))).get(pk=queue_job.document_id)

        # Do the job
        media_folder_path = MEDIA_ROOT
        documents_folder_path = os.path.join(
            media_folder_path, "documents", str(document.guid))

        pre_processings = PreProcessing.objects.filter(
            parser_id=parser.id).order_by("step")

        image_paths = []

        for page_idx in range(document.total_page_num):

            # Check if Pre-Processing has been stopped
            queue = Queue.objects.get(
                document_id=document.id
            )
            if queue.queue_status == QueueStatus.STOPPED.value:
                queue.queue_class = QueueClass.PROCESSED.value
                queue.queue_status = QueueStatus.READY.value
                queue.save()
                break

            page_num = page_idx + 1
            document_page = DocumentPage.objects.get(
                document_id=document.id, page_num=page_num)
            
            last_pre_processing = None

            for pre_processing_index, pre_processing in enumerate(pre_processings):

                working_path = os.path.join(
                    documents_folder_path, "pre_processed-" + str(pre_processing.id))
                is_working_dir_exist = os.path.exists(working_path)
                if not is_working_dir_exist:
                    os.makedirs(working_path)

                pre_processings_type = pre_processing.pre_processing_type
                if pre_processings_type == PreProcessingType.ORIENTATION_DETECTION_OPENCV.value:

                    detect_orientation_opencv(document, page_num, pre_processing,
                                                last_pre_processing)
                    
                if pre_processings_type == PreProcessingType.ORIENTATION_DETECTION_TESSERACT.value:

                    detect_orientation_tesseract(document, page_num, pre_processing,
                                                last_pre_processing)
                    
                elif pre_processings_type == PreProcessingType.THRESHOLD_BINARIZATION.value:

                    threshold_binarization(document_page, pre_processing,
                                                last_pre_processing)

                last_pre_processing = pre_processing

            document_page.preprocessed = True
            document_page.save()

        for pre_processing_index, pre_processing in enumerate(pre_processings):

            image_paths = glob.glob('*.jpg')
            image_paths.sort(key=lambda x: int(Path(x).stem))

            output_pdf_path = os.path.join(
                documents_folder_path, "pre_processed-" + str(pre_processing.id), "output.pdf")
            convert_images_to_pdf(image_paths, output_pdf_path)

        # Mark the job as completed
        # queue_job.queue_status = QueueStatus.COMPLETED.value
        # queue_job.save()

        # Mark the job as preprocessing in progress
        updated_queue_job = Queue.objects.get(pk=queue_job.id)
        if updated_queue_job.queue_class == QueueClass.PROCESSED.value and updated_queue_job.queue_status == QueueStatus.READY.value:
            return
        queue_job.queue_class = QueueClass.OCR.value
        queue_job.queue_status = QueueStatus.READY.value
        document_pages = document.document_pages.all()
        for document_page in document_pages:
            document_page.preprocessed = True
            document_page.ocred = False
            document_page.save()
        queue_job.save()

        ocr = OCR.objects.get(parser_id=parser.id)
        if ocr.ocr_type == OCRType.NO_OCR.value:
            process_single_no_ocr_queue(queue_job)
        else:
            process_single_ocr_queue(queue_job)

    except Exception as e:
        print(traceback.format_exc())
        queue_job.queue_class = QueueClass.PRE_PROCESSING.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()

def convert_images_to_pdf(images, output_file_path):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    pdf = Canvas(output_file_path, pageCompression=1)
    dpi = 300
    for image in images:
        im = Image.open(image)
        w, h = im.size
        try:
            dpi = im.info['dpi'][0]
        except KeyError:
            pass
        width = w * 72 / dpi
        height = h * 72 / dpi
        pdf.setPageSize((width, height))
        pdf.drawImage(image, 0, 0, width=width, height=height)
        pdf.showPage()
    pdf.save()

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

        process_single_preprocessing_queue(queue_job)

def process_stopped_preprocessing_queue_job():

    all_stopped_preprocessing_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.PRE_PROCESSING.value, queue_status=QueueStatus.STOPPED.value)

    for queue_job in all_stopped_preprocessing_queue_jobs:
        queue_job.queue_class = QueueClass.PROCESSED.value
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()


def preprocessing_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "preprocessing_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_preprocessing_queue_job, 'interval', seconds=5)
    scheduler.add_job(process_stopped_preprocessing_queue_job,
                      'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Pre-processing Queue", file=sys.stdout)
