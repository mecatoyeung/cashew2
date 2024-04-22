import copy
import traceback
import json

from django.db.models import Prefetch
from django.core import serializers
from django.forms.models import model_to_dict

from parsers.models.parser import Parser
from ..models.rule_type import RuleType
from ..models.rule import Rule
from ..models.stream import Stream
from .rule_extractor import RuleExtractor
from parsers.helpers.stream_processors.textfield.extract_first_n_lines import ExtractFirstNLinesStreamProcessor
from parsers.helpers.stream_processors.textfield.extract_nth_lines import ExtractNthLinesStreamProcessor
from parsers.helpers.stream_processors.textfield.regex_extract import RegexExtractStreamProcessor
from parsers.helpers.stream_processors.textfield.regex_replace import RegexReplaceStreamProcessor
from parsers.helpers.stream_processors.textfield.join_all_rows import JoinAllRowsStreamProcessor
from parsers.helpers.stream_processors.textfield.trim_space import TrimSpaceStreamProcessor
from parsers.helpers.stream_processors.textfield.remove_text_before_start_of_text import RemoveTextBeforeStartOfTextStreamProcessor
from parsers.helpers.stream_processors.textfield.remove_text_before_end_of_text import RemoveTextBeforeEndOfTextStreamProcessor
from parsers.helpers.stream_processors.textfield.remove_text_after_start_of_text import RemoveTextAfterStartOfTextStreamProcessor
from parsers.helpers.stream_processors.textfield.remove_text_after_end_of_text import RemoveTextAfterEndOfTextStreamProcessor
from parsers.helpers.stream_processors.textfield.convert_to_table_by_specify_header import ConvertToTableBySpecifyHeaderStreamProcessor
from parsers.helpers.stream_processors.textfield.remove_empty_lines import RemoveEmptyLinesStreamProcessor
from parsers.helpers.stream_processors.textfield.openai import OpenAITextStreamProcessor

from parsers.helpers.stream_processors.table.combine_first_n_lines import CombineFirstNLinesStreamProcessor
from parsers.helpers.stream_processors.table.get_chars_from_next_col_if_regex_not_match import GetCharsFromNextColIfRegexNotMatchStreamProcessor
from parsers.helpers.stream_processors.table.trim_space import TrimSpaceTableStreamProcessor
from parsers.helpers.stream_processors.table.remove_rows_with_conditions import RemoveRowsWithConditionsStreamProcessor
from parsers.helpers.stream_processors.table.merge_rows_with_conditions import MergeRowsWithConditionsStreamProcessor
from parsers.helpers.stream_processors.table.merge_rows_with_same_columns import MergeRowsWithSameColumnsStreamProcessor
from parsers.helpers.stream_processors.table.remove_rows_before_row_with_conditions import RemoveRowsBeforeRowWithConditionsStreamProcessor
from parsers.helpers.stream_processors.table.remove_rows_after_row_with_conditions import RemoveRowsAfterRowWithConditionsStreamProcessor
from parsers.helpers.stream_processors.table.unpivot_column import UnpivotColumnStreamProcessor
from parsers.helpers.stream_processors.table.make_first_row_to_be_header import MakeFirstRowToBeHeaderStreamProcessor
from parsers.helpers.stream_processors.json.extract_json_as_text import ExtractJSONAsTextStreamProcessor
from parsers.helpers.stream_processors.json.extract_json_as_table import ExtractJSONAsTableStreamProcessor
from parsers.helpers.stream_processors.table.openai import OpenAITableStreamProcessor

STREAM_PROCESSOR_MAPPING = {
    "EXTRACT_FIRST_N_LINES": ExtractFirstNLinesStreamProcessor,
    "EXTRACT_NTH_LINES": ExtractNthLinesStreamProcessor,
    "REGEX_EXTRACT": RegexExtractStreamProcessor,
    "REGEX_REPLACE": RegexReplaceStreamProcessor,
    "JOIN_ALL_ROWS": JoinAllRowsStreamProcessor,
    "TRIM_SPACE": TrimSpaceStreamProcessor,
    "TRIM_SPACE_FOR_ALL_ROWS_AND_COLS": TrimSpaceTableStreamProcessor,
    "REMOVE_EMPTY_LINES": RemoveEmptyLinesStreamProcessor,
    "OPEN_AI_TEXT": OpenAITextStreamProcessor,
    "REMOVE_TEXT_BEFORE_START_OF_TEXT": RemoveTextBeforeStartOfTextStreamProcessor,
    "REMOVE_TEXT_BEFORE_END_OF_TEXT": RemoveTextBeforeEndOfTextStreamProcessor,
    "REMOVE_TEXT_AFTER_START_OF_TEXT": RemoveTextAfterStartOfTextStreamProcessor,
    "REMOVE_TEXT_AFTER_END_OF_TEXT": RemoveTextAfterEndOfTextStreamProcessor,
    "COMBINE_FIRST_N_LINES": CombineFirstNLinesStreamProcessor,
    "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS": ConvertToTableBySpecifyHeaderStreamProcessor,
    "GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH": GetCharsFromNextColIfRegexNotMatchStreamProcessor,
    "MERGE_ROWS_WITH_SAME_COLUMNS": MergeRowsWithSameColumnsStreamProcessor,
    "REMOVE_ROWS_WITH_CONDITIONS": RemoveRowsWithConditionsStreamProcessor,
    "MERGE_ROWS_WITH_CONDITIONS": MergeRowsWithConditionsStreamProcessor,
    "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS": RemoveRowsBeforeRowWithConditionsStreamProcessor,
    "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS": RemoveRowsAfterRowWithConditionsStreamProcessor,
    "UNPIVOT_TABLE": UnpivotColumnStreamProcessor,
    "MAKE_FIRST_ROW_TO_BE_HEADER": MakeFirstRowToBeHeaderStreamProcessor,
    "OPEN_AI_TABLE": OpenAITableStreamProcessor,
    "EXTRACT_JSON_AS_TEXT": ExtractJSONAsTextStreamProcessor,
    "EXTRACT_JSON_AS_TABLE": ExtractJSONAsTableStreamProcessor
}


def convert_to_table_by_specify_headers_map(object):
    return object.header.header


class StreamProcessor:

    def __init__(self, rule):
        self.rule = rule

    def process(self, extracted):

        streams = Stream.objects.filter(rule_id=self.rule.id) \
            .prefetch_related('streamcondition_set') \
            .order_by('step')

        processedStreams = []

        processedStreams.append({
            "step": 0,
            "type": extracted["type"],
            "data": {
                "type":extracted["type"],
                "value": extracted["value"]
            }
        })

        last_processed_data = extracted
        has_error = False

        for streamIndex in range(len(streams)):

            if streams[streamIndex].stream_class in STREAM_PROCESSOR_MAPPING:
                sp = STREAM_PROCESSOR_MAPPING[streams[streamIndex].stream_class](
                    streams[streamIndex])
            else:
                raise Exception("No such stream")

            """if streams[streamIndex].stream_class == "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS":
                streams[streamIndex].type = "TABLE"

            if streams[streamIndex].stream_class == "OPEN_AI_TEXT":
                streams[streamIndex].type = "JSON"

            if streams[streamIndex].stream_class == "OPEN_AI_TABLE":
                streams[streamIndex].type = "JSON"

            if streams[streamIndex].stream_class == "EXTRACT_JSON_AS_TEXT":
                streams[streamIndex].type = "TEXTFIELD"

            if streams[streamIndex].stream_class == "EXTRACT_JSON_AS_TABLE":
                streams[streamIndex].type = "TABLE"""

            """if processedStreams[-1]["step"] != 0 and processedStreams[-1]["status"] == "error":
                processedStreams.append({
                    "status": "error",
                    "error_message": "Please correct the error in the above step first.",
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].type,
                    "class": streams[streamIndex].stream_class,
                    "col_index": streams[streamIndex].col_index,
                    "col_indexes": streams[streamIndex].col_indexes,
                    "remove_matched_row_also": streams[streamIndex].remove_matched_row_also,
                    "text": streams[streamIndex].text,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_lines": streams[streamIndex].extract_nth_lines,
                    "open_ai_question": streams[streamIndex].open_ai_question,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "convert_to_table_by_specify_headers": streams[streamIndex].convert_to_table_by_specify_headers,
                    "unpivot_column_index": streams[streamIndex].unpivot_column_index,
                    "unpivot_newline_char": streams[streamIndex].unpivot_newline_char,
                    "unpivot_property_assign_char": streams[streamIndex].unpivot_property_assign_char,
                    "stream_conditions": [model_to_dict(condition) for condition in streams[streamIndex].streamcondition_set.all()],
                    "json_extract_code": streams[streamIndex].json_extract_code
                })
                continue"""

            try:
                if not has_error:
                    processed_data = sp.process(last_processed_data)
                else:
                    processed_data = last_processed_data
                processedStreams.append({
                    "status": "success",
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": processed_data["type"],
                    "class": streams[streamIndex].stream_class,
                    "col_index": streams[streamIndex].col_index,
                    "col_indexes": streams[streamIndex].col_indexes,
                    "remove_matched_row_also": streams[streamIndex].remove_matched_row_also,
                    "text": streams[streamIndex].text,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_lines": streams[streamIndex].extract_nth_lines,
                    "open_ai_question": streams[streamIndex].open_ai_question,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "convert_to_table_by_specify_headers": streams[streamIndex].convert_to_table_by_specify_headers,
                    "unpivot_column_index": streams[streamIndex].unpivot_column_index,
                    "unpivot_newline_char": streams[streamIndex].unpivot_newline_char,
                    "unpivot_property_assign_char": streams[streamIndex].unpivot_property_assign_char,
                    "stream_conditions": [model_to_dict(condition) for condition in streams[streamIndex].streamcondition_set.all()],
                    "json_extract_code": streams[streamIndex].json_extract_code,
                    "data": processed_data
                })
                last_processed_data = processed_data
            except Exception as e:
                print(traceback.format_exc())
                processedStreams.append({
                    "status": "error",
                    "error_message": str(e),
                    "data": {
                        "type": "TEXTFIELD",
                        "value": [str(e)]
                    },
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": last_processed_data["type"],
                    "class": streams[streamIndex].stream_class,
                    "col_index": streams[streamIndex].col_index,
                    "col_indexes": streams[streamIndex].col_indexes,
                    "remove_matched_row_also": streams[streamIndex].remove_matched_row_also,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_lines": streams[streamIndex].extract_nth_lines,
                    "open_ai_question": streams[streamIndex].open_ai_question,
                    "text": streams[streamIndex].text,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "convert_to_table_by_specify_headers": streams[streamIndex].convert_to_table_by_specify_headers,
                    "unpivot_column_index": streams[streamIndex].unpivot_column_index,
                    "unpivot_newline_char": streams[streamIndex].unpivot_newline_char,
                    "unpivot_property_assign_char": streams[streamIndex].unpivot_property_assign_char,
                    "stream_conditions": [model_to_dict(condition) for condition in streams[streamIndex].streamcondition_set.all()],
                    "json_extract_code": streams[streamIndex].json_extract_code
                })
                has_error = True

        return processedStreams
