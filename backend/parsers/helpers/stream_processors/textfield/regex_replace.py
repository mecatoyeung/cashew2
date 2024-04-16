import re

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class RegexReplaceStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.regex = stream.regex
        self.text = stream.text

    def process(self, input):

        new_value = []

        if len(input["value"]) == 0:
            new_value = [""]
        else:
            for line in input["value"]:
                new_value.append(re.sub(self.regex, self.text, line))

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    