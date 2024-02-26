from parsers.helpers.stream_processors.base import StreamBase


class JoinAllRowsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.join_string = stream.join_string

    def process(self, streamed_data):

        if len(streamed_data) == 0:
            output = [""]
        else:
            output = [self.join_string.join(streamed_data)]

        return output
    
    