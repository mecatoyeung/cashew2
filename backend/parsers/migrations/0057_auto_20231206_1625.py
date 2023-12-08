# Generated by Django 3.2.23 on 2023-12-06 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0056_auto_20231204_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbot',
            name='base_url',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='chatbot',
            name='chatbot_type',
            field=models.CharField(choices=[('NO_CHATBOT', 'NO_CHATBOT'), ('OPEN_AI', 'OPEN_AI'), ('ON_PREMISE_AI', 'ON_PREMISE_AI')], default='NO_CHATBOT', max_length=255, null=True),
        ),
    ]
