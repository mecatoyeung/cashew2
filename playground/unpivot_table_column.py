import re

unpivot_column_index = 4

def unpivot_table_column(input):

    # deep copy
    output_header = input["header"][:]
    output_body = [row[:] for row in input["body"]]

    columns_to_add = []

    insert_col_at = unpivot_column_index + 1

    for i in range(0, len(input["body"])):

        textlines = input["body"][i][unpivot_column_index].split("\n")

        if textlines[0] == '':
            textlines.pop(0)

        while(len(textlines) > 0):
            if re.match(r"([A-Za-z0-9 -/]+):[\s]*([A-Za-z0-9 -/:]+)", textlines[0]):
                matched = re.findall(r"([A-Za-z0-9 -/]+):[\s]*([A-Za-z0-9 -/:]+)", textlines[0])
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

    if len(output_body) == 0:
        output_body = [[""]]

    output = {
        'header': output_header,
        'body': output_body
    }

    return output

result = unpivot_table_column({ 
    "header": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "body": [[
        '',
        '',
        '400291011141',
        '',
        """
Buyer Size: 50340\nUnit of Measure: EA - Eaches\nBuyer Item No: 002\nVendor Style No: SLIPSNKRW2-810\nBuyer Color Description: ORNG\nOMBRE\nSize: 6\nDescription: SLIP ON STRAPPY\nSNEAKER O\nBuyer Color: 810\nBuyer Size Description: 6\nProduct Type Code: WA\nInner Qty Per Container: 1\nBuyer Style No: 2391015
""",
        '',
        '   12.01',
        '      60',
        '        6',
        'EA',
        '      72.06'
    ],
    [
        '',
        '',
        '400291011141',
        '',
        """
Buyer Size: 50340\nUnit of Measure: EA - Eaches\nBuyer Item No: 002\nVendor Style No: SLIPSNKRW2-810\nBuyer Color Description: ORNG\nOMBRE\nSize: 6\nDescription: SLIP ON STRAPPY\nSNEAKER O\nBuyer Color: 810\nBuyer Size Description: 6\nProduct Type Code: WA\nInner Qty Per Container: 1\nBuyer Style No: 2391015
""",
        '',
        '   12.01',
        '      60',
        '        6',
        'EA',
        '      72.06'
    ]]
})

print(result)