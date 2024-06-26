# Generated by Django 3.2.25 on 2024-04-05 00:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('parsers', '0090_auto_20240405_0818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parser',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='parser',
            name='permitted_groups',
            field=models.ManyToManyField(related_name='group_permitted_parser', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='parser',
            name='permitted_users',
            field=models.ManyToManyField(related_name='user_permitted_parser', to=settings.AUTH_USER_MODEL),
        ),
    ]
