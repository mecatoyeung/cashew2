from parsers.helpers.stream_processors.base import StreamBase
from parsers.helpers.get_line_nos_from_range import get_line_nos_from_range
from parsers.models.stream_type import StreamType

class ExtractNthLinesStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.n = stream.extract_nth_lines

    def process(self, input):

        if len(input["value"]) == 0:
            new_value = [""]
        else:
            new_value = []
            line_nos = get_line_nos_from_range(self.n,
                last=str(len(input["value"])))
            if len(line_nos) <= 0:
                new_value = [""]
                return new_value
            for line_no in line_nos:
                new_value.append(input["value"][line_no - 1])

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    