import os
import shutil
import glob

from django.db import transaction

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema_field

from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue
from parsers.models.queue import QueueClass
from parsers.models.queue_status import QueueStatus

#from parsers.serializers.nested.document import DocumentSerializer

from backend import settings


class QueueDocumentPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentPage
        fields = [
            'id',
            'document',
            'page_num',
            'width',
            'height',
            'preprocessed',
            'ocred',
            'postprocessed',
            'chatbot_completed'
        ]
        read_only_fields = ['id']

class QueueDocumentSerializer(serializers.ModelSerializer):

    document_pages = QueueDocumentPageSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'parser',
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

class QueueSerializer(serializers.ModelSerializer):


    document = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = [
            'id',
            'guid',
            'document',
            'parser',
            'queue_class',
            'queue_status',
            'input_result',
            'parsed_result',
        ]
        read_only_fields = ['id']

    @extend_schema_field(QueueDocumentSerializer)
    def get_document(self, obj):
        return QueueDocumentSerializer(obj.document).data

    def create(self, validated_data):
        """ Create a queue. """
        queue = Queue.objects.create(**validated_data)

        return queue

    def update(self, instance, validated_data):
        """ Update queue. """
        for attr, value in validated_data.items():
            if attr == "document":
                continue
            if attr == "queue_class" and value == QueueClass.PROCESSED.value:
                document_pages = DocumentPage.objects.filter(
                    document__queue__id=instance.pk)
                for document_page in document_pages:
                    document_page.preprocessed = False
                    document_page.ocred = False
                    document_page.postprocessed = False
                    document_page.save()
            if attr == "queue_class" and value == QueueClass.PRE_PROCESSING.value:
                document_pages = DocumentPage.objects.filter(
                    document__queue__id=instance.pk)
                for document_page in document_pages:
                    document_page.preprocessed = False
                    document_page.ocred = False
                    document_page.postprocessed = False
                    document_page.save()
            if attr == "queue_class" and value == QueueClass.OCR.value:
                document_pages = DocumentPage.objects.filter(
                    document__queue__id=instance.pk)
                for document_page in document_pages:
                    document_page.preprocessed = False
                    document_page.ocred = False
                    document_page.postprocessed = False
                    document_page.save()
            if attr == "queue_class" and value == QueueClass.POST_PROCESSING.value:
                document_pages = DocumentPage.objects.filter(
                    document__queue__id=instance.pk)
                for document_page in document_pages:
                    document_page.preprocessed = False
                    document_page.ocred = False
                    document_page.postprocessed = False
                    document_page.save()
            setattr(instance, attr, value)

        instance.save()
        return instance
