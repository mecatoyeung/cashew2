# Generated by Django 3.2.25 on 2024-04-16 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0098_rule_depends_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='lastpagesplittingrule',
            name='last_page_splitting_rule_type',
            field=models.CharField(choices=[('BY_CONDITIONS', 'BY_CONDITIONS'), ('WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH', 'WHEN_OTHER_FIRST_PAGE_SPLITTING_RULES_MATCH')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='stream',
            name='stream_class',
            field=models.CharField(choices=[('EXTRACT_FIRST_N_LINES', 'EXTRACT_FIRST_N_LINES'), ('EXTRACT_NTH_LINES', 'EXTRACT_NTH_LINES'), ('REGEX_EXTRACT', 'REGEX_EXTRACT'), ('REGEX_REPLACE', 'REGEX_REPLACE'), ('TRIM_SPACE', 'TRIM_SPACE'), ('REMOVE_TEXT_BEFORE_START_OF_TEXT', 'REMOVE_TEXT_BEFORE_START_OF_TEXT'), ('REMOVE_TEXT_BEFORE_END_OF_TEXT', 'REMOVE_TEXT_BEFORE_END_OF_TEXT'), ('REMOVE_TEXT_AFTER_START_OF_TEXT', 'REMOVE_TEXT_AFTER_START_OF_TEXT'), ('REMOVE_TEXT_AFTER_END_OF_TEXT', 'REMOVE_TEXT_AFTER_END_OF_TEXT'), ('REPLACE_TEXT', 'REPLACE_TEXT'), ('REPLACE_REGEX', 'REPLACE_REGEX'), ('JOIN_ALL_ROWS', 'JOIN_ALL_ROWS'), ('OPEN_AI_TEXT', 'OPEN_AI_TEXT'), ('COMBINE_FIRST_N_LINES', 'COMBINE_FIRST_N_LINES'), ('GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH', 'GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH'), ('TRIM_SPACE_FOR_ALL_ROWS_AND_COLS', 'TRIM_SPACE_FOR_ALL_ROWS_AND_COLS'), ('REMOVE_ROWS_WITH_CONDITIONS', 'REMOVE_ROWS_WITH_CONDITIONS'), ('MERGE_ROWS_WITH_CONDITIONS', 'MERGE_ROWS_WITH_CONDITIONS'), ('MERGE_ROWS_WITH_SAME_COLUMNS', 'MERGE_ROWS_WITH_SAME_COLUMNS'), ('REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS', 'REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS'), ('REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS', 'REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS'), ('UNPIVOT_TABLE', 'UNPIVOT_TABLE'), ('MAKE_FIRST_ROW_TO_BE_HEADER', 'MAKE_FIRST_ROW_TO_BE_HEADER'), ('OPEN_AI_TABLE', 'OPEN_AI_TABLE'), ('REMOVE_EMPTY_LINES', 'REMOVE_EMPTY_LINES'), ('CONVERT_TO_TABLE_BY_SPECIFY_HEADERS', 'CONVERT_TO_TABLE_BY_SPECIFY_HEADERS'), ('EXTRACT_JSON_AS_TEXT', 'EXTRACT_JSON_AS_TEXT'), ('EXTRACT_JSON_AS_TABLE', 'EXTRACT_JSON_AS_TABLE')], max_length=256),
        ),
    ]
