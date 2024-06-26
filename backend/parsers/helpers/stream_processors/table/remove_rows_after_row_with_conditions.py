import re

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class RemoveRowsAfterRowWithConditionsStreamProcessor(StreamBase):

    def __init__(self, stream):
        self.conditions = stream.streamcondition_set.all()
        self.remove_matched_row_also = stream.remove_matched_row_also

    def process(self, input):
        if len(input["value"]["body"]) == 0:
            return [[""]]

        output_body = []
        conditions = self.conditions
        remove_matched_row_also = self.remove_matched_row_also

        matched_already = False
        for i in range(0, len(input["value"]["body"])):
            matched = True
            if matched_already == False:
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
                    matched_already = True
                    matched_i = i
                    break

        if matched_already:
            output_body = input["value"]["body"][:(matched_i+1)]
            if remove_matched_row_also:
                output_body = output_body[:-1]
        else:
            output_body = input["value"]["body"]

        if len(output_body) == 0:
            output_body = [[""]]

        new_value = {
            'header': input["value"]["header"],
            'body': output_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }

