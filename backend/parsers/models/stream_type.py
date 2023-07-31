from enum import Enum


class StreamtType(Enum):

    REGEX_EXTRACT = "REGEX_EXTRACT"
    REGEX_REPLACE = "REGEX_REPLACE"

    TRIM_SPACE = "TRIM_SPACE"
    REMOVE_TEXT_BEFORE_START_OF_TEXT = "REMOVE_TEXT_BEFORE_START_OF_TEXT"
    REMOVE_TEXT_BEFORE_END_OF_TEXT = "REMOVE_TEXT_BEFORE_END_OF_TEXT"
    REMOVE_TEXT_AFTER_START_OF_TEXT = "REMOVE_TEXT_AFTER_START_OF_TEXT"
    REMOVE_TEXT_AFTER_END_OF_TEXT = "REMOVE_TEXT_AFTER_END_OF_TEXT"
    REPLACE_TEXT = "REPLACE_TEXT"
    REPLACE_REGEX = "REPLACE_REGEX"
    JOIN_ALL_ROWS = "JOIN_ALL_ROWS"
    EXTRACT_FIRST_N_LINES = "EXTRACT_FIRST_N_LINES"
    EXTRACT_NTH_LINE = "EXTRACT_NTH_LINE"

    COMBINE_FIRST_N_LINES = "COMBINE_FIRST_N_LINES"
    GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH = "GET_CHARS_FROM_NEXT_COL_IF_REGEX_NOT_MATCH"
    TRIM_SPACE_FOR_ALL_ROWS_AND_COLS = "TRIM_SPACE_FOR_ALL_ROWS_AND_COLS"
    REMOVE_ROWS_WITH_CONDITIONS = "REMOVE_ROWS_WITH_CONDITIONS"
    MERGE_ROWS_WITH_CONDITIONS = "MERGE_ROWS_WITH_CONDITIONS"
    MERGE_ROWS_WITH_SAME_COLUMNS = "MERGE_ROWS_WITH_SAME_COLUMNS"
    REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS = "REMOVE_ROWS_BEFORE_ROW_WITH_CONDITIONS"
    REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS = "REMOVE_ROWS_AFTER_ROW_WITH_CONDITIONS"
    UNPIVOT_TABLE = "UNPIVOT_TABLE"
    MAKE_FIRST_ROW_TO_BE_HEADER = "MAKE_FIRST_ROW_TO_BE_HEADER"

    REMOVE_EMPTY_LINES = "REMOVE_EMPTY_LINES"

    CONVERT_TO_TABLE_BY_SPECIFY_HEADERS = "CONVERT_TO_TABLE_BY_SPECIFY_HEADERS"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
