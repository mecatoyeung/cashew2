import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
import statistics
from decimal import Decimal
from pathlib import Path

from .path_helper import xml_path
from parsers.helpers.is_chinese import is_chinese

SAME_LINE_ACCEPTANCE_RANGE = Decimal(0.0)
ASSUMED_TEXT_WIDTH = Decimal(0.3)
ASSUMED_TEXT_HEIGHT = Decimal(0.6)


def is_english(s):
    return s.isascii() and s.isalpha()


class XMLPage:

    def __init__(self, document_parser, page_num):
        self.document_parser = document_parser
        self.page_num = page_num
        self.region = XMLRegion()
        self.xml = document_parser.document.document_pages.get(
            page_num=page_num).xml
        root = ET.fromstring(self.xml.replace('\n', ''))

        page_el = root.find('.//page')
        if page_el != None:
            page_bbox_str = page_el.attrib['bbox']
            page_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                         page_bbox_str,
                                         re.IGNORECASE
                                         )
            self.width = Decimal(page_bbox_search.group(3))
            self.height = Decimal(page_bbox_search.group(4))
        else:
            self.width = document_parser.document.document_pages.get(
                page_num=page_num).width
            self.height = document_parser.document.document_pages.get(
                page_num=page_num).height
        self.text_widths = []
        self.text_heights = []
        self.median_of_text_widths = ASSUMED_TEXT_WIDTH
        self.median_of_text_heights = ASSUMED_TEXT_HEIGHT
        self.textlines = []
        self.load_all_textlines()

    def load_all_textlines(self):

        self.textlines = []

        root = ET.fromstring(self.xml.replace('\n', ''))
        textline_elements = root.findall('.//textline')

        self.region.x1 = Decimal(0)
        self.region.y1 = Decimal(0)
        self.region.x2 = Decimal(100)
        self.region.y2 = Decimal(100)

        # put all textlines into page
        for textline_element in textline_elements:
            textline_bbox_str = textline_element.attrib['bbox']
            textline_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                             textline_bbox_str,
                                             re.IGNORECASE
                                             )

            textline = XMLTextLine(self)

            textline.region.x1 = Decimal(
                textline_bbox_search.group(1)) / self.width * Decimal(100.00)
            textline.region.y1 = Decimal(
                textline_bbox_search.group(2)) / self.height * Decimal(100.00)
            textline.region.x2 = Decimal(
                textline_bbox_search.group(3)) / self.width * Decimal(100.00)
            textline.region.y2 = Decimal(
                textline_bbox_search.group(4)) / self.height * Decimal(100.00)
            textline.textline_element = textline_element

            if textline.region.x1 == None or textline.region.x2 == None or textline.region.y1 == None or textline.region.y2 == None:
                continue

            self.textlines.append(textline)

        # split textline into textlines if there is empty text betwwen them

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
            text_els = textline.textline_element.findall('.//text')
            for i in range(len(text_els)):
                text_el = text_els[i]

                if text_el.text != '\n' and text_el.text != '' and text_el.text != None and 'bbox' in text_el.attrib:

                    text = XMLText()
                    text_bbox_str = text_el.attrib['bbox']
                    text_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                 text_bbox_str,
                                                 re.IGNORECASE
                                                 )
                    text.region.x1 = Decimal(text_bbox_search.group(
                        1)) / self.width * Decimal(100.00)
                    text.region.y1 = Decimal(text_bbox_search.group(
                        2)) / self.height * Decimal(100.00)
                    text.region.x2 = Decimal(text_bbox_search.group(
                        3)) / self.width * Decimal(100.00)
                    text.region.y2 = Decimal(text_bbox_search.group(
                        4)) / self.height * Decimal(100.00)

                    prev_text_width = text.region.x2 - text.region.x1

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

                elif (text_el.text == ' ' and 'bbox' not in text_el.attrib) or text_el.text == '':

                    if prev_text == None:
                        continue

                    text = XMLText()
                    text.text = " "

                    text.region.x1 = prev_text.region.x2
                    text.region.y1 = prev_text.region.y1
                    text.region.x2 = prev_text.region.x2 + prev_text.region.x2 - prev_text.region.x1
                    text.region.y2 = prev_text.region.y2

                    textline.text_elements.append(text)

                    result_text = result_text + text.text

                    prev_text = text
                    prev_text_el = text_el

            textline.text = result_text

            textline.region.x1 = actual_textline_x1
            textline.region.y1 = actual_textline_y1
            textline.region.x2 = actual_textline_x2
            textline.region.y2 = actual_textline_y2

        self.sort_textlines()

        

        # Calculate median of text width and height
        """text_widths = []
        text_heights = []
        for textline in self.textlines:
            for text in textline.text_elements:
                text_width = text.region.x2 - text.region.x1
                text_height = text.region.y2 - text.region.y1
                text_widths.append(text_width)
                text_heights.append(text_height)

        self.median_of_text_widths = statistics.median(text_widths) * 2 / 3
        self.median_of_text_heights = statistics.median(text_heights) * 2 / 3"""
        self.median_of_text_widths = ASSUMED_TEXT_WIDTH
        self.median_of_text_heights = ASSUMED_TEXT_HEIGHT

        return

    def sort_textlines(self):

        def insertionSort(arr):

            n = len(arr)  # Get the length of the array

            if n <= 1:
                return  # If the array has 0 or 1 element, it is already sorted, so return

            for i in range(1, n):  # Iterate over the array starting from the second element
                # Store the current element as the key to be inserted in the right position
                key = arr[i]
                j = i-1
                # Move elements greater than key one position ahead
                while j >= 0 and compare(key, arr[j], arr[:j]) > 0:
                    arr[j+1] = arr[j]  # Shift elements to the right
                    j -= 1
                arr[j+1] = key
                pass

            return arr

        def compare(a, b, arr_before):
            if a.region.x1 == None or a.region.x2 == None or a.region.y1 == None or a.region.y2 == None:
                return 0
            if b.region.x1 == None or b.region.x2 == None or b.region.y1 == None or b.region.y2 == None:
                return 0

            if (a.region.is_in_same_line(b.region)):
                for item_before in arr_before:
                    if a.region.is_in_same_column(item_before.region):
                        return -1
                if a.region.x1 < b.region.x1:
                    return 1
                elif a.region.x2 < b.region.x2:
                    return 1
            elif (a.region.y1 > b.region.y1):
                return 1
            elif (a.region.y2 > b.region.y2):
                return 1
            return -1

        self.textlines = insertionSort(self.textlines)

        if self.textlines == None:
            self.textlines = []

        return


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
        if (self.y1 + SAME_LINE_ACCEPTANCE_RANGE) <= another_region.y2 and self.y1 >= (another_region.y1) and self.y2 >= (another_region.y2):
            return True
        if (self.y1) <= another_region.y1 and (self.y2) <= another_region.y2 and self.y2 >= (another_region.y1 + SAME_LINE_ACCEPTANCE_RANGE):
            return True
        if self.y2 >= (another_region.y2) and (self.y1) <= another_region.y1:
            return True
        if (self.y2) <= another_region.y2 and self.y1 >= (another_region.y1):
            return True
        return False

    def is_in_same_column(self, another_region):
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if self.x1 >= another_region.x1 and self.x1 <= another_region.x2 and self.x2 >= another_region.x1 and self.x2 <= another_region.x2:
            return True
        if self.x1 <= another_region.x1 and self.x2 >= another_region.x2:
            return True
        if self.x1 <= another_region.x1 and self.x2 >= another_region.x1:
            return True
        if self.x1 <= another_region.x2 and self.x2 >= another_region.x2:
            return True
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
