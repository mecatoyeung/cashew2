from parsers.helpers.stream_processors.base import StreamBase


class MakeFirstRowToBeHeaderStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):
        if len(input["body"]) == 0:
            return [[""]]

        output_header = []
        output_body = input["body"]

        for l in range(0, len(output_body[0])):
            output_header.append(output_body[0][l])

        output_body = output_body[1:]

        output = {
            'header': output_header,
            'body': output_body
        }

        return output

