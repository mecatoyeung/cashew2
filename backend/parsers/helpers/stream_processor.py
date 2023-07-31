import copy

from ..models.rule_type import RuleType
from ..models.rule import Rule
from ..models.stream import Stream
from .rule_extractor import RuleExtractor
from .stream_processors.textfield.extract_first_n_lines import ExtractFirstNLinesStreamProcessor
from .stream_processors.textfield.extract_nth_lines import ExtractNthLinesStreamProcessor
from .stream_processors.textfield.regex_extract import RegexExtractStreamProcessor
from .stream_processors.textfield.regex_replace import RegexReplaceStreamProcessor
from .stream_processors.textfield.join_all_rows import JoinAllRowsStreamProcessor
from .stream_processors.textfield.trim_space import TrimSpaceStreamProcessor
from .stream_processors.textfield.remove_text_before_start_of_text import RemoveTextBeforeStartOfTextStreamProcessor
from .stream_processors.textfield.remove_text_before_end_of_text import RemoveTextBeforeEndOfTextStreamProcessor
from .stream_processors.textfield.remove_text_after_start_of_text import RemoveTextAfterStartOfTextStreamProcessor
from .stream_processors.textfield.remove_text_after_end_of_text import RemoveTextAfterEndOfTextStreamProcessor
from .stream_processors.textfield.convert_to_table_by_specify_header import ConvertToTableBySpecifyHeaderStreamProcessor
from .stream_processors.textfield.remove_empty_lines import RemoveEmptyLinesStreamProcessor
from .stream_processors.table.combine_first_n_lines import CombineFirstNLinesStreamProcessor
from .stream_processors.table.get_chars_from_next_col_when_regex_not_match import GetCharsFromNextColWhenRegexNotMatchStreamProcessor
from .stream_processors.table.trim_space import TrimSpaceTableStreamProcessor
from .stream_processors.table.remove_rows_with_conditions import RemoveRowsWithConditionsStreamProcessor
from .stream_processors.table.merge_rows_with_conditions import MergeRowsWithConditionsStreamProcessor
from .stream_processors.table.merge_rows_with_same_columns import MergeRowsWithSameColumnsStreamProcessor
from .stream_processors.table.remove_rows_before_row_with_conditions import RemoveRowsBeforeRowWithConditionsStreamProcessor
from .stream_processors.table.remove_rows_after_row_with_conditions import RemoveRowsAfterRowWithConditionsStreamProcessor
from .stream_processors.table.unpivot_column import UnpivotColumnStreamProcessor
from .stream_processors.table.make_first_row_to_be_header import MakeFirstRowToBeHeaderStreamProcessor

class StreamProcessor:

    def __init__(self, rule):
        self.rule = rule

    def process(self, document):

        rule_extractor = RuleExtractor(self.rule, document)

        streams = Stream.objects.filter(rule_id=self.rule.id).order_by('step')

        rule_raw_result = rule_extractor.extract()
        inputStream = rule_raw_result

        processedStreams = []
        processedStreams.append({
            "step": 0,
            "type": self.rule.rule_type,
            "data": inputStream
        })

        for streamIndex in range(len(streams)):
            if streams[streamIndex].stream_class == "REGEX_EXTRACT":
                sp = RegexExtractStreamProcessor(streams[streamIndex].regex)
            elif streams[streamIndex].stream_class == "REGEX_REPLACE":
                sp = RegexReplaceStreamProcessor(
                    streams[streamIndex].regex, streams[streamIndex].replace_text)
            elif streams[streamIndex].stream_class == "EXTRACT_FIRST_N_LINE":
                sp = ExtractFirstNLinesStreamProcessor(streams[streamIndex].extract_first_n_lines)
            elif streams[streamIndex].stream_class == "EXTRACT_NTH_LINE":
                sp = ExtractNthLinesStreamProcessor(streams[streamIndex].extract_nth_line)
            elif streams[streamIndex].stream_class == "JOIN_ALL_ROWS":
                sp = JoinAllRowsStreamProcessor(streams[streamIndex].join_string)
            elif streams[streamIndex].stream_class == "TRIM_SPACE":
                sp = TrimSpaceStreamProcessor()
            elif streams[streamIndex].stream_class == "REMOVE_TEXT_BEFORE_START_OF_TEXT":
                sp = RemoveTextBeforeStartOfTextStreamProcessor(
                    streams[streamIndex].remove_text)
            elif streams[streamIndex].stream_class == "REMOVE_TEXT_BEFORE_END_OF_TEXT":
                sp = RemoveTextBeforeEndOfTextStreamProcessor(
                    streams[streamIndex].remove_text)
            elif streams[streamIndex].stream_class == "REMOVE_TEXT_AFTER_START_OF_TEXT":
                sp = RemoveTextAfterStartOfTextStreamProcessor(
                    streams[streamIndex].remove_text)
            elif streams[streamIndex].stream_class == "REMOVE_TEXT_AFTER_END_OF_TEXT":
                sp = RemoveTextAfterEndOfTextStreamProcessor(
                    streams[streamIndex].remove_text)
            elif streams[streamIndex].stream_class == "COMBINE_FIRST_N_LINES":
                sp = CombineFirstNLinesStreamProcessor(
                    streams[streamIndex].combine_first_n_lines)
            elif streams[streamIndex].stream_class == "GET_CHARS_FROM_NEXT_COL_WHEN_REGEX_NOT_MATCH":
                sp = GetCharsFromNextColWhenRegexNotMatchStreamProcessor(
                    streams[streamIndex].get_chars_from_next_col_when_regex_not_match)
            elif streams[streamIndex].stream_class == "TRIM_SPACE_TABLE":
                sp = TrimSpaceTableStreamProcessor()
            elif streams[streamIndex].stream_class == "REMOVE_ROWS_WITH_CONDITIONS":
                sp = RemoveRowsWithConditionsStreamProcessor(
                    streams[streamIndex].remove_rows_with_conditions)
            elif streams[streamIndex].stream_class == "MERGE_ROWS_WITH_CONDITIONS":
                sp = MergeRowsWithConditionsStreamProcessor(
                    streams[streamIndex].merge_rows_with_conditions)
            elif streams[streamIndex].stream_class == "MERGE_ROWS_WITH_SAME_COLUMNS":
                sp = MergeRowsWithSameColumnsStreamProcessor(
                    streams[streamIndex].merge_rows_with_same_columns)
            elif streams[streamIndex].stream_class == "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS":
                sp = RemoveRowsBeforeRowWithConditionsStreamProcessor(
                    streams[streamIndex].remove_rows_before_row_with_conditions)
            elif streams[streamIndex].stream_class == "REMOVE_EMPTY_LINES":
                sp = RemoveEmptyLinesStreamProcessor()
            elif streams[streamIndex].stream_class == "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS":
                sp = RemoveRowsAfterRowWithConditionsStreamProcessor(
                    streams[streamIndex].remove_rows_after_row_with_conditions)
            elif streams[streamIndex].stream_class == "UNPIVOT_TABLE":
                sp = UnpivotColumnStreamProcessor(
                    streams[streamIndex].unpivot_table, streams[streamIndex].unpivot_table_conditions)
            elif streams[streamIndex].stream_class == "MAKE_FIRST_ROW_TO_BE_HEADER":
                sp = MakeFirstRowToBeHeaderStreamProcessor()
            elif streams[streamIndex].stream_class == "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS":
                sp = ConvertToTableBySpecifyHeaderStreamProcessor(
                    streams[streamIndex].convert_to_table_by_specify_headers
                )
            else:
                raise Exception("No such stream")

            if processedStreams[-1]["step"] != 0 and processedStreams[-1]["status"] == "error":
                processedStreams.append({
                    "status": "error",
                    "error_message": "Please correct the error in the above step first.",
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].stream_type,
                    "class": streams[streamIndex].stream_class,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_line": streams[streamIndex].extract_nth_line,
                    "replace_text": streams[streamIndex].replace_text,
                    "remove_text": streams[streamIndex].remove_text,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "get_chars_from_next_col_when_regex_not_match": streams[streamIndex].get_chars_from_next_col_when_regex_not_match,
                    "remove_rows_with_conditions": streams[streamIndex].remove_rows_with_conditions,
                    "merge_rows_with_conditions": streams[streamIndex].merge_rows_with_conditions,
                    "remove_rows_before_row_with_conditions": streams[streamIndex].remove_rows_before_row_with_conditions,
                    "remove_rows_after_row_with_conditions": streams[streamIndex].remove_rows_after_row_with_conditions,
                    "unpivot_table": streams[streamIndex].unpivot_table,
                    "unpivot_table_conditions": streams[streamIndex].unpivot_table_conditions,
                    "convert_to_table_by_specify_headers": streams[streamIndex].convert_to_table_by_specify_headers
                })
                continue

            try:
                result = sp.process(inputStream)
                processedStreams.append({
                    "status": "success",
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].stream_type,
                    "class": streams[streamIndex].stream_class,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_line": streams[streamIndex].extract_nth_line,
                    "replace_text": streams[streamIndex].replace_text,
                    "remove_text": streams[streamIndex].remove_text,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "get_chars_from_next_col_when_regex_not_match": streams[streamIndex].get_chars_from_next_col_when_regex_not_match,
                    "remove_rows_with_conditions": streams[streamIndex].remove_rows_with_conditions,
                    "merge_rows_with_conditions": streams[streamIndex].merge_rows_with_conditions,
                    "remove_rows_before_row_with_conditions": streams[streamIndex].remove_rows_before_row_with_conditions,
                    "remove_rows_after_row_with_conditions": streams[streamIndex].remove_rows_after_row_with_conditions,
                    "unpivot_table": streams[streamIndex].unpivot_table,
                    "unpivot_table_conditions": streams[streamIndex].unpivot_table_conditions,
                    "convert_to_table_by_specify_headers": streams[streamIndex].convert_to_table_by_specify_headers,
                    "data": result
                })
                inputStream = result
            except Exception as e:
                processedStreams.append({
                    "status": "error",
                    "error_message": str(e),
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].stream_type,
                    "class": streams[streamIndex].stream_class,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_line": streams[streamIndex].extract_nth_line,
                    "replace_text": streams[streamIndex].replace_text,
                    "remove_text": streams[streamIndex].remove_text,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "get_chars_from_next_col_when_regex_not_match": streams[streamIndex].get_chars_from_next_col_when_regex_not_match,
                    "remove_rows_with_conditions": streams[streamIndex].remove_rows_with_conditions,
                    "merge_rows_with_conditions": streams[streamIndex].merge_rows_with_conditions,
                    "remove_rows_before_row_with_conditions": streams[streamIndex].remove_rows_before_row_with_conditions,
                    "remove_rows_after_row_with_conditions": streams[streamIndex].remove_rows_after_row_with_conditions,
                    "unpivot_table": streams[streamIndex].unpivot_table,
                    "unpivot_table_conditions": streams[streamIndex].unpivot_table_conditions,
                    "convert_to_table_by_specify_headers": streams[streamIndex].convert_to_table_by_specify_headers
                })

        return processedStreams

