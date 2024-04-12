import os
import io
import uuid
from datetime import datetime

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from pathlib import Path

import PIL

from parsers.models.document import Document
from parsers.models.document_extension import DocumentExtension
from parsers.models.document_page import DocumentPage
from parsers.models.queue_class import QueueClass
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus
from parsers.models.parser import Parser

from parsers.serializers.queue import QueueSerializer
from parsers.serializers.document_page import DocumentPageSerializer, DocumentPageDetailSerializer

from parsers.helpers.generate_images_from_pdf import generate_images_from_pdf
from parsers.helpers.path_helpers import source_file_pdf_path, document_path

from backend import settings


class DocumentSerializer(serializers.ModelSerializer):

    queue = QueueSerializer(many=False, read_only=True)
    document_pages = DocumentPageSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'parser',
            'queue',
            'guid',
            'file',
            'document_type',
            'document_extension',
            'filename_without_extension',
            'extension',
            'total_page_num',
            'splitted',
            'last_modified_at',
            'document_pages',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a document. """
        document = Document.objects.create(**validated_data)

        return document

    def delete(self, request, pk, format=None):
        # delete document pages first
        DocumentPage.objects.delete(document_id=pk)
        # delete queue first
        Queue.objects.delete(document_id=pk)
        instance = self.get_object(pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentUploadSerializer(DocumentSerializer):
    """ Serializer for document upload view. """
    document_extension = serializers.CharField(required=False, allow_null=True)
    filename_without_extension = serializers.CharField(
        required=False, allow_null=True)
    extension = serializers.CharField(required=False, allow_null=True)
    total_page_num = serializers.IntegerField(required=False, allow_null=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields

    def pre_save(self, instance):
        folder_path = os.path.join(
            settings.MEDIA_ROOT, 'documents', instance.guid)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join('documents', instance.guid, "source_file.pdf")
        instance.file = filepath

    def create(self, validated_data):
        """ Create a document. """
        guid = str(uuid.uuid4())
        file = validated_data.pop("file")
        filename_without_extension = Path(file.name).stem
        extension = Path(file.name).suffix[1:]
        validated_data["guid"] = guid
        validated_data["filename_without_extension"] = filename_without_extension

        im = None
        if extension == "pdf" or extension == "PDF":
            validated_data["document_extension"] = DocumentExtension.PDF.value
        elif extension == "jpg" or extension == "JPG":
            image = PIL.Image.open(file)
            im = image.convert('RGB')
        elif extension == "png" or extension == "PNG":
            image = PIL.Image.open(file)
            im = image.convert('RGB')
        elif extension == "tiff" or extension == "TIFF":
            image = PIL.Image.open(file)
            im = image.convert('RGB')

        validated_data["extension"] = "pdf"
        validated_data["document_extension"] = "PDF"
        validated_data["last_modified_at"] = datetime.now()
        document = Document.objects.create(**validated_data)

        document.save()

        abs_document_path = document_path(document)
        is_folder_exist = os.path.exists(abs_document_path)
        if not is_folder_exist:
            os.makedirs(abs_document_path)
        abs_source_file_pdf_path = source_file_pdf_path(document)
        if im != None:
            im.save(abs_source_file_pdf_path)
        else:
            with open(abs_source_file_pdf_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        parser = Parser.objects.get(id=document.parser_id)

        generate_images_from_pdf(parser, document)

        # Create queue object in database
        q = Queue()
        q.queue_status = QueueStatus.READY.value
        q.parser = parser
        q.document = document
        q.queue_class = QueueClass.IMPORT.value
        q.save()

        return document


class DocumentDetailSerializer(DocumentSerializer):
    """ Serializer for document detail view. """
    document_pages = DocumentPageDetailSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields
