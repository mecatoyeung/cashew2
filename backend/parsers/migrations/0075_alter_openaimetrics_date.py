# Generated by Django 3.2.23 on 2024-02-15 08:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0074_openaimetrics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openaimetrics',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
