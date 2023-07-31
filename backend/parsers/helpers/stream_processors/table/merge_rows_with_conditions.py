import re
import json
import copy

from ..base import StreamBase

class MergeRowsWithConditionsStreamProcessor(StreamBase):

    def __init__(self, conditions):
        self.conditions = conditions

    def process(self, input):
        if len(input["body"]) == 0:
            return [[""]]

        input["body"] = [row[:] for row in input["body"]]
        output_body = []

        previousLine = copy.deepcopy(input["body"][0])
        conditions = json.loads(self.conditions)
        for i in range(1, (len(input["body"]))):
            matched = True
            for condition in conditions:
                column = int(condition['column'])
                if column < 0:
                    break
                if column >= len(input["body"][i]):
                    break
                if (condition['operator'] == 'equals'):
                    if not input["body"][i][column] == condition['value']:
                        matched = False
                elif (condition['operator'] == 'regex'):
                    if not re.match(condition['value'], input["body"][i][column]):
                        matched = False
                elif (condition['operator'] == 'contains'):
                    if not condition['value'] in input["body"][i][column]:
                        matched = False
                elif (condition['operator'] == 'isEmpty'):
                    if not input["body"][i][column].strip() == "":
                        matched = False
                elif (condition['operator'] == 'isNotEmpty'):
                    if not input["body"][i][column].strip() != "":
                        matched = False

            if matched == True:
                if len(previousLine) == 0:
                    previousLine = copy.deepcopy(input["body"][i])
                else:
                    for j in range(0, (len(input["body"][i]))):
                        if (previousLine[j] == "" or input["body"][i][j] == ""):
                            continue
                        previousLine[j] = str(previousLine[j]) + "\n" + str(input["body"][i][j])

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