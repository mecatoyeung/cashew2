# Generated by Django 3.2.23 on 2023-11-28 04:05

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0051_alter_document_document_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='postprocessing',
            name='guid',
            field=models.CharField(default=uuid.uuid4, max_length=255),
        ),
        migrations.AddField(
            model_name='preprocessing',
            name='guid',
            field=models.CharField(default=uuid.uuid4, max_length=255),
        ),
        migrations.AlterField(
            model_name='ocr',
            name='parser',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ocr', to='parsers.parser'),
        ),
        migrations.AlterField(
            model_name='splitting',
            name='parser',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='splitting', to='parsers.parser'),
        ),
    ]