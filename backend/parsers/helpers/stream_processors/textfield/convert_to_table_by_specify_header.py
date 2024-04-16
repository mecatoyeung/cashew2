import re

from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType


def convert_to_table_by_specify_headers_map(object):
    return object.header.header

class ConvertToTableBySpecifyHeaderStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.convert_to_table_by_specify_headers = stream.convert_to_table_by_specify_headers

    def process(self, input):

        output_body = []

        headers = self.convert_to_table_by_specify_headers.split("|")

        headers_row = input["value"][0]
        headers_xs_ranges = []
        for header_index, header in enumerate(headers):
            if header_index == 0:
                res = re.search(rf'{header}', headers_row)
                if res == None:
                    raise Exception(f'Header "{header}" not found.')
                start_index = res.start()
                end_index = res.end()
            else:
                res = re.search(rf'{header}', headers_row[end_index:])
                if res == None:
                    raise Exception(f'Header "{header}" not found.')
                start_index = end_index
                end_index = start_index + res.end()
            if start_index == end_index:
                continue
            headers_xs_ranges.append([start_index, end_index])

        for input_value_row in input["value"]:
            row = []
            for headers_xs_range in headers_xs_ranges:
                row.append(input_value_row[headers_xs_range[0]:headers_xs_range[1]])
            output_body.append(row)

        if len(output_body) == 0:
            output_body = [[""]]

        output_header = []
        for x_index in range(len(output_body[0])):
            output_header.append(x_index)

        output = {
            'header': output_header,
            'body': output_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": output
        }
    