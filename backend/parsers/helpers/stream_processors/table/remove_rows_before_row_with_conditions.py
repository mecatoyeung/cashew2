import re

from parsers.helpers.stream_processors.base import StreamBase

class RemoveRowsBeforeRowWithConditionsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.conditions = stream.streamcondition_set.all()
        self.remove_matched_row_also = stream.remove_matched_row_also

    def process(self, input):
        if len(input["body"]) == 0:
            return [[""]]

        output_body = []
        conditions = self.conditions
        remove_matched_row_also = self.remove_matched_row_also

        matched_already = False
        for i in range(0, len(input["body"])):
            matched = True
            if matched_already == False:
                for condition in conditions:
                    column = int(condition.column) - 1
                    if column < 0:
                        break
                    if column >= len(input["body"][i]):
                        break
                    if (condition.operator == 'EQUALS'):
                        if not input["body"][i][column] == condition.value:
                            matched = False
                    elif (condition.operator == 'REGEX'):
                        if not re.match(condition.value, input["body"][i][column]):
                            matched = False
                    elif (condition.operator == 'CONTAINS'):
                        if not condition.value in input["body"][i][column]:
                            matched = False
                    elif (condition.operator == 'IS_EMPTY'):
                        if not input["body"][i][column].strip() == "":
                            matched = False
                    elif (condition.operator == 'IS_NOT_EMPTY'):
                        if not input["body"][i][column].strip() != "":
                            matched = False
                if matched == True:
                    matched_already = True
                    output_body = []
                    if remove_matched_row_also:
                        continue
            output_body.append(input["body"][i])

        if len(output_body) == 0:
            output_body = [[""]]

        output = {
            'header': input["header"],
            'body': output_body
        }

        return output
    
    