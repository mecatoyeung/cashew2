from rest_framework import serializers

from rest_access_policy import FieldAccessMixin

from parsers.models.ocr import OCR

from parsers.serializers.rule import RuleSerializer


class OCRSerializer(serializers.ModelSerializer):

    google_vision_ocr_api_key = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = OCR
        fields = ['id', 'guid', 'ocr_type',
                  'google_vision_ocr_api_key', 'paddle_ocr_language', 
                  'omnipage_ocr_language', 
                  'apple_vision_ocr_language',
                  'ocr_image_layer_type', 'image_layer_preprocessing', 
                  'detect_searchable',
                  'debug']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a parser. """
        ocr = OCR.objects.create(**validated_data)

        return ocr

    def update(self, instance, validated_data):
        """ Update parser. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ProtectedOCRSerializer(serializers.ModelSerializer):

    class Meta:
        model = OCR
        fields = ['id', 'guid', 'ocr_type',
                  'paddle_ocr_language', 
                  'omnipage_ocr_language', 
                  'apple_vision_ocr_language',
                  'ocr_image_layer_type', 'image_layer_preprocessing', 
                  'detect_searchable',
                  'debug']
        read_only_fields = ['id']