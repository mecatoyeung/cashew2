# Generated by Django 3.2.20 on 2023-10-09 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0004_auto_20231009_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routingcondition',
            name='operator',
            field=models.CharField(choices=[('EQUALS', 'EQUALS'), ('CONTAINS', 'CONTAINS'), ('REGEX', 'REGEX'), ('IS_EMPTY', 'IS_EMPTY'), ('IS_NOT_EMPTY', 'IS_NOT_EMPTY')], max_length=255),
        ),
        migrations.AlterField(
            model_name='streamcondition',
            name='operator',
            field=models.CharField(choices=[('EQUALS', 'EQUALS'), ('CONTAINS', 'CONTAINS'), ('REGEX', 'REGEX'), ('IS_EMPTY', 'IS_EMPTY'), ('IS_NOT_EMPTY', 'IS_NOT_EMPTY')], max_length=255),
        ),
    ]
