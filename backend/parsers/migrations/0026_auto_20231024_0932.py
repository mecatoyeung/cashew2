# Generated by Django 3.2.20 on 2023-10-24 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0025_auto_20231024_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ocr',
            name='image_layer_preprocessing',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='parsers.preprocessing'),
        ),
        migrations.AlterField(
            model_name='ocr',
            name='text_layer_preprocessing',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='parsers.preprocessing'),
        ),
    ]