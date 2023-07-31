import re
import copy
import json

from ..base import StreamBase

class GetCharsFromNextColWhenRegexNotMatchStreamProcessor(StreamBase):

    def __init__(self, get_chars_from_next_col_when_regex_not_match):
        self.get_chars_from_next_col_when_regex_not_match = get_chars_from_next_col_when_regex_not_match

    def process(self, input):

        get_chars_from_next_col_when_regex_not_match = json.loads(self.get_chars_from_next_col_when_regex_not_match)
        col_index = int(get_chars_from_next_col_when_regex_not_match["col_index"])
        regex = get_chars_from_next_col_when_regex_not_match["regex"]

        if len(input["body"]) == 0:
            return [""]

        if col_index >= len(input["body"][0]):
            output = {
                'header': input["header"],
                'body': input["body"]
            }
            return output

        output_body = []
        for row in input["body"]:
            updated_row = copy.deepcopy(row)
            chars_from_two_cols = row[col_index] + row[col_index + 1]
            found = re.findall(regex, chars_from_two_cols)
            if len(found) > 0:
                extra_col_width = len(found[0]) - len(row[col_index])
                updated_row[col_index] = found[0]
                updated_row[col_index + 1] = updated_row[col_index + 1][extra_col_width:]
            output_body.append(updated_row)

        output = {
            'header': input["header"],
            'body': output_body
        }

        return output