import re
import json

from ..base import StreamBase

class RemoveRowsBeforeRowWithConditionsStreamProcessor(StreamBase):

    def __init__(self, conditions):
        self.conditions = conditions

    def process(self, input):
        if len(input["body"]) == 0:
            return [[""]]

        output_body = []
        conditions = json.loads(self.conditions)

        matchedAlready = False
        for i in range(0, len(input["body"])):
            matched = True
            if matchedAlready == False:
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
                    matchedAlready = True
                    output_body = []
            output_body.append(input["body"][i])

        if len(output_body) == 0:
            output_body = [[""]]

        output = {
            'header': input["header"],
            'body': output_body
        }

        return output