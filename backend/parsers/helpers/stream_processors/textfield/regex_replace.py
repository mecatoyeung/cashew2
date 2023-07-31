import re

from ..base import StreamBase

class RegexReplaceStreamProcessor(StreamBase):

    def __init__(self, regex, replace_text):
        self.regex = regex
        self.replace_text = replace_text

    def process(self, streamed_data):

        output = []

        if len(streamed_data) == 0:
            output = [""]
        else:
            for line in streamed_data:
                output.append(re.sub(self.regex, self.replace_text, line))

        return output