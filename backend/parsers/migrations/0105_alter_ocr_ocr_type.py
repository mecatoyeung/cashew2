# Generated by Django 3.2.25 on 2024-07-01 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0104_remove_documentpage_chatbot_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ocr',
            name='ocr_type',
            field=models.CharField(choices=[('NO_OCR', 'NO_OCR'), ('GOOGLE_VISION', 'GOOGLE_VISION'), ('DOCTR', 'DOCTR'), ('PADDLE', 'PADDLE'), ('OMNIPAGE', 'OMNIPAGE'), ('APPLE_VISION', 'APPLE_VISION')], default='NO_OCR', max_length=255, null=True),
        ),
    ]
