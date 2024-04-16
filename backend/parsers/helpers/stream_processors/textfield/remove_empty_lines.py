from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class RemoveEmptyLinesStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):

        new_value = []

        for line in input["value"]:
            if not line.strip() == "":
                new_value.append(line)

        if len(new_value) == 0:
            new_value = [""]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    