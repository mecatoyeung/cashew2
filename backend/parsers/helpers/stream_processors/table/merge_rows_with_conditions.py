import re
import copy

from parsers.helpers.stream_processors.base import StreamBase
from parsers.models.stream_type import StreamType


class MergeRowsWithConditionsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.conditions = stream.streamcondition_set.all()

    def process(self, input):
        if len(input["value"]["body"]) == 0:
            return [[""]]

        input["value"]["body"] = [row[:] for row in input["value"]["body"]]
        new_value_body = []

        previousLine = copy.deepcopy(input["value"]["body"][0])
        conditions = self.conditions
        for i in range(1, (len(input["value"]["body"]))):
            matched = True
            for condition in conditions:
                column = int(condition.column) - 1
                if column < 0:
                    break
                if column >= len(input["value"]["body"][i]):
                    break
                if (condition.operator == 'EQUALS'):
                    if not input["value"]["body"][i][column] == condition.value:
                        matched = False
                elif (condition.operator == 'REGEX'):
                    if not re.match(condition.value, input["value"]["body"][i][column]):
                        matched = False
                elif (condition.operator == 'CONTAINS'):
                    if not condition.value in input["value"]["body"][i][column]:
                        matched = False
                elif (condition.operator == 'IS_EMPTY'):
                    if not input["value"]["body"][i][column].strip() == "":
                        matched = False
                elif (condition.operator == 'IS_NOT_EMPTY'):
                    if not input["value"]["body"][i][column].strip() != "":
                        matched = False

            if matched == True:
                if len(previousLine) == 0:
                    previousLine = copy.deepcopy(input["value"]["body"][i])
                else:
                    for j in range(0, (len(input["value"]["body"][i]))):
                        if (previousLine[j] == "" or input["value"]["body"][i][j] == ""):
                            continue
                        previousLine[j] = str(previousLine[j]) + "\n" + str(input["value"]["body"][i][j])

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
    
    