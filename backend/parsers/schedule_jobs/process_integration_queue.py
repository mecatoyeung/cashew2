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
from parsers.models.document_type import DocumentType
from parsers.models.integration import Integration
from parsers.models.integration_type import IntegrationType
from parsers.models.pdf_integration_type import PDFIntegrationType
from backend.settings import MEDIA_URL
import sys
import os
from pathlib import Path
from datetime import datetime
from jinja2 import Template
import shutil
import json
import glob

from django.conf import settings


def process_integration_queue_job():

    failed_job_counter = 0
    all_ready_integration_queue_jobs = Queue.objects \
        .select_related("document") \
        .filter(queue_class=QueueClass.INTEGRATION.value, queue_status=QueueStatus.READY.value) \
        .all()
    for queue_job in all_ready_integration_queue_jobs:
        parser = queue_job.parser
        document = queue_job.document
        parsed_result = json.loads(queue_job.parsed_result)
        failed_job_counter += 1

        updated_parsed_result = {}
        for single_parsed_result in parsed_result:
            if single_parsed_result["rule"]["type"] == "TEXTFIELD" or \
                    single_parsed_result["rule"]["type"] == "ANCHORED_TEXTFIELD" or \
                    single_parsed_result["rule"]["type"] == "BARCODE":
                updated_parsed_result[single_parsed_result["rule"]
                                      ["name"]] = single_parsed_result["streamed"]
            else:
                updated_parsed_result[single_parsed_result["rule"]
                                      ["name"]] = " ".join(single_parsed_result["streamed"])

        # Mark the job as in progress
        # queue_job.queue_class = QueueClass.INTEGRATION.value
        # queue_job.queue_status = QueueStatus.IN_PROGRESS.value
        # queue_job.save()

        # Do the job
        integrations = Integration.objects.filter(parser_id=parser.id)
        for integration in integrations:
            if integration.integration_type == IntegrationType.XML_INTEGRATION.value:

                xml_path = integration.xml_path
                template = integration.template

                builtin_vars = {
                    "created_date": datetime.now()
                }

                path_t = Template(xml_path)
                rendered_path_template = path_t.render(
                    parsed_result=updated_parsed_result, document=document, datetime=datetime, builtin_vars=builtin_vars, str=str)

                if Path(rendered_path_template).stem.split(".")[0] == "":
                    failed_path = os.path.join(os.path.dirname(rendered_path_template), "No filename (Document Name = " + document.filename_without_extension + ")."
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
                    pdf_from_path = os.path.join(settings.MEDIA_ROOT, 'documents',
                                                 document.guid,
                                                 "pre_processed-" +
                                                 str(integration.pre_processing.id),
                                                 "output.pdf")
                elif integration.pdf_integration_type == PDFIntegrationType.OCR.value:
                    pdf_from_path = os.path.join(settings.MEDIA_ROOT, 'documents', document.guid,
                                                 "ocred.pdf")
                elif integration.pdf_integration_type == PDFIntegrationType.POST_PROCESSING.value:
                    pdf_from_path = os.path.join(settings.MEDIA_ROOT, 'documents',
                                                 document.guid,
                                                 "post_processed-" +
                                                 str(integration.post_processing.id),
                                                 "output.pdf")

                pdf_path = integration.pdf_path

                builtin_vars = {
                    "created_date": datetime.now()
                }

                pdf_to_path_t = Template(pdf_path)
                pdf_to_path = pdf_to_path_t.render(
                    parsed_result=updated_parsed_result, document=document, datetime=datetime, builtin_vars=builtin_vars, str=str)

                if Path(pdf_to_path).stem.split(".")[0] == "":
                    failed_path = os.path.join(os.path.dirname(pdf_to_path), "No filename (Document GUID = " + document.filename_without_extension + ")."
                                               + Path(pdf_to_path).stem.split(".")[1])
                    pdf_to_path = failed_path

                shutil.copyfile(pdf_from_path, pdf_to_path)

        # Mark the job as completed
        # queue_job.queue_status = QueueStatus.COMPLETED.value
        # queue_job.save()

        # Mark the job as preprocessing in progress
        queue_job.queue_class = QueueClass.PROCESSED.value
        queue_job.queue_status = QueueStatus.COMPLETED.value
        queue_job.save()

        # Delete documents after integration
        if document.document_type == DocumentType.IMPORT.value:
            document_folder = os.path.join(
                settings.MEDIA_ROOT, 'documents', document.guid)
            shutil.rmtree(document_folder)
            queue_job.delete()
            Document.objects.filter(pk=document.id).delete()


def integration_queue_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 1})
    # scheduler.add_jobstore(DjangoJobStore(), "integration_queue_job_store")
    # run this job every 60 seconds
    scheduler.add_job(process_integration_queue_job, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing Integration Queue", file=sys.stdout)
