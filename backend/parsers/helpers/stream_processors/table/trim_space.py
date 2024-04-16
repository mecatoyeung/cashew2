from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class TrimSpaceTableStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):

        new_value_body = []

        for row in input["value"]["body"]:
            new_row = []
            for col in row:
                new_row.append(col.strip())
            new_value_body.append(new_row)

        if len(new_value_body) == 0:
            new_value_body = [[""]]

        new_value = {
            'header': input["value"]["header"],
            'body': new_value_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }
    
    