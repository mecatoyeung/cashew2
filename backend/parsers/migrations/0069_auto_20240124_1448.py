# Generated by Django 3.2.23 on 2024-01-24 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0068_auto_20240124_1205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consecutivepagesplittingcondition',
            old_name='consecutive_routing_rule',
            new_name='consecutive_page_splitting_rule',
        ),
        migrations.RenameField(
            model_name='lastpagesplittingcondition',
            old_name='last_page_routing_rule',
            new_name='last_page_splitting_rule',
        ),
    ]
