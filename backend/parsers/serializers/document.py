import os
import uuid
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from pathlib import Path

from pdf2image import convert_from_path
import PIL

from parsers.models.document import Document
from parsers.models.document_type import DocumentType
from parsers.models.document_extension import DocumentExtension
from parsers.models.document_page import DocumentPage
from parsers.models.queue_class import QueueClass
from parsers.models.queue import Queue

from parsers.serializers.queue import QueueSerializer
from parsers.serializers.document_page import DocumentPageSerializer, DocumentPageDetailSerializer

from parsers.helpers.generate_images_from_pdf import generate_images_from_pdf
from parsers.helpers.parse_pdf_to_xml import parse_pdf_to_xml
from parsers.helpers.upload_document import upload_document
from parsers.helpers.create_queue_when_upload_document import create_queue_when_upload_document

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
        filename_without_extension = os.path.basename(file.name).split(".")[0]
        extension = file.name.split(".")[1].lower()
        validated_data["guid"] = guid
        validated_data["filename_without_extension"] = filename_without_extension
        if extension == "pdf" or extension == "PDF":
            validated_data["document_extension"] = DocumentExtension.PDF.value
        validated_data["extension"] = extension
        document = Document.objects.create(**validated_data)

        document.save()

        upload_document(document, file)
        generate_images_from_pdf(document)
        create_queue_when_upload_document(document)

        return document


class DocumentDetailSerializer(DocumentSerializer):
    """ Serializer for document detail view. """
    document_pages = DocumentPageDetailSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields