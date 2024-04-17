from .xml_helpers import XMLPage
from decimal import Decimal
import math
import re

from parsers.models.rule import Rule
from parsers.models.rule_type import RuleType

from parsers.helpers.get_document_nos_from_range import get_document_nos_from_range
from parsers.helpers.rule_extractor import RuleExtractor
from parsers.helpers.stream_processor import StreamProcessor


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
    
    def extract(self, rule, parsed_result=[]):
        if rule.rule_type == RuleType.DEPENDENT_RULE.value:
            page_nums = list(range(1, self.document.total_page_num + 1))
        else:
            page_nums = get_document_nos_from_range(
                rule.pages[:], 1, self.document.total_page_num)

        if self.document.document_pages.filter(ocred=False, page_num__in=page_nums).count() > 0:
            return {
                    "type": "TEXTFIELD",
                    "value": ["Please wait until the document finishes OCR"]
                }

        for page_num in page_nums:
            xml_page_already_exists = sum(
                1 for x in self.xml_pages if x.page_num == page_num) > 0
            if not xml_page_already_exists:
                xml_page = XMLPage(self, page_num)
                self.xml_pages.append(xml_page)
        self.xml_pages.sort(key=lambda x: x.page_num)

        if rule.rule_type == RuleType.TEXTFIELD.value:

            extracted = self.extract_textfield(
                rule, self.xml_pages, parsed_result)

        elif rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value:

            extracted = self.extract_anchored_textfield(
                rule, self.xml_pages, parsed_result)

        elif rule.rule_type == RuleType.TABLE.value:

            extracted = self.extract_table(
                rule, self.xml_pages, parsed_result)

        elif rule.rule_type == RuleType.BARCODE.value:

            extracted = self.extract_barcode(
                rule, self.xml_pages, parsed_result)

        elif rule.rule_type == RuleType.ACROBAT_FORM.value:

            extracted = self.extract_acrobat_form(
                rule, self.xml_pages, parsed_result)

        elif rule.rule_type == RuleType.INPUT_TEXTFIELD.value:

            return ""

        elif rule.rule_type == RuleType.INPUT_DROPDOWN.value:

            return ""
        
        elif rule.rule_type == RuleType.DEPENDENT_RULE.value:

            extracted = self.extract_dependent_rule(
                rule, self.xml_pages, parsed_result
            )

        return extracted

    def extract_and_stream(self, rule, parsed_result=[], with_processed_stream=False):
        extracted = self.extract(rule, parsed_result=parsed_result)

        stream_processor = StreamProcessor(rule)
        processed_streams = stream_processor.process(extracted)
        
        result = {
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "type": rule.rule_type
            },
            "extracted": extracted,
            "streamed": processed_streams[-1]["data"]
        }

        if with_processed_stream:
            result["processed_streams"] = processed_streams

        #parsed_result.append(result)

        return result
    
    def extract_dependent_rule(self, rule, xml_pages, parsed_result=[]):

        depends_on_rule_exists_in_parsed_result = False
        for single_parsed_result in parsed_result:
            if single_parsed_result["rule"]["id"] == rule.depends_on.id:
                result = single_parsed_result
                streamed = result["streamed"]
                depends_on_rule_exists_in_parsed_result = True
                break

        if not depends_on_rule_exists_in_parsed_result:
            depends_on_rule = Rule.objects.get(pk=rule.depends_on.id)
            result = self.extract_and_stream(depends_on_rule, parsed_result)
            streamed = result["streamed"]

        return streamed

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
