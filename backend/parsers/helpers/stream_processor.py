import copy

from django.db.models import Prefetch
from django.core import serializers

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

STREAM_PROCESSOR_MAPPING = {
    "EXTRACT_FIRST_N_LINES": ExtractFirstNLinesStreamProcessor,
    "EXTRACT_NTH_LINES": ExtractNthLinesStreamProcessor,
    "REGEX_EXTRACT": RegexExtractStreamProcessor,
    "REGEX_REPLACE": RegexReplaceStreamProcessor,
    "JOIN_ALL_ROWS": JoinAllRowsStreamProcessor,
    "TRIM_SPACE": TrimSpaceStreamProcessor,
    "REMOVE_EMPTY_LINES": RemoveEmptyLinesStreamProcessor,
    "REMOVE_TEXT_BEFORE_START_OF_TEXT": RemoveTextBeforeStartOfTextStreamProcessor,
    "REMOVE_TEXT_BEFORE_END_OF_TEXT": RemoveTextBeforeEndOfTextStreamProcessor,
    "REMOVE_TEXT_AFTER_START_OF_TEXT": RemoveTextAfterStartOfTextStreamProcessor,
    "REMOVE_TEXT_AFTER_END_OF_TEXT": RemoveTextAfterEndOfTextStreamProcessor,
    "COMBINE_FIRST_N_LINES": RemoveTextAfterEndOfTextStreamProcessor,
    "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS": ConvertToTableBySpecifyHeaderStreamProcessor
}

def convert_to_table_by_specify_headers_map(object):
    return object.header.header

class StreamProcessor:

    def __init__(self, rule):
        self.rule = rule

    def process(self, document):

        rule_extractor = RuleExtractor(self.rule, document)

        streams = Stream.objects.filter(rule_id=self.rule.id).select_related(
            'convert_to_table_by_specify_headers',
        ).prefetch_related(
            'convert_to_table_by_specify_headers__headers',
        ).order_by('step')

        rule_raw_result = rule_extractor.extract()
        inputStream = rule_raw_result

        processedStreams = []
        processedStreams.append({
            "step": 0,
            "type": self.rule.rule_type,
            "data": inputStream
        })

        for streamIndex in range(len(streams)):

            if streams[streamIndex].stream_class in STREAM_PROCESSOR_MAPPING:
                sp = STREAM_PROCESSOR_MAPPING[streams[streamIndex].stream_class](streams[streamIndex])
            else:
                raise Exception("No such stream")

            if streams[streamIndex].stream_class == "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS":
                streams[streamIndex].type = "TABLE"

            if processedStreams[-1]["step"] != 0 and processedStreams[-1]["status"] == "error":
                processedStreams.append({
                    "status": "error",
                    "error_message": "Please correct the error in the above step first.",
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].type,
                    "class": streams[streamIndex].stream_class,
                    "text": streams[streamIndex].text,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_lines": streams[streamIndex].extract_nth_lines,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "convert_to_table_by_specify_headers": { "headers": [] if streams[streamIndex].convert_to_table_by_specify_headers == None else serializers.serialize("json", streams[streamIndex].convert_to_table_by_specify_headers.headers.all()) }
                })
                continue

            try:
                result = sp.process(inputStream)
                processedStreams.append({
                    "status": "success",
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].type,
                    "class": streams[streamIndex].stream_class,
                    "text": streams[streamIndex].text,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_lines": streams[streamIndex].extract_nth_lines,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "convert_to_table_by_specify_headers": { "headers": [] if streams[streamIndex].convert_to_table_by_specify_headers == None else serializers.serialize("json", streams[streamIndex].convert_to_table_by_specify_headers.headers.all()) },
                    "data": result
                })
                inputStream = result
            except Exception as e:
                processedStreams.append({
                    "status": "error",
                    "error_message": str(e),
                    "id": streams[streamIndex].id,
                    "step": streams[streamIndex].step,
                    "type": streams[streamIndex].type,
                    "class": streams[streamIndex].stream_class,
                    "regex": streams[streamIndex].regex,
                    "join_string": streams[streamIndex].join_string,
                    "extract_first_n_lines": streams[streamIndex].extract_first_n_lines,
                    "extract_nth_lines": streams[streamIndex].extract_nth_lines,
                    "text": streams[streamIndex].text,
                    "combine_first_n_lines": streams[streamIndex].combine_first_n_lines,
                    "convert_to_table_by_specify_headers": { "headers": [] if streams[streamIndex].convert_to_table_by_specify_headers == None else serializers.serialize("json", streams[streamIndex].convert_to_table_by_specify_headers.headers.all()) }
                })

        return processedStreams

