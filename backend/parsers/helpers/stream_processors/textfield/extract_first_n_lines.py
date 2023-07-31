from ..base import StreamBase

class ExtractFirstNLinesStreamProcessor(StreamBase):

    def __init__(self, n):
        self.n = n

    def process(self, streamed_data):

        if len(streamed_data) == 0:
            output = [""]
        else:
            output = streamed_data[:int(self.n)]

        return output