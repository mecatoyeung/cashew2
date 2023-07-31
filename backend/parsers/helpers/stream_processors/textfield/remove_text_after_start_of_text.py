import re

from ..base import StreamBase

class RemoveTextAfterStartOfTextStreamProcessor(StreamBase):

    def __init__(self, removeText):
        self.removeText = removeText

    def process(self, streamed_data):

        output = []

        for line in streamed_data:
            result = re.search(self.removeText, line)
            if not result == None:
                # append current text line
                index = result.start()
                output.append(line[0:index])
                break
            else:
                output.append(line)

        if len(output) == 0:
            output = [""]

        return output