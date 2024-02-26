import re
import json

from parsers.helpers.stream_processors.base import StreamBase


class UnpivotColumnStreamProcessor(StreamBase):

    def __init__(self, unpivot_table, unpivot_table_conditions):
        self.unpivot_table = unpivot_table
        self.unpivot_table_conditions = unpivot_table_conditions

    def process(self, input):
        if len(input["body"]) == 0:
            return [[""]]

        output_body = []

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
        output_header = input["header"][:]
        output_body = [row[:] for row in input["body"]]

        columns_to_add = []

        insert_col_at = unpivot_column_index + 1

        for i in range(0, len(input["body"])):
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
                    if not input["body"][i][column] == "":
                        matched = False
                elif (condition['operator'] == 'isNotEmpty'):
                    if not input["body"][i][column] != "":
                        matched = False

            if matched == False:
                continue

            textlines = input["body"][i][unpivot_column_index].split(newline_char)

            if textlines[0] == '':
                textlines.pop(0)

            while(len(textlines) > 0):
                if re.match(r"([A-Za-z0-9 -/]+)" + re.escape(property_assign_char) + r"[\s]*([A-Za-z0-9 -/:]*)", textlines[0]):
                    matched = re.findall(r"([A-Za-z0-9 -/]+):[\s]*([A-Za-z0-9 -/:]*)", textlines[0])
                    matched_col_name = matched[0][0]
                    matched_data = matched[0][1]

                    if not matched_col_name in columns_to_add:
                        # insert header
                        output_header.insert(insert_col_at, matched_col_name)
                        for l in range(insert_col_at + 1, len(output_header)):
                            output_header[l] += 1
                        # insert col to output
                        for k in range(0, len(output_body)):
                            output_body[k].insert(insert_col_at, "")

                        insert_col_at += 1

                        columns_to_add.append(matched_col_name)

                    output_body[i][unpivot_column_index+columns_to_add.index(matched_col_name)+1] = matched_data
                else:
                    try:
                        matched_col_name
                        output_body[i][unpivot_column_index+columns_to_add.index(matched_col_name)+1] += " " + textlines[0]
                    except:
                        textlines.pop(0)
                        continue

                textlines.pop(0)

        for i in range(0, len(columns_to_add)):
            output_body[0][unpivot_column_index+i+1] = columns_to_add[i]

        if len(output_body) == 0:
            output_body = [[""]]

        output = {
            'header': output_header,
            'body': output_body
        }

        return output
    
    