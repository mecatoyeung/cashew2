# Generated by Django 3.2.23 on 2024-03-19 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0085_integration_guid'),
    ]

    operations = [
        migrations.AddField(
            model_name='ocr',
            name='detect_searchable',
            field=models.BooleanField(default=False),
        ),
    ]