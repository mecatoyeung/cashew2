from rest_framework import serializers

from parsers.models.ocr import OCR

from parsers.serializers.rule import RuleSerializer


class OCRSerializer(serializers.ModelSerializer):

    google_vision_ocr_api_key = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = OCR
        fields = ['id', 'guid', 'ocr_type', 'google_vision_ocr_api_key']
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
