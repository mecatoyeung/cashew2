# Generated by Django 3.2.23 on 2024-03-14 03:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0082_rule_acrobat_form_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocr',
            name='ocr_text_layer_type',
        ),
        migrations.RemoveField(
            model_name='ocr',
            name='text_layer_preprocessing',
        ),
    ]
