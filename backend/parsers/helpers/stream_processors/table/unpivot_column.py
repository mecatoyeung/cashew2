import re
import json

from parsers.helpers.stream_processors.base import StreamBase

from parsers.models.stream_type import StreamType


class UnpivotColumnStreamProcessor(StreamBase):

    def __init__(self, unpivot_table, unpivot_table_conditions):
        self.unpivot_table = unpivot_table
        self.unpivot_table_conditions = unpivot_table_conditions

    def process(self, input):
        if len(input["value"]["body"]) == 0:
            return [[""]]

        new_value_body = []

        unpivot_table = json.loads(self.unpivot_table)
        unpivot_column_index = int(unpivot_table['unpivot_column_index'])
        newline_char = unpivot_table['newline_char']
        if newline_char == "":
            raise Exception("Please specify new line character.")
        property_assign_char = unpivot_table['property_assign_char']
        if property_assign_char == "":
            raise Exception("Please specify assignment character.")
        conditions = json.loads(self.unpivot_table_conditions)

        # deep copy
        new_value_header = input["value"]["header"][:]
        new_value_body = [row[:] for row in input["value"]["body"]]

        columns_to_add = []

        insert_col_at = unpivot_column_index + 1

        for i in range(0, len(input["value"]["body"])):
            matched = True
            for condition in conditions:
                column = int(condition['column'])
                if column < 0:
                    break
                if column >= len(input["value"]["body"][i]):
                    break
                if (condition['operator'] == 'equals'):
                    if not input["value"]["body"][i][column] == condition['value']:
                        matched = False
                elif (condition['operator'] == 'regex'):
                    if not re.match(condition['value'], input["value"]["body"][i][column]):
                        matched = False
                elif (condition['operator'] == 'contains'):
                    if not condition['value'] in input["value"]["body"][i][column]:
                        matched = False
                elif (condition['operator'] == 'isEmpty'):
                    if not input["value"]["body"][i][column] == "":
                        matched = False
                elif (condition['operator'] == 'isNotEmpty'):
                    if not input["value"]["body"][i][column] != "":
                        matched = False

            if matched == False:
                continue

            textlines = input["value"]["body"][i][unpivot_column_index].split(newline_char)

            if textlines[0] == '':
                textlines.pop(0)

            while(len(textlines) > 0):
                if re.match(r"([A-Za-z0-9 -/]+)" + re.escape(property_assign_char) + r"[\s]*([A-Za-z0-9 -/:]*)", textlines[0]):
                    matched = re.findall(r"([A-Za-z0-9 -/]+):[\s]*([A-Za-z0-9 -/:]*)", textlines[0])
                    matched_col_name = matched[0][0]
                    matched_data = matched[0][1]

                    if not matched_col_name in columns_to_add:
                        # insert header
                        new_value_header.insert(insert_col_at, matched_col_name)
                        for l in range(insert_col_at + 1, len(new_value_header)):
                            new_value_header[l] += 1
                        # insert col to output
                        for k in range(0, len(new_value_body)):
                            new_value_body[k].insert(insert_col_at, "")

                        insert_col_at += 1

                        columns_to_add.append(matched_col_name)

                    new_value_body[i][unpivot_column_index+columns_to_add.index(matched_col_name)+1] = matched_data
                else:
                    try:
                        matched_col_name
                        new_value_body[i][unpivot_column_index+columns_to_add.index(matched_col_name)+1] += " " + textlines[0]
                    except:
                        textlines.pop(0)
                        continue

                textlines.pop(0)

        for i in range(0, len(columns_to_add)):
            new_value_body[0][unpivot_column_index+i+1] = columns_to_add[i]

        if len(new_value_body) == 0:
            new_value_body = [[""]]

        new_value = {
            'header': new_value_header,
            'body': new_value_body
        }

        return {
            "type": StreamType.TABLE.value,
            "value": new_value
        }
    
    