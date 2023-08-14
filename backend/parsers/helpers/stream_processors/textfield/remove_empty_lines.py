from ..base import StreamBase

class RemoveEmptyLinesStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):

        output = []

        for line in input:
            if not line.strip() == "":
                output.append(line)

        if len(output) == 0:
            output = [""]

        return output