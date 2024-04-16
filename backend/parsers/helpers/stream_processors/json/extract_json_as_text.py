import json
from typing import List
import ast

from munch import DefaultMunch

from parsers.models.stream_type import StreamType

from parsers.helpers.stream_processors.base import StreamBase


def is_valid_python(code):
   try:
       ast.parse(code)
   except SyntaxError:
       return False
   return True

class DynamicAccessNestedDict:
    def __init__(self, data: dict):
        self.data = data

    def getval(self, keys: List):
        data = self.data
        for k in keys:
            data = data[k]
        return data

    def setval(self, keys: List, val) -> None:
        data = self.data
        lastkey = keys[-1]
        for k in keys[:-1]:
            data = data[k]
        data[lastkey] = val

class ExtractJSONAsTextStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.json_extract_code = stream.json_extract_code

    def process(self, input):

        input_obj = DefaultMunch.fromDict(json.loads(input["value"]))

        if not is_valid_python(self.json_extract_code):
            raise Exception("Extract code format is not correct. Please verify your input or contact system administrator.")

        try:
            d = DynamicAccessNestedDict(input_obj)
            extracted = d.getval(eval(self.json_extract_code))
        except Exception as e:
            raise Exception("Extraction failed. Please verify your input or contact system administrator.")

        primitives = (bool, str, int, float)
        if not isinstance(extracted, primitives):
            raise Exception("The variable is not string, integer, float, or boolean.")

        new_value = [extracted]

        return {
            "type": StreamType.TEXTFIELD.value,
            "value": new_value
        }

