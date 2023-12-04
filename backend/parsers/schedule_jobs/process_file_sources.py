import os
import sys
import stat
import uuid
from datetime import timedelta

from io import BytesIO

from django.db.models import Prefetch

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.jobstores import register_job
from django.core.files import File

from PyPDF2 import PdfReader


from parsers.models.parser import Parser
from parsers.models.source import Source
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.document import Document
from parsers.models.document_type import DocumentType
from parsers.models.document_extension import DocumentExtension
from parsers.serializers.document import DocumentUploadSerializer


class FileObject:

    def __init__(self, filename, file):
        self.filename = filename
        self.file = file


def process_file_sources():

    file_sources = Source.objects.all()
    for file_source in file_sources:
        if file_source.next_run_time > timezone.now():
            continue

        if file_source.is_running == True:
            continue

        file_source.is_running = True
        file_source.save()

        try:

            source_path = file_source.source_path

            for dirpath, _, filenames in os.walk(source_path):
                for filename in filenames:
                    if filename.endswith(".pdf") or filename.endswith(".PDF"):

                        try:
                            abs_source_file_path = os.path.abspath(
                                os.path.join(dirpath, filename))

                            os.chmod(abs_source_file_path, stat.S_IWRITE)

                            document_upload_serializer_data = {}

                            with open(abs_source_file_path, "rb") as file:

                                document_upload_serializer_data["file"] = File(BytesIO(
                                    file.read()), file.name)
                                file.close()

                            parser_id = file_source.parser_id
                            document_upload_serializer_data["parser"] = parser_id

                            document_upload_serializer_data["guid"] = str(
                                uuid.uuid4())

                            document_upload_serializer_data["document_type"] = DocumentType.IMPORT.value

                            document_upload_serializer_data["document_extension"] = DocumentExtension.PDF.value

                            document_upload_serializer_data["filename_without_extension"] = os.path.basename(filename).split(".")[
                                0]
                            document_upload_serializer_data["extension"] = filename.split(".")[
                                1].lower()

                            try:
                                with open(abs_source_file_path, "rb") as file:
                                    pdf = PdfReader(file)
                                    document_upload_serializer_data["total_page_num"] = len(
                                        pdf.pages)
                                    file.close()
                            except Exception as e:
                                print(e)

                            document_upload_serializer = DocumentUploadSerializer(
                                data=document_upload_serializer_data)

                            if document_upload_serializer.is_valid():
                                document_upload_serializer.save()

                        except Exception as e:

                            print(e)

                        finally:

                            if os.path.isfile(abs_source_file_path):
                                os.remove(abs_source_file_path)

            file_source.next_run_time = timezone.now(
            ) + timedelta(seconds=file_source.interval_seconds)
            file_source.is_running = False
            file_source.save()
        except Exception as e:
            file_source.is_running = False
            file_source.save()
            print(e)


def file_source_scheduler_start():
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 5})
    # scheduler.add_jobstore(DjangoJobStore(), "file_sources_job_store")
    # run this job every 60 seconds
    # scheduler.add_job(process_file_sources, 'interval',
    #                  seconds=5, name='process_file_sources', jobstore='file_sources_job_store')
    scheduler.add_job(process_file_sources, 'interval', seconds=5)
    # register_events(scheduler)
    scheduler.start()
    print("Processing File Source", file=sys.stdout)
