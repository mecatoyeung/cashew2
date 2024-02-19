from hmac import compare_digest
import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
from decimal import Decimal
import statistics
import os
import cv2
from pyzbar.pyzbar import decode

from backend.settings import MEDIA_ROOT, MEDIA_URL

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSLiteral, PSKeyword
from pdfminer.utils import decode_text

from parsers.models.rule_type import RuleType
from parsers.models.pre_processing import PreProcessing

from parsers.helpers.xml_helpers import XMLPage, XMLRegion, XMLRule, XMLTextLine, XMLText
from parsers.helpers.is_chinese import is_chinese
from parsers.helpers.get_document_nos_from_range import get_document_nos_from_range
from parsers.helpers.check_chinese_characters import check_chinese_characters
from parsers.helpers.calculate_separator_regions import calculate_separator_regions

from django.conf import settings

SAME_LINE_ACCEPTANCE_RANGE = Decimal(0.0)
ASSUMED_TEXT_WIDTH = Decimal(0.5)
ASSUMED_TEXT_HEIGHT = Decimal(1.0)


class RuleExtractor:

    def __init__(self, parser, rule, document, xml_pages):
        self.parser = parser
        self.rule = rule
        self.document = document
        self.xml_pages = xml_pages
        self.page_nums = get_document_nos_from_range(
            self.rule.pages, last=str(document.total_page_num))

    def extract(self, xml_pages, parsed_result=[]):

        if self.rule.rule_type == RuleType.TEXTFIELD.value:

            result = self.extract_textfield(xml_pages, parsed_result=[])

        elif self.rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value:

            result = self.extract_anchored_textfield(
                xml_pages, parsed_result=[])

        elif self.rule.rule_type == RuleType.TABLE.value:

            result = self.extract_table(xml_pages, parsed_result=[])

        elif self.rule.rule_type == RuleType.ACROBAT_FORM.value:

            result = self.extract_acrobat_form(xml_pages, parsed_result=[])

        elif self.rule.rule_type == RuleType.INPUT_TEXTFIELD.value:

            return ""

        elif self.rule.rule_type == RuleType.INPUT_DROPDOWN.value:

            return ""

        return result

    def extract_textfield(self, parsed_result=[]):

        xml_pages = self.xml_pages

        page_nums = get_document_nos_from_range(
            self.rule.pages, 1, self.document.total_page_num)

        textlines_in_all_pages = []

        for page_num in page_nums:

            xml_page = [x for x in xml_pages if x.page_num == page_num][0]

            xml_rule = XMLRule(xml_page, self.rule)

            # Get All Textlines within Area
            textlines_within_area = []
            for textline in xml_page.textlines:
                # Tailored for Google Invoices
                if re.match(r'[.]+', textline.text):
                    continue

                if xml_rule.region.overlaps(textline.region) and textline.text != "":
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
                    (xml_rule.region.y2 - textlines_in_rows[0][0].region.y2) / xml_page.median_of_text_heights)
                for i in range(num_of_empty_lines_to_be_prepend):
                    num_of_spaces_to_be_prepend = math.floor(
                        (xml_rule.region.x2 - xml_rule.region.x1) / xml_page.median_of_text_widths)
                    spaces = " " * num_of_spaces_to_be_prepend
                    text_in_rows.append(spaces)

            previous_textline = None
            for textlines_in_row in textlines_in_rows:

                """text_widths = []
                text_heights = []
                for textline in textlines_in_row:
                    for text in textline.text_elements:
                        text_width = text.region.x2 - text.region.x1
                        text_height = text.region.y2 - text.region.y1
                        text_widths.append(text_width)
                        text_heights.append(text_height)

                median_of_text_widths = statistics.median(text_widths)
                median_of_text_heights = statistics.median(text_heights)"""

                median_of_text_widths = xml_page.median_of_text_widths
                median_of_text_heights = xml_page.median_of_text_heights

                text_in_current_row = ""
                for current_textline_index in range(0, len(textlines_in_row)):
                    current_textline = textlines_in_row[current_textline_index]

                    if current_textline_index == 0:
                        # if current textline is the first line in the row,
                        # add empty lines before
                        if previous_textline != None:
                            num_of_empty_lines_to_be_prepend = math.floor(
                                (previous_textline.region.y1 - current_textline.region.y2) / median_of_text_heights)
                            for i in range(num_of_empty_lines_to_be_prepend):
                                num_of_spaces_to_be_prepend = math.floor(
                                    (xml_rule.region.x2 - xml_rule.region.x1) / median_of_text_widths)
                                spaces = " " * num_of_spaces_to_be_prepend
                                text_in_rows.append(spaces)
                        # if current textline is the first line in the row,
                        # add spaces before
                        num_of_spaces_to_be_prepend = math.floor(
                            (current_textline.region.x1 - xml_rule.region.x1) / median_of_text_widths)
                        spaces = " " * num_of_spaces_to_be_prepend
                        text_in_current_row = spaces + current_textline.text
                    # if current textline has previous line,
                    # add spaces before
                    else:
                        num_of_spaces_to_be_prepend = math.floor(
                            (current_textline.region.x1 - xml_rule.region.x1) / median_of_text_widths) - len(text_in_current_row)
                        spaces = " " * num_of_spaces_to_be_prepend
                        text_in_current_row = text_in_current_row + spaces + current_textline.text

                    # add spaces if textline is the last
                    if current_textline_index == (len(textlines_in_row) - 1):
                        num_of_spaces_to_be_prepend = math.floor(
                            (xml_rule.region.x2 - xml_rule.region.x1) / median_of_text_widths) - len(text_in_current_row)
                        spaces = " " * num_of_spaces_to_be_prepend
                        text_in_current_row = text_in_current_row + spaces

                    previous_textline = current_textline

                text_in_rows.append(text_in_current_row)

            # append empty textlines in the end
            if len(textlines_in_rows) > 0:
                last_textline = textlines_in_rows[-1][-1]
                if len(textlines_within_area) == 0:
                    num_of_empty_lines_to_be_append = math.floor(
                        (last_textline.region.y1 - xml_rule.region.y1) / xml_page.median_of_text_heights)
                    for i in range(num_of_empty_lines_to_be_append):
                        text_in_rows.append("")

            textlines_in_all_pages = textlines_in_all_pages + text_in_rows

        if len(textlines_in_all_pages) == 0:
            textlines_in_all_pages = [""]

        return textlines_in_all_pages

    def get_anchor_relative_region(self, parsed_result=[]):

        xml_pages = self.xml_pages

        xml_page = [x for x in xml_pages if x.page_num ==
                    self.rule.anchor_page_num][0]

        anchor_region = XMLRegion()

        anchor_region.x1 = Decimal(
            self.rule.anchor_x1)
        anchor_region.x2 = Decimal(
            self.rule.anchor_x2)
        anchor_region.y1 = Decimal(
            self.rule.anchor_y1)
        anchor_region.y2 = Decimal(
            self.rule.anchor_y2)

        result = XMLRegion()

        for textline in xml_page.textlines:

            if self.rule.anchor_text in textline.text:
                start_pos = textline.text.find(self.rule.anchor_text)

                result.x1 = self.rule.x1 - \
                    textline.text_elements[start_pos].region.x1
                result.y1 = self.rule.y1 - \
                    textline.text_elements[start_pos].region.y1
                result.x2 = self.rule.x2 - \
                    textline.text_elements[start_pos].region.x2
                result.y2 = self.rule.y2 - \
                    textline.text_elements[start_pos].region.y2

                return result

        result.x1 = self.rule.anchor_x1
        result.y1 = self.rule.anchor_y1
        result.x2 = self.rule.anchor_x2
        result.y2 = self.rule.anchor_y2

        return result

    def extract_anchored_textfield(self, parsed_result=[]):

        xml_pages = self.xml_pages

        xml_page = [x for x in xml_pages if x.page_num ==
                    self.rule.anchor_page_num][0]

        anchor_region = XMLRegion()
        anchor_region.x1 = self.rule.anchor_x1
        anchor_region.x2 = self.rule.anchor_x2
        anchor_region.y1 = self.rule.anchor_y1
        anchor_region.y2 = self.rule.anchor_y2

        result = [""]

        for textline in xml_page.textlines:

            if self.rule.anchor_text in textline.text and anchor_region.overlaps(textline.region):
                start_pos = textline.text.find(self.rule.anchor_text)
                textline.text_elements[start_pos]

                anchored_textline_region = XMLRegion()

                anchored_textline_region.x1 = textline.text_elements[
                    start_pos].region.x1 + self.rule.anchor_relative_x1
                anchored_textline_region.y1 = textline.text_elements[
                    start_pos].region.y1 + self.rule.anchor_relative_y1
                anchored_textline_region.x2 = textline.text_elements[
                    start_pos].region.x2 + self.rule.anchor_relative_x2
                anchored_textline_region.y2 = textline.text_elements[
                    start_pos].region.y2 + self.rule.anchor_relative_y2

                xml_rule = XMLRule(xml_page, self.rule)

                textlines_in_rows = []

                # Get All Textlines within Area
                textlines_within_area = []
                for textline in xml_page.textlines:
                    if anchored_textline_region.overlaps(textline.region) and textline.text != "":
                        textlines_within_area.append(textline)

                text_in_current_row = ""
                prev_text_width = xml_page.median_text_width
                first_textline_in_row = None
                while len(textlines_within_area) > 0:
                    current_textline = textlines_within_area.pop(0)

                    text_to_add = ""
                    for text_in_textline in current_textline.text_elements:
                        if anchored_textline_region.overlaps(text_in_textline.region):
                            text_to_add = text_to_add + text_in_textline.text
                            if check_chinese_characters(text_in_textline.text):
                                prev_text_width = text_in_textline.region.x2 - text_in_textline.region.x1

                    # if it is a new line, just prepend space append to the row array
                    if len(text_in_current_row) == 0:
                        first_textline_in_row = current_textline
                        # if it is the first line, add empty lines
                        if len(textlines_in_rows) == 0:
                            num_of_empty_lines_to_be_prepend = math.floor(
                                (anchored_textline_region.y2 - current_textline.region.y2) / xml_page.median_text_height)
                            for i in range(num_of_empty_lines_to_be_prepend):
                                textlines_in_rows.append("")
                        # if it is not the first line and there is a line difference between current line and previous line,
                        # add empty lines between them
                        else:
                            num_of_empty_lines_to_be_prepend = math.floor(
                                (previous_textline.region.y1 - current_textline.region.y2) / xml_page.median_text_height)
                            for i in range(num_of_empty_lines_to_be_prepend):
                                textlines_in_rows.append("")

                        num_of_spaces_to_be_prepend = math.floor(
                            (current_textline.region.x1 - anchored_textline_region.x1) / prev_text_width)
                        spaces = " " * num_of_spaces_to_be_prepend
                        text_in_current_row = text_in_current_row + spaces + text_to_add

                    # else, calculate spaces to prepend from previous textline
                    else:
                        num_of_spaces_to_be_prepend = math.floor(
                            (current_textline.region.x1 - anchored_textline_region.x1) / prev_text_width) - len(text_in_current_row)
                        spaces = " " * num_of_spaces_to_be_prepend
                        text_in_current_row = text_in_current_row + spaces + text_to_add

                    # if it is the last textline or next textline is a new line, push current row to textlines_in_rows
                    if len(textlines_within_area) == 0 or not textlines_within_area[0].region.is_in_same_line(current_textline.region):
                        num_of_spaces_to_be_append = math.floor((xml_page.region.x2 - anchored_textline_region.x1) / prev_text_width) - \
                            len(text_in_current_row)
                        spaces = " " * num_of_spaces_to_be_append
                        text_in_current_row = text_in_current_row + spaces
                        textlines_in_rows.append(text_in_current_row)
                        text_in_current_row = ""

                    # append empty textlines in the end
                    if len(textlines_within_area) == 0:
                        num_of_empty_lines_to_be_append = math.floor(
                            (current_textline.region.y1 - anchored_textline_region.y1) / xml_page.median_text_height)
                        for i in range(num_of_empty_lines_to_be_append):
                            textlines_in_rows.append("")

                    previous_textline = current_textline

                result = textlines_in_rows

        return result

    def extract_acrobat_form(self, parsed_result=[]):

        def decode_value(value):

            # decode PSLiteral, PSKeyword
            if isinstance(value, (PSLiteral, PSKeyword)):
                value = value.name

            # decode bytes
            if isinstance(value, bytes):
                value = decode_text(value)

            return value

        pdf_path = os.path.join(settings.MEDIA_ROOT, 'documents', self.document.guid,
                                "source_file.pdf")

        data = []

        with open(pdf_path, 'rb') as fp:
            parser = PDFParser(fp)

            doc = PDFDocument(parser)
            res = resolve1(doc.catalog)

            if 'AcroForm' not in res:
                raise ValueError("No AcroForm Found")

            fields = resolve1(doc.catalog['AcroForm'])[
                'Fields']  # may need further resolving

            for f in fields:
                field = resolve1(f)
                name, values = field.get('T'), field.get('V')

                # decode name
                name = decode_text(name)

                # resolve indirect obj
                values = resolve1(values)

                # decode value(s)
                if isinstance(values, list):
                    values = [decode_value(v) for v in values]
                else:
                    values = decode_value(values)

                if values == None:
                    values = ""

                data.append(name + ": " + values)

        return data

    def extract_table(self, parsed_result=[]):

        xml_pages = self.xml_pages

        page_nums = get_document_nos_from_range(
            self.rule.pages, 1, self.document.total_page_num)

        textlines_organized_in_columns = []

        for page_num in page_nums:

            xml_page = [x for x in xml_pages if x.page_num == page_num][0]

            separator_regions = calculate_separator_regions(
                xml_page, self.rule)

            xml_rule = XMLRule(xml_page, self.rule)

            # Calculate median of text width and height
            text_widths = []
            text_heights = []
            for textline in xml_page.textlines:
                for text in textline.text_elements:
                    text_width = text.region.x2 - text.region.x1
                    text_height = text.region.y2 - text.region.y1
                    text_widths.append(text_width)
                    text_heights.append(text_height)

            for separator_region in separator_regions:
                textlines_within_area = []
                for textline in xml_page.textlines:
                    if separator_region.overlaps(textline.region) and textline.text != "":
                        num_of_text_overlaps = 0
                        # Create textline to add instead of using original textline
                        # This is to avoid duplicate text when textlines partially overlaps the area
                        num_of_text_overlaps = 0
                        overlap_start_index = 0
                        overlap_end_index = 0
                        for text_index in range(len(textline.text_elements)):
                            text = textline.text_elements[text_index]
                            if separator_region.overlaps(text.region) and num_of_text_overlaps == 0:
                                overlap_start_index = text_index
                                overlap_end_index = text_index + 1
                            elif separator_region.overlaps(text.region) and num_of_text_overlaps > 0:
                                overlap_end_index = text_index + 1
                            num_of_text_overlaps += 1

                        overlap_text_elements = textline.text_elements[
                            overlap_start_index:overlap_end_index]
                        if (len(overlap_text_elements) > 0):
                            new_textline = XMLTextLine(xml_page)
                            new_textline.region.x1 = Decimal(
                                overlap_text_elements[0].region.x1)
                            new_textline.region.y1 = Decimal(
                                overlap_text_elements[0].region.y1)
                            new_textline.region.x2 = Decimal(
                                overlap_text_elements[-1].region.x2)
                            new_textline.region.y2 = Decimal(
                                overlap_text_elements[-1].region.y2)
                            new_textline.text = textline.text[overlap_start_index:overlap_end_index]
                            new_textline.text_elements = textline.text_elements[
                                overlap_start_index:overlap_end_index]

                            # Remove overlap text from original textline
                            textline.text = textline.text[overlap_end_index:]
                            textline.text_elements = textline.text_elements[overlap_end_index:]

                            textlines_within_area.append(new_textline)

                textlines_organized_in_columns.append(textlines_within_area)

        median_of_text_widths = statistics.median(text_widths)
        # median_of_text_widths = ASSUMED_TEXT_WIDTH
        median_of_text_heights = statistics.median(text_heights)
        #median_of_text_heights = ASSUMED_TEXT_HEIGHT

        textlines_organized_in_rows = []
        toppest_textline = None
        toppest_textline_index = -1
        textlines_in_row = []
        for i in textlines_organized_in_columns:
            textlines_in_row.append([])
        ranges_of_textlines_in_the_row = []
        while (sum(len(textlines_organized_in_column) for textlines_organized_in_column in textlines_organized_in_columns)):
            # Find toppest textline
            if toppest_textline == None:
                for textlines_in_column_index in range(len(textlines_organized_in_columns)):
                    textlines_in_column = textlines_organized_in_columns[textlines_in_column_index]
                    if len(textlines_in_column) > 0:
                        toppest_textline = textlines_in_column[0]
                        toppest_textline_index = textlines_in_column_index
                        break
                for textlines_in_column_index in range(len(textlines_organized_in_columns)):
                    textlines_in_column = textlines_organized_in_columns[textlines_in_column_index]
                    if len(textlines_in_column) == 0:
                        continue
                    if toppest_textline == textlines_in_column[0]:
                        continue
                    if textlines_in_column[0].region.y2 > toppest_textline.region.y2:
                        toppest_textline = textlines_in_column[0]
                        toppest_textline_index = textlines_in_column_index
                textlines_organized_in_columns[toppest_textline_index].pop(0)
                textlines_in_row[toppest_textline_index].append(
                    toppest_textline)

                ranges_of_textlines_in_the_row.append(
                    {"x1": toppest_textline.region.x1, "x2": toppest_textline.region.x2})

                continue

            # Find textlines that are in the same row of toppest textline
            textline_indexes_to_be_popped = []
            for textlines_in_column_index in range(len(textlines_organized_in_columns)):
                textlines_in_column = textlines_organized_in_columns[textlines_in_column_index]
                for textline_in_column_index in range(len(textlines_in_column)):
                    textline_in_column = textlines_in_column[textline_in_column_index]

                    is_textline_under_existing_textlines_in_row = False
                    for range_of_textlines_in_the_row in ranges_of_textlines_in_the_row:
                        if textline_in_column.region.x1 > range_of_textlines_in_the_row["x1"] and textline_in_column.region.x1 < range_of_textlines_in_the_row["x2"]:
                            is_textline_under_existing_textlines_in_row = True
                        if textline_in_column.region.x2 < range_of_textlines_in_the_row["x2"] and textline_in_column.region.x2 > range_of_textlines_in_the_row["x1"]:
                            is_textline_under_existing_textlines_in_row = True

                    if toppest_textline.region.is_in_same_line(textline_in_column.region) and \
                            not is_textline_under_existing_textlines_in_row:
                        textline_indexes_to_be_popped.append(
                            textlines_in_column_index)
                        textlines_in_row[textlines_in_column_index].append(
                            textline_in_column)
                        ranges_of_textlines_in_the_row.append(
                            {"x1": textline_in_column.region.x1, "x2": textline_in_column.region.x2})

            for textline_index_to_be_popped in textline_indexes_to_be_popped:
                textlines_organized_in_columns[textline_index_to_be_popped].pop(
                    0)

            # Add textlines_in_row to textlines_organized_in_rows
            textlines_organized_in_rows.append(textlines_in_row)

            # Reset toppest textline and loop again
            toppest_textline = None
            toppest_textline_index = -1
            textlines_in_row = []
            for i in textlines_organized_in_columns:
                textlines_in_row.append([])
            ranges_of_textlines_in_the_row = []

        # Convert to JSON
        previous_textline = None
        text_in_rows = []
        for textlines_organized_in_row_index in range(len(textlines_organized_in_rows)):
            textlines_organized_in_row = textlines_organized_in_rows[textlines_organized_in_row_index]
            text_in_current_row = []
            for column_index in range(len(textlines_organized_in_row)):
                text_in_column = ""
                textlines_in_column = textlines_organized_in_row[column_index]
                # if there is no textlines in the column, add white spaces
                if len(textlines_in_column) == 0:
                    x_difference = separator_regions[column_index].x2 - \
                        separator_regions[column_index].x1
                    number_of_spaces_to_be_added_before = math.floor(
                        x_difference / median_of_text_widths)
                    text_in_column = text_in_column + \
                        (" " * number_of_spaces_to_be_added_before)
                if not previous_textline == None and is_chinese(previous_textline.text[-1]):
                    space_char = "　"
                else:
                    space_char = " "
                for textline_index in range(len(textlines_in_column)):
                    textline = textlines_in_column[textline_index]
                    # Add empty rows before data
                    if len(text_in_rows) == 0:
                        y_difference = xml_rule.region.y2 - textline.region.y2
                        number_of_empty_lines_to_be_added = math.floor(
                            y_difference / median_of_text_heights)
                        for empty_line_index in range(number_of_empty_lines_to_be_added):
                            empty_line = []
                            for empty_line_column_index in range(len(textlines_organized_in_row)):
                                x_difference = separator_regions[empty_line_column_index].x2 - \
                                    separator_regions[empty_line_column_index].x1
                                number_of_spaces_in_empty_line_column = math.floor(
                                    x_difference / median_of_text_widths)
                                empty_line.append(
                                    space_char * number_of_spaces_in_empty_line_column)
                            text_in_rows.append(empty_line)
                    # if it is the first textline in the first column, add white spaces before the text
                    if textline_index == 0:
                        x_difference = textline.region.x1 - \
                            separator_regions[column_index].x1
                        number_of_spaces_to_be_added_before = math.floor(
                            x_difference / median_of_text_widths)
                        text_in_column = text_in_column + \
                            (space_char * number_of_spaces_to_be_added_before)
                        # add the text after adding spaces
                        text_in_column = text_in_column + textline.text
                    # if it is the second or further textline in the column, add white spaces before the text
                    elif textline_index > 0:
                        previous_textline = textlines_in_column[textline_index - 1]
                        # x_difference = textline.region.x1 - previous_textline.region.x2
                        # number_of_spaces_to_be_added_before = math.floor(
                        #    x_difference / median_of_text_widths)
                        number_of_spaces_to_be_added_before = math.floor(
                            textline.region.x1 / median_of_text_widths) - len(text_in_column)
                        text_in_column = text_in_column + \
                            (space_char * number_of_spaces_to_be_added_before)
                        # add the text after adding spaces
                        text_in_column = text_in_column + textline.text
                    # if it is the last textline in the column, add shite spaces after the text
                    if textline_index == (len(textlines_in_column) - 1):
                        x_difference = separator_regions[column_index].x2 - \
                            textline.region.x2
                        number_of_spaces_to_be_added_after = math.floor(
                            x_difference / median_of_text_widths)
                        text_in_column = text_in_column + \
                            (space_char * number_of_spaces_to_be_added_after)

                    previous_textline = textline

                text_in_current_row.append(text_in_column)
            text_in_rows.append(text_in_current_row)

        # Add empty rows after data
        if 'textline' in locals() and textline.region.y1 != None:
            y_difference = textline.region.y1 - xml_rule.region.y1
            number_of_empty_lines_to_be_added = math.floor(
                y_difference / median_of_text_heights)
            for empty_line_index in range(number_of_empty_lines_to_be_added):
                empty_line = []
                for empty_line_column_index in range(len(textlines_organized_in_row)):
                    x_difference = separator_regions[empty_line_column_index].x2 - \
                        separator_regions[empty_line_column_index].x1
                    number_of_spaces_in_empty_line_column = math.floor(
                        x_difference / median_of_text_widths)
                    empty_line.append(
                        " " * number_of_spaces_in_empty_line_column)
                text_in_rows.append(empty_line)

        header = []
        for header_index in range(len(separator_regions)):
            header.append(header_index + 1)

        if len(text_in_rows) == 0:
            text_in_rows = [[""]]

        response = {
            "header": header,
            "body": text_in_rows
        }

        return response

    def extract_barcode(self, parsed_result=[]):

        xml_pages = self.xml_pages

        preprocessings = PreProcessing.objects.filter(
            parser_id=self.parser.id).all()
        page_num = get_document_nos_from_range(
            self.rule.pages, 1, self.document.total_page_num)[0]

        xml_page = [x for x in xml_pages if x.page_num == page_num][0]
        # xml_page = xml_pages[page_num-1]

        xml_rule = XMLRule(xml_page, self.rule)

        if len(preprocessings) > 0:
            last_preprocessing = preprocessings[len(preprocessings)-1]
            last_preprocessing_id = last_preprocessing.id
            png_path = os.path.join(
                'documents', self.document.guid, "pre_processed-" + str(last_preprocessing_id), str(page_num) + ".jpg")
        else:
            png_path = os.path.join(
                'documents', self.document.guid, str(page_num) + ".jpg")
        full_png_path = os.path.join(MEDIA_ROOT, png_path)

        im = cv2.imread(full_png_path)
        h, w, c = im.shape
        ret, bw_im = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)

        crop_x1 = int(xml_rule.region.x1 / xml_page.region.x2
                      * w)
        crop_x2 = int(xml_rule.region.x2 / xml_page.region.x2
                      * w)
        crop_y1 = int((xml_page.region.y2 - xml_rule.region.y2) /
                      xml_page.region.y2 * h)
        crop_y2 = int((xml_page.region.y2 - xml_rule.region.y1) /
                      xml_page.region.y2 * h)
        cropped_im = bw_im[crop_y1:crop_y2, crop_x1:crop_x2]

        detectedBarcodes = [decoded.data.decode('utf-8')
                            for decoded in decode(cropped_im)]

        if len(detectedBarcodes) == 0:
            return [""]

        return detectedBarcodes
