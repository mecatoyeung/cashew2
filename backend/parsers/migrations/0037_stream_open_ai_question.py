# Generated by Django 3.2.23 on 2023-11-10 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0036_auto_20231110_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='open_ai_question',
            field=models.TextField(blank=True, default='', max_length=4096, null=True),
        ),
    ]
