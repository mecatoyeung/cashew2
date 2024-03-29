# Generated by Django 3.2.23 on 2023-12-22 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0064_auto_20231222_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='splittingcondition',
            name='consecutive_page_splitting_rule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='splitting_conditions', to='parsers.consecutivepagesplittingrule'),
        ),
        migrations.AddField(
            model_name='splittingcondition',
            name='last_page_splitting_rule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='splitting_conditions', to='parsers.lastpagesplittingrule'),
        ),
        migrations.AlterField(
            model_name='splittingcondition',
            name='splitting_rule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='splitting_conditions', to='parsers.splittingrule'),
        ),
    ]
