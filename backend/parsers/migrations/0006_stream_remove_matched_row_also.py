# Generated by Django 3.2.20 on 2023-10-09 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0005_auto_20231009_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='remove_matched_row_also',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]