# Generated by Django 3.2.23 on 2023-11-09 03:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0032_splitting_activated'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIChat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('guid', models.CharField(default=uuid.uuid4, max_length=255)),
                ('enabled', models.BooleanField(default=False)),
                ('parser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='parsers.parser')),
            ],
            options={
                'db_table': 'ai_chats',
            },
        ),
    ]