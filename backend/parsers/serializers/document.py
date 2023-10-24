import os
import uuid
from rest_framework import serializers

from pathlib import Path

from pdf2image import convert_from_path
import PIL
from ..helpers.generate_images_from_pdf import generate_images_from_pdf
from ..helpers.parse_pdf_to_xml import parse_pdf_to_xml
from ..helpers.upload_document import upload_document
from ..helpers.create_queue_when_upload_document import create_queue_when_upload_document

from backend import settings

from ..models.document import Document
from ..models.document_page import DocumentPage
from ..models.queue_class import QueueClass
from ..models.queue import Queue

from .document_page import DocumentPageSerializer, DocumentPageDetailSerializer


class DocumentSerializer(serializers.ModelSerializer):

    document_pages = DocumentPageSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'parser',
            'guid',
            'file',
            'document_type',
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


class DocumentUploadSerializer(DocumentSerializer):
    """ Serializer for document upload view. """
    document_type = serializers.CharField(required=False, allow_null=True)
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
        filename_without_extension = file.name.split(".")[0]
        extension = file.name.split(".")[1].lower()
        validated_data["guid"] = guid
        validated_data["filename_without_extension"] = filename_without_extension
        validated_data["extension"] = extension
        validated_data["total_page_num"] = 1
        document = Document.objects.create(**validated_data)

        upload_document(document, file)
        create_queue_when_upload_document(document)
        generate_images_from_pdf(document)
        parse_pdf_to_xml(document)

        document.save()

        return document


class DocumentDetailSerializer(DocumentSerializer):
    """ Serializer for document detail view. """
    document_pages = DocumentPageDetailSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields
