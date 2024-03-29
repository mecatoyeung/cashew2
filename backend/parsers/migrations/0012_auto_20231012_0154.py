# Generated by Django 3.2.20 on 2023-10-11 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0011_documentpage_hocr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocr',
            name='activated',
        ),
        migrations.AlterField(
            model_name='ocr',
            name='ocr_type',
            field=models.CharField(choices=[('NO_OCR', 'NO_OCR'), ('GOOGLE_VISION', 'GOOGLE_VISION'), ('DOCTR', 'DOCTR')], default='NO_OCR', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='parser',
            name='type',
            field=models.CharField(choices=[('LAYOUT', 'LAYOUT'), ('ROUTING', 'ROUTING')], default='LAYOUT', max_length=255),
        ),
    ]
