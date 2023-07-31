from ..base import StreamBase
from ....helpers.get_line_nos_from_range import get_line_nos_from_range

class ExtractNthLinesStreamProcessor(StreamBase):

    def __init__(self, n):
        self.n = n

    def process(self, streamed_data):

        if len(streamed_data) == 0:
            output = [""]
        else:
            output = []
            line_nos = get_line_nos_from_range(self.n,
                last=str(len(streamed_data)))
            if len(line_nos) <= 0:
                output = [""]
                return output
            for line_no in line_nos:
                output.append(streamed_data[line_no - 1])

        return output