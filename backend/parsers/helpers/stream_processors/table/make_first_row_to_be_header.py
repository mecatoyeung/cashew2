from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType


class MakeFirstRowToBeHeaderStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):
        if len(input["value"]["body"]) == 0:
            return [[""]]

        new_value_header = []
        new_value_body = input["value"]["body"]

        for l in range(0, len(new_value_body[0])):
            new_value_header.append(new_value_body[0][l])

        new_value_body = new_value_body[1:]

        new_value = {
            'header': new_value_header,
            'body': new_value_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }

