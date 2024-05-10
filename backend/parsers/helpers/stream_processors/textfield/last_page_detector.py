import re

from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType

class LastPageDetectorStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.current_page_regex = stream.current_page_regex
        self.last_page_regex = stream.last_page_regex

    def process(self, input):

        if len(input["value"]) == 0:
            new_value = ["False"]
        else:
            current_page_value = ""
            for line in input["value"]:
                found_current_page = re.findall(self.current_page_regex, line)
                if len(found_current_page) > 0:
                    current_page_value = found_current_page[0]
                    break
            last_page_value = ""
            for line in input["value"]:
                found_last_page = re.findall(self.last_page_regex, line)
                if len(found_last_page) > 0:
                    last_page_value = found_last_page[0]
                    break

            if current_page_value == "":
                new_value = ["False"]

            if last_page_value == "":
                new_value = ["False"]

            if current_page_value == last_page_value:
                new_value = ["True"]
            else:
                new_value = ["False"]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }
    