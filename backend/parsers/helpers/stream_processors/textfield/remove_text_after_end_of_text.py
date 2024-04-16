import re

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class RemoveTextAfterEndOfTextStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.removeText = stream.text

    def process(self, input):

        new_value = []

        for line in input["value"]:
            result = re.search(self.removeText, line)
            if not result == None:
                # append current text line
                index = result.start() + len(result.group(0))
                new_value.append(line[0:index])
                break
            else:
                new_value.append(line)

        if len(new_value) == 0:
            new_value = [""]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    