# Generated by Django 3.2.20 on 2023-10-17 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0013_auto_20231013_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='queue_class',
            field=models.CharField(choices=[('PROCESSED', 'PROCESSED'), ('IMPORT', 'IMPORT'), ('PREPROCESSING', 'PREPROCESSING'), ('OCR', 'OCR'), ('SPLITTING', 'SPLITTING'), ('PARSING', 'PARSING'), ('POST_PROCESSING', 'POSTPROCESSING'), ('INTEGRATION', 'INTEGRATION')], max_length=255),
        ),
    ]
