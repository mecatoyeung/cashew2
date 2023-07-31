from ..base import StreamBase

class JoinAllRowsStreamProcessor(StreamBase):

    def __init__(self, join_string):
        self.join_string = join_string

    def process(self, streamed_data):

        if len(streamed_data) == 0:
            output = [""]
        else:
            output = [self.join_string.join(streamed_data)]

        return output