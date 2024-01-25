from .xml_helpers import XMLPage
from decimal import Decimal
import math
import re

from parsers.models.rule import Rule
from parsers.models.rule_type import RuleType

from parsers.helpers.get_document_nos_from_range import get_document_nos_from_range
from parsers.helpers.rule_extractor import RuleExtractor

SAME_LINE_ACCEPTANCE_RANGE = Decimal(0.0)
ASSUMED_TEXT_WIDTH = Decimal(0.5)
ASSUMED_TEXT_HEIGHT = Decimal(1.0)


class DocumentParser:

    def __init__(self, parser, document):
        self.parser = parser
        self.document = document
        self.xml_pages = []
        self.parsed_result = []

    def extract_all_text_in_one_page(self, page_num):

        rule = Rule()
        rule.rule_type = RuleType.TEXTFIELD.value
        rule.pages = str(page_num)
        rule.x1 = Decimal(0.00)
        rule.x2 = Decimal(100.00)
        rule.y1 = Decimal(0.00)
        rule.y2 = Decimal(100.00)

        return self.extract(rule)

        """page_nums = [int(page_num)]

        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in self.xml_pages if x.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                self.xml_pages.append(xml_page)
        self.xml_pages.sort(key=lambda x: x.page_num)

        xml_page = [x for x in self.xml_pages if x.page_num == page_num][0]

        # Get All Textlines within Area
        textlines_within_area = []
        for textline in xml_page.textlines:
            # Tailored for Google Invoices
            if re.match(r'[.]+', textline.text):
                continue

            textlines_within_area.append(textline)

        text_in_rows = []
        textlines_in_rows = []
        # Organize Textlines in Row by Row
        # textlines_in_current_row = []
        # while len(textlines_within_area) > 0:
        #    current_textline = textlines_within_area.pop(0)

        toppest_textline = None
        toppest_textline_index = 0
        while len(textlines_within_area) > 0:

            if toppest_textline == None:
                toppest_textline = textlines_within_area[0]
                toppest_textline_index = 0

            for textline_index in range(0, len(textlines_within_area) - 1):

                if textline_index == toppest_textline_index:
                    continue

                if toppest_textline.region.is_in_same_line(textlines_within_area[textline_index].region):
                    if textlines_within_area[textline_index].region.y2 > toppest_textline.region.y2:
                        toppest_textline = textlines_within_area[textline_index]
                        toppest_textline_index = textline_index

            # found the toppest line.
            # Now find all textlines in the same line
            textlines_that_are_the_same_line_with_toppest = []
            textline_indexes_that_are_the_same_line_with_toppest = []

            textlines_that_are_the_same_line_with_toppest.append(
                toppest_textline)
            textlines_within_area.pop(toppest_textline_index)
            textline_index = 0
            # for textline_index in range(0, len(textlines_within_area)):
            while textline_index < len(textlines_within_area):

                if textlines_within_area[textline_index].region.y2 < toppest_textline.region.y1:
                    break

                if toppest_textline.region.is_in_same_line(textlines_within_area[textline_index].region):

                    overlapping_column_with_existing_textlines = False
                    for textline_that_are_the_same_line_with_toppest in textlines_that_are_the_same_line_with_toppest:
                        if textline_that_are_the_same_line_with_toppest == toppest_textline:
                            continue
                        if textline_that_are_the_same_line_with_toppest.region.is_in_same_column(toppest_textline.region):
                            overlapping_column_with_existing_textlines = True
                            break

                    if not overlapping_column_with_existing_textlines:
                        textlines_that_are_the_same_line_with_toppest.append(
                            textlines_within_area[textline_index])
                        textline_indexes_that_are_the_same_line_with_toppest.append(
                            textline_index)
                        textlines_within_area.pop(
                            textline_index)
                        continue

                textline_index += 1

            textlines_that_are_the_same_line_with_toppest.sort(
                key=lambda x: x.region.x1)

            textlines_in_rows.append(
                textlines_that_are_the_same_line_with_toppest)

            toppest_textline = None
            toppest_textline_index = 0

        if len(textlines_in_rows) > 0 and len(textlines_in_rows[0]) > 0:
            num_of_empty_lines_to_be_prepend = math.floor(
                (100 - textlines_in_rows[0][0].region.y2) / xml_page.median_text_height)
            for i in range(num_of_empty_lines_to_be_prepend):
                num_of_spaces_to_be_prepend = math.floor(
                    (100 - 0) / xml_page.median_text_width)
                spaces = " " * num_of_spaces_to_be_prepend
                text_in_rows.append(spaces)

        previous_textline = None
        for textlines_in_row in textlines_in_rows:
            text_in_current_row = ""
            for current_textline_index in range(0, len(textlines_in_row)):
                current_textline = textlines_in_row[current_textline_index]

                if current_textline_index == 0:
                    # if current textline is the first line in the row,
                    # add empty lines before
                    if previous_textline != None:
                        num_of_empty_lines_to_be_prepend = math.floor(
                            (previous_textline.region.y1 - current_textline.region.y2) / xml_page.median_text_height)
                        for i in range(num_of_empty_lines_to_be_prepend):
                            num_of_spaces_to_be_prepend = math.floor(
                                (100 - 0) / xml_page.median_text_width)
                            spaces = " " * num_of_spaces_to_be_prepend
                            text_in_rows.append(spaces)
                    # if current textline is the first line in the row,
                    # add spaces before
                    num_of_spaces_to_be_prepend = math.floor(
                        (current_textline.region.x1 - 0) / xml_page.median_text_width)
                    spaces = " " * num_of_spaces_to_be_prepend
                    text_in_current_row = spaces + current_textline.text
                # if current textline has previous line,
                # add spaces before
                else:
                    num_of_spaces_to_be_prepend = math.floor(
                        (current_textline.region.x1 - 0) / xml_page.median_text_width) - len(text_in_current_row)
                    spaces = " " * num_of_spaces_to_be_prepend
                    text_in_current_row = text_in_current_row + spaces + current_textline.text

                # add spaces if textline is the last
                if current_textline_index == (len(textlines_in_row) - 1):
                    num_of_spaces_to_be_prepend = math.floor(
                        (100 - 0) / xml_page.median_text_width) - len(text_in_current_row)
                    spaces = " " * num_of_spaces_to_be_prepend
                    text_in_current_row = text_in_current_row + spaces

                previous_textline = current_textline

            text_in_rows.append(text_in_current_row)

        # append empty textlines in the end
        if len(textlines_in_rows) > 0:
            last_textline = textlines_in_rows[-1][-1]
            if len(textlines_within_area) == 0:
                num_of_empty_lines_to_be_append = math.floor(
                    (last_textline.region.y1 - 0) / xml_page.median_text_height)
                for i in range(num_of_empty_lines_to_be_append):
                    text_in_rows.append("")

        return text_in_rows"""

    def extract_all_text_in_all_pages(self):

        textlines_in_all_pages = []

        page_nums = range(1, self.document.total_page_num + 1)

        for page_num in page_nums:
            textlines_in_all_pages += self.extract_all_text_in_one_page(
                page_num)

        return textlines_in_all_pages

    def extract(self, rule):
        # Add to xml page if not yet initialized
        # if rule.anchor_page_num == None:
        #    pages = rule.pages
        # else:
        #    pages = rule.pages + "," + str(rule.anchor_page_num)
        page_nums = get_document_nos_from_range(
            rule.pages[:], 1, self.document.total_page_num)

        if len(self.document.document_pages.filter(ocred=False, page_num__in=page_nums)) > 0:
            if rule.rule_type == RuleType.TABLE.value:
                return [["Please wait until the document finishes OCR"]]
            else:
                return ["Please wait until the document finishes OCR"]

        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in self.xml_pages if x.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                self.xml_pages.append(xml_page)
        self.xml_pages.sort(key=lambda x: x.page_num)

        if rule.rule_type == RuleType.TEXTFIELD.value:

            result = self.extract_textfield(
                rule, self.xml_pages, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value:

            result = self.extract_anchored_textfield(
                rule, self.xml_pages, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.TABLE.value:

            result = self.extract_table(
                rule, self.xml_pages, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.BARCODE.value:

            result = self.extract_barcode(
                rule, self.xml_pages, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.ACROBAT_FORM.value:

            result = self.extract_acrobat_form(
                rule, self.xml_pages, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.INPUT_TEXTFIELD.value:

            return ""

        elif rule.rule_type == RuleType.INPUT_DROPDOWN.value:

            return ""

        return result

    def extract_textfield(self, rule, xml_pages, parsed_result=[]):

        rule_extractor = RuleExtractor(
            self.parser, rule, self.document, xml_pages)

        return rule_extractor.extract_textfield(parsed_result=parsed_result)

    def extract_table(self, rule, xml_pages, parsed_result=[]):

        rule_extractor = RuleExtractor(self.parser,
                                       rule, self.document, xml_pages)

        return rule_extractor.extract_table(parsed_result=parsed_result)

    def get_anchor_relative_region(self, rule, parsed_result=[]):

        xml_pages = []

        page_nums = get_document_nos_from_range(
            rule.pages + "," + str(rule.anchor_page_num), 1, self.document.total_page_num)

        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in self.xml_pages if x.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                xml_pages.append(xml_page)
        xml_pages.sort(key=lambda x: x.page_num)

        # Add to xml page if not yet initialized
        page_nums = get_document_nos_from_range(
            rule.pages, 1, self.document.total_page_num)
        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in xml_pages if x.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                xml_pages.append(xml_page)
        xml_pages.sort(key=lambda x: x.page_num)

        rule_extractor = RuleExtractor(self.parser,
                                       rule, self.document, xml_pages)
        return rule_extractor.get_anchor_relative_region(parsed_result=parsed_result)

    def extract_anchored_textfield(self, rule, xml_pages, parsed_result=[]):
        rule_extractor = RuleExtractor(self.parser,
                                       rule, self.document, xml_pages)
        return rule_extractor.extract_anchored_textfield(parsed_result=parsed_result)

    def extract_barcode(self, rule, xml_pages, parsed_result=[]):

        rule_extractor = RuleExtractor(
            self.parser, rule, self.document, xml_pages)

        return rule_extractor.extract_barcode(parsed_result=parsed_result)

    def extract_acrobat_form(self, rule, xml_pages, parsed_result=[]):

        rule_extractor = RuleExtractor(
            self.parser, rule, self.document, xml_pages)

        return rule_extractor.extract_acrobat_form(parsed_result=parsed_result)
