# Generated by Django 3.2.20 on 2023-10-11 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0010_auto_20231011_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentpage',
            name='hocr',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
