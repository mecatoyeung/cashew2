import os
import shutil
import glob

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from parsers.models.document import Document
from parsers.models.document_page import DocumentPage
from parsers.models.queue import Queue
from parsers.models.queue_status import QueueStatus

from backend import settings


class DocumentPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentPage
        fields = [
            'id',
            'document',
            'page_num',
            'width',
            'height',
            'ocred',
            'chatbot_completed'
        ]
        read_only_fields = ['id']


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
            'document_extension',
            'filename_without_extension',
            'extension',
            'total_page_num',
            'last_modified_at',
            'document_pages',
        ]
        read_only_fields = ['id']


class QueueSerializer(serializers.ModelSerializer):

    document = DocumentSerializer(
        many=False, required=False, allow_null=True)

    class Meta:
        model = Queue
        fields = [
            'id',
            'guid',
            'document',
            'parser',
            'queue_class',
            'input_result',
            'parsed_result',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a queue. """
        queue = Queue.objects.create(**validated_data)

        return queue

    def update(self, instance, validated_data):
        """ Update queue. """
        for attr, value in validated_data.items():
            if attr == "document":
                continue
            if attr == "queue_class" and value == "OCR":
                document_pages = DocumentPage.objects.filter(
                    document__queue__id=instance.pk)
                for document_page in document_pages:
                    document_page.ocred = False
                    document_page.save()
            setattr(instance, attr, value)

        instance.queue_status = QueueStatus.READY.value
        instance.save()
        return instance

    """def delete(self, request, pk, format=None):
        instance = self.get_object(pk)
        # delete documents folder first
        document_folder = os.path.join(
            settings.MEDIA_ROOT, 'documents', instance.guid)
        files = glob.glob(document_folder)
        for f in files:
            os.remove(f)
        shutil.rmtree(document_folder)
        # delete document pages first
        DocumentPage.objects.delete(document__queue_id=pk)
        # delete document first
        Document.objects.delete(queue_id=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)"""
