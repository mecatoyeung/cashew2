# Generated by Django 3.2.23 on 2023-12-04 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0055_remove_documentpage_image_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentpage',
            name='postprocessed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='documentpage',
            name='preprocessed',
            field=models.BooleanField(default=False),
        ),
    ]