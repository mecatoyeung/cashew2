# Generated by Django 3.2.23 on 2024-02-16 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0075_alter_openaimetrics_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='parser',
            name='total_num_of_pages_processed',
            field=models.IntegerField(default=0),
        ),
    ]
