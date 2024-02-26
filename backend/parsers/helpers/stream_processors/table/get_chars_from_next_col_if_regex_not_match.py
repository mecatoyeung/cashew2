import re
import copy

from parsers.helpers.stream_processors.base import StreamBase


class GetCharsFromNextColIfRegexNotMatchStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.col_index = stream.col_index
        self.regex = stream.regex

    def process(self, input):

        col_index = self.col_index
        regex = self.regex

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
    
    