# Generated by Django 3.2.23 on 2024-01-23 08:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0066_alter_splittingcondition_operator'),
    ]

    operations = [
        migrations.AddField(
            model_name='preprocessing',
            name='threshold_binarization',
            field=models.IntegerField(blank=True, default=170, null=True, validators=[django.core.validators.MaxValueValidator(255), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(choices=[('TEMPLATE', 'TEMPLATE'), ('IMPORT', 'IMPORT'), ('TRASH', 'TRASH')], max_length=255),
        ),
        migrations.AlterField(
            model_name='preprocessing',
            name='pre_processing_type',
            field=models.CharField(choices=[('ORIENTATION_DETECTION', 'ORIENTATION_DETECTION'), ('THRESHOLD_BINARIZATION', 'THRESHOLD_BINARIZATION')], max_length=255),
        ),
        migrations.AlterField(
            model_name='queue',
            name='queue_class',
            field=models.CharField(choices=[('PROCESSED', 'PROCESSED'), ('IMPORT', 'IMPORT'), ('PRE_PROCESSING', 'PRE_PROCESSING'), ('OCR', 'OCR'), ('SPLITTING', 'SPLITTING'), ('AICHAT', 'AICHAT'), ('PARSING', 'PARSING'), ('POST_PROCESSING', 'POST_PROCESSING'), ('INTEGRATION', 'INTEGRATION'), ('TRASH', 'TRASH')], max_length=255),
        ),
    ]