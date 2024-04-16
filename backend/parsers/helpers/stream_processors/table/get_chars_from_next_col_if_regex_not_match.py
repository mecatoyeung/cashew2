import re
import copy

from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType


class GetCharsFromNextColIfRegexNotMatchStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.col_index = stream.col_index
        self.regex = stream.regex

    def process(self, input):

        col_index = self.col_index
        regex = self.regex

        if len(input["value"]["body"]) == 0:
            return [""]

        if col_index >= len(input["value"]["body"][0]):
            new_value = {
                'header': input["value"]["header"],
                'body': input["value"]["body"]
            }
            return new_value

        new_value_body = []
        for row in input["value"]["body"]:
            updated_row = copy.deepcopy(row)
            chars_from_two_cols = row[col_index-1] + row[col_index]
            found = re.findall(regex, chars_from_two_cols)
            if len(found) > 0:
                extra_col_width = len(found[0]) - len(row[col_index-1])
                updated_row[col_index-1] = found[0]
                updated_row[col_index] = updated_row[col_index][extra_col_width:]
            new_value_body.append(updated_row)

        new_value = {
            'header': input["value"]["header"],
            'body': new_value_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }
    
    