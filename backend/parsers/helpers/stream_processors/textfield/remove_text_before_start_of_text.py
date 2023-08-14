import re

from ..base import StreamBase

class RemoveTextBeforeStartOfTextStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.removeText = stream.text

    def process(self, streamed_data):

        output = []

        for lineIndex, line in enumerate(streamed_data):
            result = re.search(self.removeText, line)
            if not result == None:
                # remove all previous text
                output = []

                # append current text line
                index = result.start()
                output.append(line[index:])
                output += streamed_data[(lineIndex+1):]
                break

        if len(output) == 0:
            output = [""]

        return output