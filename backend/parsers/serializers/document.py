import os
import uuid
from rest_framework import serializers

from pathlib import Path

from pdf2image import convert_from_path
import PIL
from ..helpers.generate_images_from_pdf import generate_images_from_pdf
from ..helpers.parse_pdf_to_xml import parse_pdf_to_xml
from ..helpers.convert_pdf import convert_pdf

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
    #source_file = serializers.FileField(required=False, allow_null=True)
    filename_without_extension = serializers.CharField(required=False, allow_null=True)
    extension = serializers.CharField(required=False, allow_null=True)
    total_page_num = serializers.IntegerField(required=False, allow_null=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields

    def pre_save(self, instance):
        folder_path = os.path.join(settings.MEDIA_ROOT, 'documents', instance.guid)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join('documents', instance.guid, "source_file.pdf")
        instance.file = filepath

    def create(self, validated_data):
        """ Create a document. """
        guid = str(uuid.uuid4())
        folder_path = os.path.join(settings.MEDIA_ROOT, 'documents', guid)
        abs_file_path = os.path.join(folder_path, "source_file.pdf")
        file = validated_data.pop("file")
        filename_without_extension = file.name.split(".")[0]
        extension = file.name.split(".")[1].lower()
        validated_data["guid"] = guid
        validated_data["filename_without_extension"] = filename_without_extension
        validated_data["extension"] = extension
        validated_data["total_page_num"] = 1
        document = Document.objects.create(**validated_data)

        generate_images_from_pdf(document)
        parse_pdf_to_xml(document)


        """
        # Copy file to document folder
        folder_path = os.path.join(settings.MEDIA_ROOT, 'documents', guid)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        abs_filepath = os.path.join(folder_path, "source_file.pdf")
        # with open(abs_filepath, "wb") as f:
        with open(abs_filepath, "wb") as f:
            f.write(file.read())

        q = Queue()
        q.document = document
        q.queue_class = QueueClass.PARSING.value
        q.parser = document.parser
        q.save()

        folder_path = os.path.join(settings.MEDIA_ROOT, 'documents', document.guid)
        abs_file_path = os.path.join(folder_path, "source_file.pdf")
        pdf_images = convert_from_path(abs_file_path, poppler_path=os.path.join(settings.BASE_DIR, "parsers", "poppler", "Library", "bin"))
        for page_idx, pdf_image in enumerate(pdf_images):
            page_no = page_idx + 1
            png_path = os.path.join(
                'documents', document.guid, "original-" + str(page_no) + ".png")
            full_png_path = os.path.join(settings.MEDIA_ROOT, png_path)
            pdf_image.save(full_png_path, 'PNG')

            image = PIL.Image.open(full_png_path)
            width, height = image.size

            xml = convert_pdf(
                path=abs_file_path,
                pagenos=[page_idx]
            )
            # fix bug in library
            xml = xml + "</pages>"

            # Create document page object in database
            dp = DocumentPage(
                document=document,
                page_num=page_no,
                image_file=png_path,
                width=width,
                height=height,
                xml=xml
            )
            dp.save()
        """



        document.total_page_num = len(pdf_images)
        document.save()

        return document

class DocumentDetailSerializer(DocumentSerializer):
    """ Serializer for document detail view. """
    document_pages = DocumentPageDetailSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields

