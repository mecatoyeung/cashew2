from ..base import StreamBase

class TrimSpaceStreamProcessor(StreamBase):

    def __init__(self, stream):
        pass

    def process(self, input):

        output = []

        for line in input:
            output.append(line.strip())

        if len(output) == 0:
            output = [""]

        return output