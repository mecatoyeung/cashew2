# Generated by Django 3.2.25 on 2024-04-10 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0096_alter_stream_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='json_extract_code',
            field=models.TextField(blank=True, default='', max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='stream',
            name='stream_class',
            field=models.CharField(choices=[('EXTRACT_FIRST_N_LINES', 'EXTRACT_FIRST_N_LINES'), ('EXTRACT_NTH_LINES', 'EXTRACT_NTH_LINES'), ('REGEX_EXTRACT', 'REGEX_EXTRACT'), ('REGEX_REPLACE', 'REGEX_REPLACE'), ('TRIM_SPACE', 'TRIM_SPACE'), ('REMOVE_TEXT_BEFORE_START_OF_TEXT', 'REMOVE_TEXT_BEFORE_START_OF_TEXT'), ('REMOVE_TEXT_BEFORE_END_OF_TEXT', 'REMOVE_TEXT_BEFORE_END_OF_TEXT'), ('REMOVE_TEXT_AFTER_START_OF_TEXT', 'REMOVE_TEXT_AFTER_START_OF_TEXT'), ('REMOVE_TEXT_AFTER_END_OF_TEXT', 'REMOVE_TEXT_AFTER_END_OF_TEXT'), ('REPLACE_TEXT', 'REPLACE_TEXT'), ('REPLACE_REGEX', 'REPLACE_REGEX'), ('JOIN_ALL_ROWS', 'JOIN_ALL_ROWS'), ('OPEN_AI', 'OPEN_AI'), ('COMBINE_FIRST_N_LINES', 'COMBINE_FIRST_N_LINES'), ('GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH', 'GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH'), ('TRIM_SPACE_FOR_ALL_ROWS_AND_COLS', 'TRIM_SPACE_FOR_ALL_ROWS_AND_COLS'), ('REMOVE_ROWS_WITH_CONDITIONS', 'REMOVE_ROWS_WITH_CONDITIONS'), ('MERGE_ROWS_WITH_CONDITIONS', 'MERGE_ROWS_WITH_CONDITIONS'), ('MERGE_ROWS_WITH_SAME_COLUMNS', 'MERGE_ROWS_WITH_SAME_COLUMNS'), ('REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS', 'REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS'), ('REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS', 'REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS'), ('UNPIVOT_TABLE', 'UNPIVOT_TABLE'), ('MAKE_FIRST_ROW_TO_BE_HEADER', 'MAKE_FIRST_ROW_TO_BE_HEADER'), ('REMOVE_EMPTY_LINES', 'REMOVE_EMPTY_LINES'), ('CONVERT_TO_TABLE_BY_SPECIFY_HEADERS', 'CONVERT_TO_TABLE_BY_SPECIFY_HEADERS'), ('EXTRACT_JSON_AS_TEXT', 'EXTRACT_JSON_AS_TEXT'), ('EXTRACT_JSON_AS_TABLE', 'EXTRACT_JSON_AS_TABLE')], max_length=256),
        ),
    ]
