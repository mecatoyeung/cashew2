from parsers.helpers.stream_processors.base import StreamBase


class TrimSpaceTableStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):

        output_body = []

        for row in input["body"]:
            new_row = []
            for col in row:
                new_row.append(col.strip())
            output_body.append(new_row)

        if len(output_body) == 0:
            output_body = [[""]]

        output = {
            'header': input["header"],
            'body': output_body
        }

        return output
    
    