from hmac import compare_digest
import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
from decimal import Decimal

from ..models.rule_type import RuleType
from .get_document_nos_from_range import get_document_nos_from_range

SAME_LINE_ACCEPTANCE_RANGE = 3
ASSUMED_TEXT_WIDTH = Decimal(3.8)
ASSUMED_TEXT_HEIGHT = Decimal(10.0)

class XMLContainer:

    def __init__(self, document):
        self.document = document
        self.xml_pages = []

    def extract(self, rule):

        page_nums = get_document_nos_from_range(rule.pages, 1, self.document.total_page_num)
        for page_num in page_nums:
            # Add to xml page if not yet initialized
            xml_page_already_exists = sum(1 for x in self.xml_pages if xml_page.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                self.xml_pages.append(xml_page)
        self.xml_pages.sort(key = lambda x:x.page_num)


        if rule.rule_type == RuleType.TEXTFIELD.value:

            result = self.extract_textfield(rule)

        elif rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value:

            result = self.extract_anchored_textfield(rule)

        elif rule.rule_type == RuleType.TABLE.value:

            result = self.extract_table(rule)

        elif rule.rule_type == RuleType.INPUT_TEXTFIELD.value:

            return ""

        elif rule.rule_type == RuleType.INPUT_DROPDOWN.value:

            return ""

        return result

    def extract_textfield(self, rule):

        page_nums = get_document_nos_from_range(rule.pages, 1, self.document.total_page_num)

        result = []

        # Since this is a textfield, we only get the first page text
        for page_num in page_nums:

            xml_rule = XMLRule(rule)
            xml_rule.region.x1 = rule.x1 / Decimal(100.00) * self.xml_pages[0].region.x2
            xml_rule.region.x2 = rule.x2 / Decimal(100.00) * self.xml_pages[0].region.x2
            xml_rule.region.y1 = rule.y1 / Decimal(100.00) * self.xml_pages[0].region.y2
            xml_rule.region.y2 = rule.y2 / Decimal(100.00) * self.xml_pages[0].region.y2

            xml_page = [xml_page for xml_page in self.xml_pages if xml_page.page_num == page_num ][0]

            textlines_in_rows = []
            textlines_within_area = []

            for textline in xml_page.textlines:
                if xml_rule.region.overlaps(textline.region) and textline.text != "":
                    textlines_within_area.append(textline)

            last_textline = None
            for textline in textlines_within_area:
                is_new_textline = True
                for existing_textlines_in_row_index, existing_textlines_in_row in enumerate(textlines_in_rows):

                    if len(textlines_in_rows) == 0:
                        is_new_textline = True
                        break

                    if len(existing_textlines_in_row) == 0:
                        continue

                    if existing_textlines_in_row[0].page.page_num == textline.page.page_num and \
                        existing_textlines_in_row[0].region.is_in_same_line(textline.region):
                        is_new_textline = False
                        textline_belongs_to_index = existing_textlines_in_row_index
                        break
                    else:
                        is_new_textline = True

                # if current textline is not a new text line and it is overlapping the last textline
                if not is_new_textline:

                    textline_inserted = False
                    for existing_textline_row_index, existing_textline_in_row in enumerate(textlines_in_rows[textline_belongs_to_index]):
                        if textline.region.x2 <= existing_textline_in_row.region.x1:
                            textlines_in_rows[textline_belongs_to_index].insert(existing_textline_row_index, textline)
                            textline_inserted = True
                            break
                        elif textline.region.x1 <= existing_textline_in_row.region.x1:
                            textlines_in_rows[textline_belongs_to_index].insert(existing_textline_row_index, textline)
                            textline_inserted = True
                            break

                    if not textline_inserted:
                        textlines_in_rows[textline_belongs_to_index].append(textline)

                else:

                    # if this is the first line
                    if last_textline == None:

                        y_difference = math.floor((xml_rule.region.y2 - textline.region.y1) / ASSUMED_TEXT_HEIGHT) - 1
                        if y_difference > 0:
                            for i in range(y_difference):
                                textlines_in_rows.append([])

                        textlines_in_rows.append([textline])

                    else:

                        y_difference = math.floor((last_textline.region.y1 - textline.region.y2) / ASSUMED_TEXT_HEIGHT) - 1
                        if y_difference > 0:
                            for i in range(y_difference):
                                textlines_in_rows.append([])

                        textlines_in_rows.append([textline])

                last_textline = textline

            last_textline = None
            for textlines_in_row in textlines_in_rows:
                result_in_row = ""
                col_index = 0
                if len(textlines_in_row) == 0:
                    result.append("")
                    continue
                if len(textlines_in_row) == 0:
                    result_in_row = ""
                for col_index, textline_in_row in enumerate(textlines_in_row):
                    if re.match("[.]+", textline_in_row.text):
                        continue
                    if col_index == 0:
                        x_difference = math.floor((textline_in_row.region.x1 - xml_rule.region.x1) / ASSUMED_TEXT_WIDTH)
                        spaces = " " * x_difference
                        result_in_row = spaces + textline_in_row.text
                    else:
                        x_difference = math.floor((textline_in_row.region.x1 - xml_rule.region.x1) / ASSUMED_TEXT_WIDTH) - len(result_in_row)

                        spaces = " " * x_difference
                        result_in_row = result_in_row + spaces + textline_in_row.text
                    if col_index == (len(textlines_in_row) - 1):
                        x_difference = math.floor(((xml_rule.region.x2 - xml_rule.region.x1) / ASSUMED_TEXT_WIDTH) - len(result_in_row))
                        spaces = " " * x_difference
                        result_in_row = result_in_row + spaces

                    last_textline = textline_in_row

                result.append(result_in_row)

        return result


class XMLPage:

    def __init__(self, xml_container, page_num):
        self.xml_container = xml_container
        self.page_num = page_num
        self.region = XMLRegion()
        self.xml = self.xml_container.document.document_pages.all()[page_num-1].xml
        self.width = self.xml_container.document.document_pages.all()[page_num-1].width
        self.height = self.xml_container.document.document_pages.all()[page_num-1].height
        self.textlines = []
        self.load_all_textlines()

    def load_all_textlines(self):

        root = ET.fromstring(self.xml)
        textline_elements = root.findall('.//textline')

        pageEl = root.find('.//page')
        page_bbox_str = pageEl.attrib['bbox']
        page_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                        page_bbox_str,
                                        re.IGNORECASE
                                        )

        self.region.x1 = Decimal(page_bbox_search.group(1))
        self.region.y1 = Decimal(page_bbox_search.group(2))
        self.region.x2 = Decimal(page_bbox_search.group(3))
        self.region.y2 = Decimal(page_bbox_search.group(4))

        # put all textlines into page
        for textline_element in textline_elements:
            textline_bbox_str = textline_element.attrib['bbox']
            textline_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                textline_bbox_str,
                                                re.IGNORECASE
                                                )

            textline = TextLine(self)

            textline.region.x1 = Decimal(textline_bbox_search.group(1))
            textline.region.y1 = Decimal(textline_bbox_search.group(2))
            textline.region.x2 = Decimal(textline_bbox_search.group(3))
            textline.region.y2 = Decimal(textline_bbox_search.group(4))
            textline.textline_el = textline_element

            if textline.region.x1 == None or textline.region.x2 == None or textline.region.y1 == None or textline.region.y2 == None:
                continue

            #if self.rule.region.overlaps(textline.region):
                #self.textlines.append(textline)
            self.textlines.append(textline)

        # filter out all text that
        for textline in self.textlines:
            result_text = ""
            # spaces in xml occupies y coordinates larger than it is
            # we resolve that in below code
            actual_textline_x1 = None
            actual_textline_y1 = None
            actual_textline_x2 = None
            actual_textline_y2 = None
            prev_text = None
            for text_el in textline.textline_el:
                if text_el.text != '\n' and 'bbox' in text_el.attrib:
                    text = XMLText()
                    text_bbox_str = text_el.attrib['bbox']
                    text_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                    text_bbox_str,
                                                    re.IGNORECASE
                                                    )
                    text.region.x1 = Decimal(text_bbox_search.group(1))
                    text.region.y1 = Decimal(text_bbox_search.group(2))
                    text.region.x2 = Decimal(text_bbox_search.group(3))
                    text.region.y2 = Decimal(text_bbox_search.group(4))

                    # Add space if previous character is too far away from current one
                    if prev_text != None and (text.region.x1 - prev_text.region.x2) > ASSUMED_TEXT_WIDTH:
                        num_of_spaces_to_be_added = math.floor((text.region.x1 - prev_text.region.x2) / ASSUMED_TEXT_WIDTH) + 1
                        spaces_to_be_added = " " * num_of_spaces_to_be_added

                        text_el.text = spaces_to_be_added + text_el.text

                    text.text = text_el.text

                    textline.text_elements.append(text)

                    if text_el.text != ' ':
                        if actual_textline_x1 == None:
                            actual_textline_x1 = text.region.x1
                        elif text.region.x1 < actual_textline_x1:
                            actual_textline_x1 = text.region.x1

                    if text_el.text != ' ':
                        if actual_textline_y1 == None:
                            actual_textline_y1 = text.region.y1
                        elif text.region.y1 < actual_textline_y1:
                            actual_textline_y1 = text.region.y1

                    if text_el.text != ' ':
                        if actual_textline_x2 == None:
                            actual_textline_x2 = text.region.x2
                        elif text.region.x2 > actual_textline_x2:
                            actual_textline_x2 = text.region.x2

                    if text_el.text != ' ':
                        if actual_textline_y2 == None:
                            actual_textline_y2 = text.region.y2
                        elif text.region.y2 > actual_textline_y2:
                            actual_textline_y2 = text.region.y2

                    #if self.rule.region.contains(text.region):
                        #result_text = result_text + text.text
                    result_text = result_text + text.text

                    prev_text = text
            textline.text = result_text

            textline.region.x1 = actual_textline_x1
            textline.region.y1 = actual_textline_y1
            textline.region.x2 = actual_textline_x2
            textline.region.y2 = actual_textline_y2

        self.sort_textlines()

    def sort_textlines(self):
        def compare(a, b):
            if a.region.x1 == None or a.region.x2 == None or a.region.y1 == None or a.region.y2 == None:
                return 0
            if b.region.x1 == None or b.region.x2 == None or b.region.y1 == None or b.region.y2 == None:
                return 0

            if (math.floor(a.region.y1) > math.floor(b.region.y2)):
                return 1
            elif (math.floor(a.region.y2) < math.floor(b.region.y1)):
                return -1
            else:
                if (math.floor(a.region.x2) < math.floor(b.region.x1)):
                    return 1
                elif (math.floor(a.region.x1) > math.floor(b.region.x2)):
                    return -1
                else:
                    return 0

        self.textlines = sorted(
            self.textlines, key=functools.cmp_to_key(compare), reverse=True)


class XMLRegion:

    def __init__(self):
        self.x1 = Decimal(0.00)
        self.y1 = Decimal(0.00)
        self.x2 = Decimal(100.00)
        self.y2 = Decimal(100.00)

    def contains(self, another_region):
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if self.x1 <= another_region.x1 and self.x2 >= another_region.x2 and self.y1 <= another_region.y1 and self.y2 >= another_region.y2:
            return True
        else:
            return False

    def overlaps(self, another_region):
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if self.x1 >= another_region.x2 or self.x2 <= another_region.x1 or self.y1 >= another_region.y2 or self.y2 <= another_region.y1:
            return False
        else:
            return True

    def is_in_same_line(self, another_region):
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if ((self.y1 + SAME_LINE_ACCEPTANCE_RANGE) <= another_region.y1 or (self.y1 - SAME_LINE_ACCEPTANCE_RANGE) <= another_region.y1) and self.y2 >= another_region.y2:
            return True
        elif self.y1 <= another_region.y1 and (self.y2 >= (another_region.y1 + SAME_LINE_ACCEPTANCE_RANGE) or self.y2 >= (another_region.y1 - SAME_LINE_ACCEPTANCE_RANGE)):
            return True
        elif self.y1 >= another_region.y1 and self.y2 <= another_region.y2:
            return True
        elif self.y1 <= another_region.y1 and self.y2 >= another_region.y2:
            return True
        else:
            return False


class TextLine:

    def __init__(self, page):
        self.page = page
        self.region = XMLRegion()
        self.region.x1 = Decimal(0.00)
        self.region.y1 = Decimal(0.00)
        self.region.x2 = Decimal(0.00)
        self.region.y2 = Decimal(0.00)
        self.textline_element = None
        self.text_elements = []
        self.text = ""


class XMLText:

    def __init__(self):
        self.region = XMLRegion()
        self.region.x1 = Decimal(0.00)
        self.region.y1 = Decimal(0.00)
        self.region.x2 = Decimal(0.00)
        self.region.y2 = Decimal(0.00)
        self.text = ""


class XMLRule:

    def __init__(self, rule):
        self.rule = rule
        self.region = XMLRegion()
        self.region.x1 = Decimal(0.00)
        self.region.y1 = Decimal(0.00)
        self.region.x2 = Decimal(0.00)
        self.region.y2 = Decimal(0.00)

