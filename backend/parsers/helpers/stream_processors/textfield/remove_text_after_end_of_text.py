import re

from ..base import StreamBase

class RemoveTextAfterEndOfTextStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.removeText = stream.text

    def process(self, streamed_data):

        output = []

        for line in streamed_data:
            result = re.search(self.removeText, line)
            if not result == None:
                # append current text line
                index = result.start() + len(result.group(0))
                output.append(line[0:index])
                break
            else:
                output.append(line)

        if len(output) == 0:
            output = [""]

        return output