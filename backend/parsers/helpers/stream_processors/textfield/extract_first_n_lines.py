from parsers.helpers.stream_processors.base import StreamBase


class ExtractFirstNLinesStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.n = stream.extract_first_n_lines

    def process(self, streamed_data):

        if len(streamed_data) == 0:
            output = [""]
        else:
            output = streamed_data[:int(self.n)]

        return output
    
    