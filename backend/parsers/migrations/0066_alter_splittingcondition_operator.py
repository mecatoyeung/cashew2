# Generated by Django 3.2.23 on 2024-01-03 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0065_auto_20231222_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='splittingcondition',
            name='operator',
            field=models.CharField(choices=[('EQUALS', 'EQUALS'), ('CONTAINS', 'CONTAINS'), ('DOES_NOT_CONTAINS', 'DOES_NOT_CONTAINS'), ('REGEX', 'REGEX'), ('NOT_REGEX', 'NOT_REGEX'), ('IS_EMPTY', 'IS_EMPTY'), ('IS_NOT_EMPTY', 'IS_NOT_EMPTY'), ('CHANGED', 'CHANGED'), ('NOT_CHANGED', 'NOT_CHANGED')], max_length=255),
        ),
    ]
