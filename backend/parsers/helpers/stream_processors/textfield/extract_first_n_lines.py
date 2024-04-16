from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType


class ExtractFirstNLinesStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.n = stream.extract_first_n_lines

    def process(self, input):

        if len(input) == 0:
            new_value = [""]
        else:
            new_value = input["value"][:int(self.n)]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    