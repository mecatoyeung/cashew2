import re

from parsers.helpers.stream_processors.base import StreamBase


class RemoveTextBeforeEndOfTextStreamProcessor(StreamBase):

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
                index = result.start() + len(result.group(0))
                if not (len(line[index:]) == 0):
                    output.append(line[index:])
                output += streamed_data[(lineIndex+1):]
                break

        if len(output) == 0:
            output = [""]

        return output
    
    