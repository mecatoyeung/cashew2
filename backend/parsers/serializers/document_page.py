from rest_framework import serializers

from parsers.models.document_page import DocumentPage


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

    def create(self, validated_data):
        """ Create a document page. """
        document = DocumentPage.objects.create(**validated_data)

        return document

    def update(self, instance, validated_data):
        """ Update document page. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class DocumentPageDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentPage
        fields = [
            'id',
            'document',
            'page_num',
            'width',
            'height',
            'xml',
            'ocred',
            'chatbot_completed'
        ]
        read_only_fields = ['id']
