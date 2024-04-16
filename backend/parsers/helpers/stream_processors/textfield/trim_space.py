from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class TrimSpaceStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):

        new_value = []

        for line in input["value"]:
            new_value.append(line.strip())

        if len(new_value) == 0:
            new_value = [""]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    