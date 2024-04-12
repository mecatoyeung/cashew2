import json
from typing import List
import ast

from munch import DefaultMunch

from parsers.models.parser import Parser

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

class ExtractJSONAsTableStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.json_extract_code = stream.json_extract_code

    def process(self, input):

        input_obj = DefaultMunch.fromDict(json.loads(input))

        if not is_valid_python(self.json_extract_code):
            raise Exception("Extract code format is not correct. Please verify your input or contact system administrator.")

        try:
            d = DynamicAccessNestedDict(input_obj)
            extracted = d.getval(eval(self.json_extract_code))
        except Exception as e:
            raise Exception("Extraction failed. Please verify your input or contact system administrator.")
        
        if not isinstance(extracted, (list, dict)):
            raise Exception("The data you asked is not a table.  Please verify your input or contact system administrator.")

        col_names = []
        for row in extracted:
            for col_name, col_value in row.items():
                col_names.append(col_name)
        col_names = list(dict.fromkeys(col_names))
            
        output_body = []

        for row in extracted:
            row_data = []
            col_index = 0
            for col_name in col_names:
                if hasattr(row, col_name):
                    row_data.append(str(row[col_name]))
                else:
                    row_data.append("")
                col_index += 1

            output_body.append(row_data)

        output = {
            'header': list(range(0, len(col_names))),
            'body': output_body
        }

        return output

