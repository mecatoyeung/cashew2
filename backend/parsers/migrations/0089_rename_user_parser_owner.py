# Generated by Django 3.2.25 on 2024-04-03 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0088_parser_pdf_to_image_dpi'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parser',
            old_name='user',
            new_name='owner',
        ),
    ]
