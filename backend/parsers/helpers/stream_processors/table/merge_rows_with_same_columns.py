import copy

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class MergeRowsWithSameColumnsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.columns = stream.col_indexes

    def process(self, input):
        if len(input["value"]["body"]) == 0:
            return [[""]]

        input["value"]["body"] = [row[:] for row in input["value"]["body"]]
        new_value_body = []

        previousLine = copy.deepcopy(input["value"]["body"][0])
        columns_array = list(map(int, self.columns.split(",")))
        for i in range(1, (len(input["value"]["body"]))):
            matched = True
            for column in columns_array:
                if previousLine[column] != input["value"]["body"][i][column]:
                    matched = False

            if matched == True:
                if len(previousLine) == 0:
                    previousLine = copy.deepcopy(input["value"]["body"][i])
                else:
                    for j in range(0, (len(input["value"]["body"][i]))):
                        if (previousLine[j] == "" or input["value"]["body"][i][j] == ""):
                            continue
                        if j in columns_array:
                            continue
                        if previousLine[j] == input["value"]["body"][i][j]:
                            continue
                        previousLine[j] = str(
                            previousLine[j]) + "\n" + str(input["value"]["body"][i][j])

            else:
                new_value_body.append(previousLine)
                previousLine = copy.deepcopy(input["value"]["body"][i])

        # append last line
        new_value_body.append(previousLine)

        if len(new_value_body) == 0:
            new_value_body = [[""]]

        new_value = {
            'header': input["value"]["header"],
            'body': new_value_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }

