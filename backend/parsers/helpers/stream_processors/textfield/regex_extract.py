import re

from parsers.helpers.stream_processors.base import StreamBase


class RegexExtractStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.regex = stream.regex

    def process(self, streamed_data):

        output = [""]

        found_any = False

        for line in streamed_data:
            found = re.findall(self.regex, line)
            if len(found) > 0:
                if not found_any:
                    found_any = True
                    output = [(" ".join(found))]
                else:
                    output.append(" ".join(found))

        return output
    
    