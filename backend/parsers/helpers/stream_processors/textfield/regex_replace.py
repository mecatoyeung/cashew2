import re

from parsers.helpers.stream_processors.base import StreamBase


class RegexReplaceStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.regex = stream.regex
        self.text = stream.text

    def process(self, streamed_data):

        output = []

        if len(streamed_data) == 0:
            output = [""]
        else:
            for line in streamed_data:
                output.append(re.sub(self.regex, self.text, line))

        return output
    
    