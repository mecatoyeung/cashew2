from .xml_helpers import XMLPage
from decimal import Decimal
import math

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
        page_nums = [int(page_num)]

        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in self.xml_pages if x.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                self.xml_pages.append(xml_page)
        self.xml_pages.sort(key=lambda x: x.page_num)

        textlines_in_all_pages = []

        for page_num in page_nums:

            xml_page = [x for x in self.xml_pages if x.page_num == page_num][0]

            textlines_in_rows = []

            # Get All Textlines within Area
            textlines_within_area = []
            for textline in xml_page.textlines:
                textlines_within_area.append(textline)

            text_in_current_row = ""
            prev_text_width = xml_page.median_text_width
            first_textline_in_row = None
            while len(textlines_within_area) > 0:
                current_textline = textlines_within_area.pop(0)

                text_to_add = ""
                for text_in_textline in current_textline.text_elements:
                    text_to_add = text_to_add + text_in_textline.text

                # if it is a new line, just prepend space append to the row array
                if len(text_in_current_row) == 0:
                    first_textline_in_row = current_textline
                    # if it is the first line, add empty lines
                    if len(textlines_in_rows) == 0:
                        num_of_empty_lines_to_be_prepend = math.floor(
                            (xml_page.region.y2 - current_textline.region.y2) / xml_page.median_text_height)
                        for i in range(num_of_empty_lines_to_be_prepend):
                            textlines_in_rows.append("")
                    # if it is not the first line and there is a line difference between current line and previous line,
                    # add empty lines between them
                    else:
                        if current_textline.region.y2 == None:
                            continue
                        num_of_empty_lines_to_be_prepend = math.floor(
                            (previous_textline.region.y1 - current_textline.region.y2) / xml_page.median_text_height)
                        for i in range(num_of_empty_lines_to_be_prepend):
                            textlines_in_rows.append("")

                    num_of_spaces_to_be_prepend = math.floor(
                        (current_textline.region.x1 - 0) / prev_text_width)
                    spaces = " " * num_of_spaces_to_be_prepend
                    text_in_current_row = text_in_current_row + spaces + text_to_add

                # else, calculate spaces to prepend from previous textline
                else:
                    num_of_spaces_to_be_prepend = math.floor(
                        (current_textline.region.x1 - 0) / prev_text_width) - len(text_in_current_row)
                    spaces = " " * num_of_spaces_to_be_prepend
                    text_in_current_row = text_in_current_row + spaces + text_to_add

                # if it is the last textline or next textline is a new line, push current row to textlines_in_rows
                if len(textlines_within_area) == 0 or not textlines_within_area[0].region.is_in_same_line(current_textline.region):
                    num_of_spaces_to_be_append = math.floor((xml_page.region.x2 - 0) / prev_text_width) - \
                        len(text_in_current_row)
                    spaces = " " * num_of_spaces_to_be_append
                    text_in_current_row = text_in_current_row + spaces
                    textlines_in_rows.append(text_in_current_row)
                    text_in_current_row = ""

                # append empty textlines in the end
                if len(textlines_within_area) == 0:
                    num_of_empty_lines_to_be_append = math.floor(
                        (current_textline.region.y1 - xml_page.region.y1) / xml_page.median_text_height)
                    for i in range(num_of_empty_lines_to_be_append):
                        textlines_in_rows.append("")

                previous_textline = current_textline

            textlines_in_all_pages = textlines_in_all_pages + textlines_in_rows

        if len(textlines_in_all_pages) == 0:
            textlines_in_all_pages = [""]

        return textlines_in_all_pages

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
