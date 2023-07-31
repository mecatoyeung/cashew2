import re

def get_document_nos_from_range(range_str, first='1', last='1'):

    re_exp = re.compile(r'^(?:%FIRST(?:[-+]\d+)*%|%LAST(?:[-+]\d+)*%|\d+)(?:-(?:%FIRST(?:[-+]\d+)*%|%LAST(?:[-+]\d+)*%|\d+))?(?:,*(?:%FIRST(?:[-+]\d+)*%|%LAST(?:[-+]\d+)*%|\d+)(?:-(?:%FIRST(?:[-+]\d+)*%|%LAST(?:[-+]\d+)*%|\d+))?)*$')
    re_check = re_exp.match(range_str)

    if not re_check:
        raise Exception("Document range_str format is wrong.")

    evaled = range_str

    while True:
        parts_matching_regex = re.search(r"(%FIRST(?:[-+]\d+)*%|%LAST(?:[-+]\d+)*%)", evaled)

        if parts_matching_regex == None or len(parts_matching_regex.groups()) <= 0:
            break

        part_to_be_resolved = parts_matching_regex.groups()[0]

        resolved_part = re.sub("FIRST", first, part_to_be_resolved)
        resolved_part = re.sub("LAST", last, resolved_part)
        calculated_part = re.sub(r'%([0-9]+[+-][0-9]+)%', lambda x: str(eval(x.group(1))), resolved_part)
        start_pos = parts_matching_regex.start()
        end_pos = start_pos + len(parts_matching_regex.group())

        evaled = calculated_part.join([evaled[:start_pos], evaled[end_pos:]])

    document_nos = set()
    for part in evaled.split(','):
        x=part.split('-')
        if x[0] == x[-1]:
            document_nos.add(int(x[0]))
            continue
        document_nos.update(range(int(x[0]),int(x[-1])+1))

    document_nos = filter(lambda x: x > 0, document_nos)

    return sorted(document_nos)
