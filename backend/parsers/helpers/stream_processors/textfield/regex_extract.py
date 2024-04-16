import re

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class RegexExtractStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.regex = stream.regex

    def process(self, input):

        new_value = [""]

        found_any = False

        for line in input["value"]:
            found = re.findall(self.regex, line)
            if len(found) > 0:
                if not found_any:
                    found_any = True
                    new_value = [(" ".join(found))]
                else:
                    new_value.append(" ".join(found))

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    
    