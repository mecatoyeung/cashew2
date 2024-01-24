from parsers.models.document import Document
from parsers.models.document_page import DocumentPage

from rest_framework import serializers

class DocumentPageSerializer(serializers.ModelSerializer):

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