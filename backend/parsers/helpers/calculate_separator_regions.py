from decimal import Decimal
from .xml_helpers import XMLRegion

def calculate_separator_regions(xml_page, rule):
    areas = []

    filtered_table_column_separators = filter(lambda table_column_separator: 
                                              table_column_separator.x > rule.x1 and table_column_separator.x < rule.x2, 
                                              rule.table_column_separators.all())
    filtered_table_column_separators = list(map(lambda a: a.x, filtered_table_column_separators))
    filtered_table_column_separators.insert(0, rule.x1)
    filtered_table_column_separators.append(rule.x2)
    for i in range(len(filtered_table_column_separators) - 1):
        region = XMLRegion()
        region.x1 = filtered_table_column_separators[i] / Decimal(100.00) * xml_page.region.x2
        region.x2 = filtered_table_column_separators[i + 1] / Decimal(100.00) * xml_page.region.x2
        region.y1 = rule.y1 / Decimal(100.00) * xml_page.region.y2
        region.y2 = rule.y2 / Decimal(100.00) * xml_page.region.y2
        areas.append(region)

    return areas