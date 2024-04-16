import re

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class RemoveTextBeforeStartOfTextStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.removeText = stream.text

    def process(self, input):

        new_value = []

        for lineIndex, line in enumerate(input["value"]):
            result = re.search(self.removeText, line)
            if not result == None:
                # remove all previous text
                new_value = []

                # append current text line
                index = result.start()
                new_value.append(line[index:])
                new_value += input["value"][(lineIndex+1):]
                break

        if len(new_value) == 0:
            new_value = [""]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    