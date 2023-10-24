from .xml_helpers import XMLPage, XMLRegion, XMLRule, XMLTextLine, XMLText
from hmac import compare_digest
import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
import statistics
from decimal import Decimal
import statistics

from ..models.rule_type import RuleType
from .get_document_nos_from_range import get_document_nos_from_range
from .check_chinese_characters import check_chinese_characters
from .calculate_separator_regions import calculate_separator_regions
from .rule_extractor import RuleExtractor

SAME_LINE_ACCEPTANCE_RANGE = Decimal(0.0)
ASSUMED_TEXT_WIDTH = Decimal(5.0)
ASSUMED_TEXT_HEIGHT = Decimal(10.0)


class DocumentParser:

    def __init__(self, parser, document):
        self.parser = parser
        self.document = document
        self.xml_pages = []
        self.parsed_result = []

    def extract(self, rule):

        # Add to xml page if not yet initialized
        page_nums = get_document_nos_from_range(
            rule.pages, 1, self.document.total_page_num)
        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in self.xml_pages if xml_page.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, self.document, page_num)
                self.xml_pages.append(xml_page)
        self.xml_pages.sort(key=lambda x: x.page_num)

        if rule.rule_type == RuleType.TEXTFIELD.value:

            result = self.extract_textfield(rule, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value:

            result = self.extract_anchored_textfield(rule, self.parsed_result)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.TABLE.value:

            result = self.extract_table(rule)
            self.parsed_result.append(result)

        elif rule.rule_type == RuleType.INPUT_TEXTFIELD.value:

            return ""

        elif rule.rule_type == RuleType.INPUT_DROPDOWN.value:

            return ""

        return result

    def extract_textfield(self, rule, parsed_result=[]):

        rule_extractor = RuleExtractor(rule, self.document)

        return rule_extractor.extract_textfield(self.xml_pages, parsed_result=parsed_result)

    def extract_table(self, rule, parsed_result=[]):

        rule_extractor = RuleExtractor(
            rule, self.document, parsed_result=parsed_result)

        return rule_extractor.extract_table(self.xml_pages)
