import copy

from ..base import StreamBase

class MergeRowsWithSameColumnsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.columns = stream.col_indexes

    def process(self, input):
        if len(input["body"]) == 0:
            return [[""]]

        input["body"] = [row[:] for row in input["body"]]
        output_body = []

        previousLine = copy.deepcopy(input["body"][0])
        columns_array = list(map(int, self.columns.split(",")))
        for i in range(1, (len(input["body"]))):
            matched = True
            for column in columns_array:
                if previousLine[column] != input["body"][i][column]:
                    matched = False

            if matched == True:
                if len(previousLine) == 0:
                    previousLine = copy.deepcopy(input["body"][i])
                else:
                    for j in range(0, (len(input["body"][i]))):
                        if (previousLine[j] == "" or input["body"][i][j] == ""):
                            continue
                        if j in columns_array:
                            continue
                        if previousLine[j] == input["body"][i][j]:
                            continue
                        previousLine[j] = str(
                            previousLine[j]) + "\n" + str(input["body"][i][j])

            else:
                output_body.append(previousLine)
                previousLine = copy.deepcopy(input["body"][i])

        # append last line
        output_body.append(previousLine)

        if len(output_body) == 0:
            output_body = [[""]]

        output = {
            'header': input["header"],
            'body': output_body
        }

        return output
