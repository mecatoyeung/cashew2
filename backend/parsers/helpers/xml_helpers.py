import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
import statistics
from decimal import Decimal

SAME_LINE_ACCEPTANCE_RANGE = Decimal(0.0)
ASSUMED_TEXT_WIDTH = Decimal(5.0)
ASSUMED_TEXT_HEIGHT = Decimal(10.0)

def isEnglish(s):
    return s.isascii() and s.isalpha()

def isChinese(s):
    return re.search(u'[\u4e00-\u9fff]', s)

class XMLPage:

    def __init__(self, document_parser, page_num):
        self.document_parser = document_parser
        self.page_num = page_num
        self.region = XMLRegion()
        self.xml = self.document_parser.document.document_pages.all()[page_num-1].xml
        self.width = self.document_parser.document.document_pages.all()[page_num-1].width
        self.height = self.document_parser.document.document_pages.all()[page_num-1].height
        self.text_widths = []
        self.text_heights = []
        self.median_text_width = ASSUMED_TEXT_WIDTH
        self.median_text_height = ASSUMED_TEXT_HEIGHT
        self.textlines = []
        self.load_all_textlines()

    def load_all_textlines(self):

        root = ET.fromstring(self.xml)
        textline_elements = root.findall('.//textline')

        page_el = root.find('.//page')
        page_bbox_str = page_el.attrib['bbox']
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

            textline = XMLTextLine(self)

            textline.region.x1 = Decimal(textline_bbox_search.group(1))
            textline.region.y1 = Decimal(textline_bbox_search.group(2))
            textline.region.x2 = Decimal(textline_bbox_search.group(3))
            textline.region.y2 = Decimal(textline_bbox_search.group(4))
            textline.textline_element = textline_element

            if textline.region.x1 == None or textline.region.x2 == None or textline.region.y1 == None or textline.region.y2 == None:
                continue

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
            for text_el in textline.textline_element.findall('.//text'):
                if text_el.text != '\n' and text_el.text != '' and 'bbox' in text_el.attrib:

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

                    prev_text_width = text.region.x2 - text.region.x1

                    text_width = text.region.x2 - text.region.x1
                    self.text_widths.append(text_width)

                    text_height = text.region.y2 - text.region.y1
                    self.text_heights.append(text_height)

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

                    result_text = result_text + text.text

                    prev_text = text

                if text_el.text == ' ' and isEnglish(prev_text.text):
                    text = XMLText()
                    text.text = " "
                    textline.text_elements.append(text)

                    result_text = result_text + text.text
                    
            textline.text = result_text

            textline.region.x1 = actual_textline_x1
            textline.region.y1 = actual_textline_y1
            textline.region.x2 = actual_textline_x2
            textline.region.y2 = actual_textline_y2

        self.sort_textlines()

        self.median_text_width = statistics.mean(self.text_widths)
        self.median_text_height = statistics.mean(self.text_heights)

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
        if self.contains(another_region):
            return True
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if self.x1 >= another_region.x2 or self.x2 <= another_region.x1:
            return False
        if self.y1 >= another_region.y2 or self.y2 <= another_region.y1:
            return False
        else:
            return True

    def is_in_same_line(self, another_region):
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if (((self.y2 + SAME_LINE_ACCEPTANCE_RANGE) >= another_region.y1 and self.y1 <= (another_region.y1 + SAME_LINE_ACCEPTANCE_RANGE)) or (self.y1 <= (another_region.y2 + SAME_LINE_ACCEPTANCE_RANGE) and (self.y1  + SAME_LINE_ACCEPTANCE_RANGE) >= another_region.y1)):
            return True
        else:
            return False


class XMLTextLine:

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
        self.text_width = Decimal(0.00)


class XMLText:

    def __init__(self):
        self.region = XMLRegion()
        self.region.x1 = Decimal(0.00)
        self.region.y1 = Decimal(0.00)
        self.region.x2 = Decimal(0.00)
        self.region.y2 = Decimal(0.00)
        self.text = ""


class XMLRule:

    def __init__(self, xml_page, rule):
        self.rule = rule
        self.region = XMLRegion()
        self.region.x1 = Decimal(0.00)
        self.region.y1 = Decimal(0.00)
        self.region.x2 = Decimal(0.00)
        self.region.y2 = Decimal(0.00)

        self.region.x1 = rule.x1 / Decimal(100.00) * xml_page.region.x2
        self.region.x2 = rule.x2 / Decimal(100.00) * xml_page.region.x2
        self.region.y1 = rule.y1 / Decimal(100.00) * xml_page.region.y2
        self.region.y2 = rule.y2 / Decimal(100.00) * xml_page.region.y2