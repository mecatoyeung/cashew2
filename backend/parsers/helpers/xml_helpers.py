import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
import statistics
from decimal import Decimal
from pathlib import Path

#SAME_LINE_ACCEPTANCE_RANGE = Decimal(2.0)
#ASSUMED_TEXT_WIDTH = Decimal(0.3)
#ASSUMED_TEXT_HEIGHT = Decimal(0.6)


class XMLPage:

    def __init__(self, document_parser, page_num):
        self.document_parser = document_parser
        self.page_num = page_num
        self.region = XMLRegion()
        try:
            self.xml = document_parser.document.document_pages.get(
                page_num=page_num).xml
        except:
            self.xml = "<?xml version='1.0' encoding='utf-8'?><pages></pages>"
        root = ET.fromstring(self.xml.replace('\n', ''))

        page_el = root.find('.//page')
        if page_el != None:
            page_bbox_str = page_el.attrib['bbox']
            page_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*)',
                                         page_bbox_str,
                                         re.IGNORECASE
                                         )
            self.width = Decimal(page_bbox_search.group(3))
            self.height = Decimal(page_bbox_search.group(4))
        else:
            try:
                self.width = document_parser.document.document_pages.get(
                    page_num=page_num).width
                self.height = document_parser.document.document_pages.get(
                    page_num=page_num).height
            except:
                self.width = 2481
                self.height = 3508
        self.text_widths = []
        self.text_heights = []
        self.median_of_text_widths = self.document_parser.parser.assumed_text_width * self.width / Decimal(1000.00)
        self.median_of_text_heights = self.document_parser.parser.assumed_text_height * self.height / Decimal(1000.00)
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
            textline_bbox_search = re.search('([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*)',
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

        figures = root.findall('.//figure')
        for figure in figures:
            accumulated_xml_texts = []
            accumulated_text_elements = []
            prev_text_element = None
            prev_xml_text = None

            textline_element = ET.Element("textline")
            text_elements = figure.findall('.//text')
            textline_text = ""
            for text_element in text_elements:

                curr_text_element = text_element

                curr_xml_text = XMLText()
                curr_xml_text.text = curr_text_element.text

                text_bbox_str = curr_text_element.attrib['bbox']
                text_bbox_search = re.search('([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*)',
                                             text_bbox_str,
                                             re.IGNORECASE
                                             )

                curr_xml_text.region.x1 = Decimal(
                    text_bbox_search.group(1)) / self.width * Decimal(100.00)
                curr_xml_text.region.y1 = Decimal(
                    text_bbox_search.group(2)) / self.height * Decimal(100.00)
                curr_xml_text.region.x2 = Decimal(
                    text_bbox_search.group(3)) / self.width * Decimal(100.00)
                curr_xml_text.region.y2 = Decimal(
                    text_bbox_search.group(4)) / self.height * Decimal(100.00)

                if prev_text_element == None:
                    textline = XMLTextLine(self)
                    accumulated_xml_texts.append(curr_xml_text)
                    accumulated_text_elements.append(curr_text_element)
                    textline.region.x1 = Decimal(
                        text_bbox_search.group(1)) / self.width * Decimal(100.00)
                    textline.region.y1 = Decimal(
                        text_bbox_search.group(2)) / self.height * Decimal(100.00)
                    textline.region.y2 = Decimal(
                        text_bbox_search.group(4)) / self.height * Decimal(100.00)
                    textline_text = textline_text + curr_text_element.text
                else:
                    if curr_xml_text.region.x1 == prev_xml_text.region.x2:
                        accumulated_xml_texts.append(curr_xml_text)
                        accumulated_text_elements.append(curr_text_element)
                        textline_text = textline_text + curr_text_element.text
                    else:
                        textline.region.x2 = Decimal(
                        text_bbox_search.group(3)) / self.width * Decimal(100.00)
                        textline_element.set('bbox', str(textline.region.x1) + ',' + str(textline.region.y1) + ',' + str(textline.region.x2) + ',' + str(textline.region.y2))
                        
                        textline.textline_element = textline_element
                        #textline.text_elements = accumulated_xml_texts
                        for accumulated_text_element in accumulated_text_elements:
                            textline.textline_element.append(accumulated_text_element)
                        textline.text = textline_text
                        self.textlines.append(textline)

                        textline = XMLTextLine(self)
                        textline.region.x1 = Decimal(
                            text_bbox_search.group(1)) / self.width * Decimal(100.00)
                        textline.region.y1 = Decimal(
                            text_bbox_search.group(2)) / self.height * Decimal(100.00)
                        textline.region.y2 = Decimal(
                            text_bbox_search.group(4)) / self.height * Decimal(100.00)
                        textline_text = curr_xml_text.text
                        accumulated_xml_texts = [curr_xml_text]
                        accumulated_text_elements = [curr_text_element]
                        textline_element = ET.Element("textline")


                prev_text_element = curr_text_element
                prev_xml_text = curr_xml_text
                prev_xml_text.region.x1 = Decimal(
                    text_bbox_search.group(1)) / self.width * Decimal(100.00)
                prev_xml_text.region.y1 = Decimal(
                    text_bbox_search.group(2)) / self.height * Decimal(100.00)
                prev_xml_text.region.x2 = Decimal(
                    text_bbox_search.group(3)) / self.width * Decimal(100.00)
                prev_xml_text.region.y2 = Decimal(
                    text_bbox_search.group(4)) / self.height * Decimal(100.00)
                
            if len(accumulated_xml_texts) > 0:
                textline.region.x2 = Decimal(
                text_bbox_search.group(3)) / self.width * Decimal(100.00)
                textline_element.set('bbox', str(textline.region.x1) + ',' + str(textline.region.y1) + ',' + str(textline.region.x2) + ',' + str(textline.region.y2))
                
                textline.textline_element = textline_element
                #textline.text_elements = accumulated_xml_texts
                for accumulated_text_element in accumulated_text_elements:
                    textline.textline_element.append(accumulated_text_element)
                textline.text = textline_text
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
            text_els = textline.textline_element.findall('.//text')

            for i in range(len(text_els)):
                text_el = text_els[i]

                if text_el.text != '\n' and text_el.text != '' and text_el.text != None and 'bbox' in text_el.attrib:

                    text = XMLText()
                    text_bbox_str = text_el.attrib['bbox']
                    text_bbox_search = re.search('([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*),([-]*[0-9]{1,4}(?:.[0-9]{3})*)',
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

        

        # split textline into textlines if there is empty text betwwen them
        new_textlines = []
        for textline in self.textlines:
            splitted = False
            text_elements = textline.text_elements
            prev_text_els = []
            for i in range(len(text_elements)):
                text_el = text_elements[i]

                if len(prev_text_els) > 0:
                    if text_el.region.x1 >= prev_text_el.region.x2 + Decimal(0.5):

                        splitted = True
                        new_textline = XMLTextLine(self)
                        if len(prev_text_els) > 0:
                            new_textline.region.x1 = prev_text_els[0].region.x1
                        else:
                            new_textline.region.x1 = text_el.region.x1
                        new_textline.region.y1 = textline.region.y1
                        if len(prev_text_els) > 0:
                            new_textline.region.x2 = prev_text_els[-1].region.x2
                        else:
                            new_textline.region.x2 = text_el.region.x2
                        new_textline.region.y2 = textline.region.y2
                        new_textline.text_elements = prev_text_els
                        for text_element in prev_text_els:
                            new_textline.text = new_textline.text + text_element.text
                        new_textlines.append(new_textline)
                        prev_text_els = []
                        prev_text_els.append(text_el)

                    else:
                        prev_text_els.append(text_el)
                else:
                    prev_text_els.append(text_el)

                if i == (len(text_elements) - 1) and len(prev_text_els) > 0:
                    splitted = True
                    new_textline = XMLTextLine(self)
                    if len(prev_text_els) > 0:
                        new_textline.region.x1 = prev_text_els[0].region.x1
                    else:
                        new_textline.region.x1 = text_el.region.x1
                    new_textline.region.y1 = textline.region.y1
                    if len(prev_text_els) > 0:
                        new_textline.region.x2 = prev_text_els[-1].region.x2
                    else:
                        new_textline.region.x2 = text_el.region.x2
                    new_textline.region.y2 = textline.region.y2
                    new_textline.text_elements = prev_text_els
                    for text_element in prev_text_els:
                        new_textline.text = new_textline.text + text_element.text
                    new_textlines.append(new_textline)
                    prev_text_els = []

                prev_text_el = text_el
                

            if not splitted:
                new_textlines.append(textline)

        self.textlines = new_textlines

        self.sort_textlines()

        filtered_textlines = []
        for textline in self.textlines:

            # Fix for Google Invoices
            if re.match(r'[.]{2,}', textline.text):
                continue

            filtered_textlines.append(textline)

        self.textlines = filtered_textlines

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
        self.median_of_text_widths = self.document_parser.parser.assumed_text_width * self.width / Decimal(1000.00)
        self.median_of_text_heights = self.document_parser.parser.assumed_text_height * self.height / Decimal(1000.00)

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
                while j >= 0 and compare(key, arr[j]) >= 0:
                    arr[j+1] = arr[j]  # Shift elements to the right
                    j -= 1
                arr[j+1] = key

            return arr

        def compare(a, b):

            if a.region.x1 == None or a.region.x2 == None or a.region.y1 == None or a.region.y2 == None:
                return 0
            if b.region.x1 == None or b.region.x2 == None or b.region.y1 == None or b.region.y2 == None:
                return 0

            if (a.region.y2 > b.region.y2):
                return 1
            elif (a.region.y2 < b.region.y2):
                return -1
            elif (a.region.y1 > b.region.y1):
                return 1
            elif (a.region.y1 < b.region.y1):
                return -1
            elif (a.region.is_in_same_line(b.region, 
                    same_line_acceptance_range=self.document_parser.parser.same_line_acceptance_range)):
                """for item_before in arr_before:
                    if a.region.is_in_same_column(item_before.region):
                        return -1"""
                if a.region.x1 < b.region.x1:
                    return 1
                #elif a.region.x2 < b.region.x2:
                    #return 1
                else:
                    return -1
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

    def is_in_same_line(self, another_region, same_line_acceptance_range=0.35):
        SAME_LINE_ACCEPTANCE_RANGE = (self.y2 - self.y1) * Decimal(0.35) # ZA Bank need 0.6 in Date and 日期, 1.0 in bottom address, Times Publishing GRN need 0.35
        SAME_LINE_ACCEPTANCE_RANGE = (self.y2 - self.y1) * same_line_acceptance_range
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if self.y1 >= another_region.y1 and (self.y1 + SAME_LINE_ACCEPTANCE_RANGE) <= another_region.y2:
            return True
        if (self.y2 - SAME_LINE_ACCEPTANCE_RANGE) >= another_region.y1 and self.y2 <= another_region.y2:
            return True
        if another_region.y1 >= self.y1 and (another_region.y1 + SAME_LINE_ACCEPTANCE_RANGE) <= self.y2:
            return True
        if (another_region.y2 - SAME_LINE_ACCEPTANCE_RANGE) >= self.y1 and another_region.y2 <= self.y2:
            return True
        return False

    def is_in_same_column(self, another_region, same_column_acceptance_range=0.25):
        SAME_COLUMN_ACCEPTANCE_RANGE = (self.x2 - self.x1) * Decimal(0.25)
        SAME_COLUMN_ACCEPTANCE_RANGE = (self.x2 - self.x1) * same_column_acceptance_range
        if self.x1 == None or self.x2 == None or self.y1 == None or self.y2 == None:
            return False
        if another_region.x1 == None or another_region.x2 == None or another_region.y1 == None or another_region.y2 == None:
            return False
        if self.x1 >= another_region.x1 and (self.x1 + SAME_COLUMN_ACCEPTANCE_RANGE) <= another_region.x2:
            return True
        if (self.x2 - SAME_COLUMN_ACCEPTANCE_RANGE) >= another_region.x1 and self.x2 <= another_region.x2:
            return True
        if another_region.x1 >= self.x1 and (another_region.x1 + SAME_COLUMN_ACCEPTANCE_RANGE) <= self.x2:
            return True
        if (another_region.x2 - SAME_COLUMN_ACCEPTANCE_RANGE) >= self.x1 and another_region.x2 <= self.x2:
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
