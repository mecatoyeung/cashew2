import sys
import os
import io
import traceback
from pathlib import Path
from datetime import datetime
from jinja2 import Template
import shutil
import json
import glob
import base64
import re

from reportlab.pdfgen.canvas import Canvas
from PIL import Image

from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from parsers.models.pre_processing import PreProcessing
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.document_type import DocumentType
from parsers.models.integration import Integration
from parsers.models.integration_type import IntegrationType
from parsers.models.pdf_integration_type import PDFIntegrationType
from parsers.models.ocr import OCR

import zlib

from parsers.helpers.path_helpers import pre_processed_image_path, pre_processed_pdf_path, ocred_image_path, \
    hocr_path, ocred_pdf_path

from django.conf import settings


def convert_images_to_pdf(images, output_file_path):
    """Create a searchable PDF from a pile of HOCR + JPEG"""
    pdf = Canvas(output_file_path, pageCompression=1)
    dpi = 100
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


def process_single_integration_queue(queue_job):

    all_in_process_integration_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.INTEGRATION.value, queue_status=QueueStatus.IN_PROGRESS.value)
    if all_in_process_integration_queue_jobs.count() > 0:
        return

    try:

        # Mark the job as in progress
        queue_job.queue_class = QueueClass.INTEGRATION.value
        queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        queue_job.save()

        parser = queue_job.parser
        document = queue_job.document
        parsed_result = json.loads(queue_job.parsed_result)

        updated_parsed_result = {}
        for single_parsed_result in parsed_result:
            if single_parsed_result["streamed"]["type"] == "TEXTFIELD":
                str_value = [str(x) for x in single_parsed_result["streamed"]["value"]]
                value_result = " ".join(str_value)
                updated_parsed_result[single_parsed_result["rule"]
                                      ["name"]] = value_result
            elif single_parsed_result["streamed"]["type"] == "TABLE":
                value_result = []
                for row in single_parsed_result["streamed"]["value"]["body"]:
                    row_result = {}
                    for sIndex, sName in enumerate(single_parsed_result["streamed"]["value"]["header"]):
                        row_result[str(sIndex)] = row[sIndex]
                        row_result[str(sName)] = row[sIndex]
                    value_result.append(row_result)
                updated_parsed_result[single_parsed_result["rule"]
                                      ["name"]] = value_result
            elif single_parsed_result["streamed"]["type"] == "JSON":
                updated_parsed_result[single_parsed_result["rule"]
                                      ["name"]] = "Parse value is in JSON format. Please correct it by add streams to convert the JSON to Textfield or Table."

        # Do the job
        integrations = Integration.objects.filter(parser_id=parser.id)
        for integration in integrations:

            if not integration.activated:
                continue

            if integration.integration_type == IntegrationType.XML_INTEGRATION.value:

                xml_path = integration.xml_path
                template = integration.template

                builtin_vars = {
                    "created_at": datetime.now()
                }

                path_t = Template(xml_path)
                rendered_path_template = path_t.render(
                    parsed_result=updated_parsed_result, document=document, datetime=datetime, builtin_vars=builtin_vars, str=str)

                if Path(rendered_path_template).stem.split(".")[0] == "":
                    no_filename_path = os.path.join(os.path.dirname(
                        rendered_path_template), "No Filename")
                    if not os.path.exists(no_filename_path):
                        os.makedirs(no_filename_path)
                    failed_path = os.path.join(no_filename_path, "Document Name = " + document.filename_without_extension + "."
                                               + Path(rendered_path_template).stem.split(".")[1])
                    rendered_path_template = failed_path

                t = Template(template)
                rendered_template = t.render(
                    parsed_result=updated_parsed_result, document=document, datetime=datetime, builtin_vars=builtin_vars, str=str)

                text_file = open(os.path.join(
                    rendered_path_template), "w", encoding="utf-8")
                text_file.write(rendered_template)
                text_file.close()

            elif integration.integration_type == IntegrationType.PDF_INTEGRATION.value:

                if integration.pdf_integration_type == PDFIntegrationType.SOURCE.value:
                    pdf_from_path = os.path.join(settings.MEDIA_ROOT, 'documents', document.guid,
                                                 "source_file.pdf")
                elif integration.pdf_integration_type == PDFIntegrationType.PRE_PROCESSING.value:

                    pre_processing = PreProcessing.objects.get(
                        pk=integration.pre_processing_id)

                    document_pages = list(DocumentPage.objects.filter(
                        document_id=document.id).all())

                    image_paths = []
                    for document_page in document_pages:
                        image_path = pre_processed_image_path(
                            document, pre_processing, document_page.page_num)
                        image_paths.append(image_path)
                    output_pdf_path = pre_processed_pdf_path(
                        document, pre_processing)
                    convert_images_to_pdf(image_paths, output_pdf_path)

                    pdf_from_path = os.path.join(output_pdf_path)
                elif integration.pdf_integration_type == PDFIntegrationType.OCR.value:
                    abs_ocred_pdf_path = ocred_pdf_path(document)
                    pdf_from_path = abs_ocred_pdf_path
                elif integration.pdf_integration_type == PDFIntegrationType.POST_PROCESSING.value:
                    pdf_from_path = os.path.join(settings.MEDIA_ROOT, 'documents',
                                                 document.guid,
                                                 "post_processed-" +
                                                 str(integration.post_processing.id),
                                                 "output.pdf")

                pdf_path = integration.pdf_path

                builtin_vars = {
                    "created_at": datetime.now()
                }

                pdf_to_path_t = Template(pdf_path)
                pdf_to_path = pdf_to_path_t.render(
                    parsed_result=updated_parsed_result, document=document, datetime=datetime, builtin_vars=builtin_vars, str=str)

                if Path(pdf_to_path).stem.split(".")[0] == "":
                    no_filename_path = os.path.join(
                        os.path.dirname(pdf_to_path), "No Filename")
                    if not os.path.exists(no_filename_path):
                        os.makedirs(no_filename_path)
                    failed_path = os.path.join(no_filename_path, "Document Name = " + document.filename_without_extension + "."
                                               + Path(pdf_to_path).stem.split(".")[1])
                    pdf_to_path = failed_path

                shutil.copyfile(pdf_from_path, pdf_to_path)

            # Update last modified at
            document.last_modified_at = datetime.now()

        document.save()

        # Mark the job as completed
        if document.document_type == DocumentType.IMPORT.value:

            # Mark the job as preprocessing in progress
            queue_job.queue_class = QueueClass.TRASH.value
            queue_job.queue_status = QueueStatus.READY.value
            queue_job.save()

        else:

            # Mark the job as preprocessing in progress
            queue_job.queue_class = QueueClass.PROCESSED.value
            queue_job.queue_status = QueueStatus.COMPLETED.value
            queue_job.save()

    except Exception as e:
        traceback.print_exc()
        queue_job.queue_class = QueueClass.INTEGRATION.value
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def process_integration_queue_job():

    all_ready_integration_queue_jobs = Queue.objects \
        .select_related("document") \
        .filter(queue_class=QueueClass.INTEGRATION.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_integration_queue_jobs:

        process_single_integration_queue(queue_job)


def process_stopped_integration_queue_job():

    all_stopped_integration_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.INTEGRATION.value, queue_status=QueueStatus.STOPPED.value)

    for queue_job in all_stopped_integration_queue_jobs:
        queue_job.queue_class = QueueClass.PROCESSED.value
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()


def process_inprogress_integration_queue_job():

    all_inprogress_integration_queue_jobs = Queue.objects.filter(
        queue_class=QueueClass.INTEGRATION.value, queue_status=QueueStatus.IN_PROGRESS.value)

    for queue_job in all_inprogress_integration_queue_jobs:
        queue_job.queue_status = QueueStatus.READY.value
        queue_job.save()


def integration_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "integration_queue_job_store")
    # run this job every 60 seconds
    process_inprogress_integration_queue_job()
    scheduler.add_job(process_integration_queue_job, 'interval', seconds=15)
    scheduler.add_job(process_stopped_integration_queue_job,
                      'interval', seconds=15)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Integration Queue", file=sys.stdout)
