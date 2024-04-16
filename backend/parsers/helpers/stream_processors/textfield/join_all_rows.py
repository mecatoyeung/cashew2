from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType

class JoinAllRowsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.join_string = stream.join_string

    def process(self, input):

        if len(input["value"]) == 0:
            new_value = [""]
        else:
            new_value = [self.join_string.join(input["value"])]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    