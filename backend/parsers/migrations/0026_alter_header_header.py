# Generated by Django 3.2.20 on 2023-08-08 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0025_alter_stream_convert_to_table_by_specify_headers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='header',
            name='header',
            field=models.TextField(blank=True, default='', max_length=255, null=True),
        ),
    ]
