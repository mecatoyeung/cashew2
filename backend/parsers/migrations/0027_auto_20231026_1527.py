# Generated by Django 3.2.20 on 2023-10-26 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0026_auto_20231024_0932'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='integration',
            name='post_processing',
        ),
        migrations.RemoveField(
            model_name='integration',
            name='pre_processing',
        ),
        migrations.AddField(
            model_name='integration',
            name='postprocessing',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='postprocessing', to='parsers.postprocessing'),
        ),
        migrations.AddField(
            model_name='integration',
            name='preprocessing',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='preprocessing', to='parsers.preprocessing'),
        ),
        migrations.AddField(
            model_name='splittingrule',
            name='parent_splitting_rule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='consecutive_page_splitting_rules', to='parsers.splittingrule'),
        ),
        migrations.AddField(
            model_name='splittingrule',
            name='splitting_rule_type',
            field=models.CharField(choices=[('FIRST_PAGE', 'FIRST_PAGE'), (
                'CONSECUTIVE_PAGE', 'CONSECUTIVE_PAGE')], default='FIRST_PAGE', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ocr',
            name='image_layer_preprocessing',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='image_layer_preprocessing', to='parsers.preprocessing'),
        ),
        migrations.AlterField(
            model_name='ocr',
            name='text_layer_preprocessing',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='text_layer_preprocessing', to='parsers.preprocessing'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='rule_type',
            field=models.CharField(choices=[('INPUT_TEXTFIELD', 'INPUT_TEXTFIELD'), ('INPUT_DROPDOWN', 'INPUT_DROPDOWN'), ('TEXTFIELD', 'TEXTFIELD'), (
                'ANCHORED_TEXTFIELD', 'ANCHORED_TEXTFIELD'), ('TABLE', 'TABLE'), ('ACROBAT_FORM', 'ACROBAT_FORM'), ('BARCODE', 'BARCODE'), ('DEPENDENT_RULE', 'DEPENDENT_RULE')], max_length=255),
        ),
    ]
