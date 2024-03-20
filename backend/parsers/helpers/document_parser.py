from .xml_helpers import XMLPage
from decimal import Decimal
import math
import re

from parsers.models.rule import Rule
from parsers.models.rule_type import RuleType

from parsers.helpers.get_document_nos_from_range import get_document_nos_from_range
from parsers.helpers.rule_extractor import RuleExtractor

#SAME_LINE_ACCEPTANCE_RANGE = Decimal(0.0)
#ASSUMED_TEXT_WIDTH = Decimal(0.5)
#ASSUMED_TEXT_HEIGHT = Decimal(1.0)


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

        if self.document.document_pages.filter(ocred=False, page_num__in=page_nums).count() > 0:
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
