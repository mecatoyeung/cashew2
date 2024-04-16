from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType


class CombineFirstNLinesStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.n = stream.combine_first_n_lines

    def process(self, input):
        if len(input["value"]["body"]) == 0:
            return [""]
        combinedRow = [ "" for _ in range(len(input["value"]["body"][0])) ]
        for i in range(0, int(self.n)):
            for j in range(0, len(input["value"]["body"][i])):
                if (i == (int(self.n) - 1)):
                    combinedRow[j] += str(input["value"]["body"][i][j])
                else:
                    combinedRow[j] += str(input["value"]["body"][i][j])

        new_value_body = input["value"]["body"][int(self.n):]
        new_value_body.insert(0, combinedRow)

        new_value = {
            'header': input["value"]["header"],
            'body': new_value_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }
    
