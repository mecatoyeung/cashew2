from hmac import compare_digest
import xml.etree.ElementTree as ET
import re
import functools
import math
import copy
import json
from decimal import Decimal


from .xml_container import XMLContainer
from .get_document_nos_from_range import get_document_nos_from_range
from ..models.rule_type import RuleType
from ..serializers.document import DocumentDetailSerializer


class RuleExtractor:

    def __init__(self, rule, document, xml_container=None):
        self.rule = rule
        self.document = document
        self.page_nums = get_document_nos_from_range(self.rule.pages, last=str(document.total_page_num))

        if xml_container == None:
            self.xml_container = XMLContainer(self.document)
        else:
            self.xml_container = xml_container

    """def get_page(self, page_num):
        for page in self.pages:
            if page.page_num == page_num:
                return page
        raise Exception("Page(page no=" + page_num + ") not found.")"""

    def extract(self):
        if self.rule.rule_type == RuleType.TEXTFIELD.value:

            result = self.extract_textfield()

        elif self.rule.rule_type == RuleType.ANCHORED_TEXTFIELD.value:

            result = self.extract_anchored_textfield()

        elif self.rule.rule_type == RuleType.TABLE.value:

            result = self.extract_table()

        elif self.rule.rule_type == RuleType.INPUT_TEXTFIELD.value:

            return ""

        elif self.rule.rule_type == RuleType.INPUT_DROPDOWN.value:

            return ""

        return result

    def extract_textfield(self):

        return self.xml_container.extract(self.rule)

    """def extract_anchor(self):

        page = self.pages[0]

        anchor_region_in_abs_pos = Region()

        anchor_region_in_abs_pos.x1 = Decimal(self.rule.anchor_x_1) / 100 * page.region.x2
        anchor_region_in_abs_pos.x2 = Decimal(self.rule.anchor_x_2) / 100 * page.region.x2
        anchor_region_in_abs_pos.y1 = Decimal(self.rule.anchor_y_1) / 100 * page.region.y2
        anchor_region_in_abs_pos.y2 = Decimal(self.rule.anchor_y_2) / 100 * page.region.y2

        result = Region()

        document_serializer = DocumentDetailSerializer(self.document)
        xml = document_serializer.data['documentPages'][page.page_no-1]['xml']

        root = ET.fromstring(xml)
        textline_els = root.findall('.//textline')

        textlines = []

        for textline_el in textline_els:
            textline_bbox_str = textline_el.attrib['bbox']
            textline_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                textline_bbox_str,
                                                re.IGNORECASE
                                                )

            textline = TextLine(page)

            textline.region.x1 = Decimal(textline_bbox_search.group(1))
            textline.region.y1 = Decimal(textline_bbox_search.group(2))
            textline.region.x2 = Decimal(textline_bbox_search.group(3))
            textline.region.y2 = Decimal(textline_bbox_search.group(4))
            textline.textline_el = textline_el

            textlines.append(textline)

            for textline in textlines:
                result_text = ""
                for text_el in textline.textline_el:
                    if text_el.text != '\n' and 'bbox' in text_el.attrib:
                        text = Text()
                        text_bbox_str = text_el.attrib['bbox']
                        text_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                        text_bbox_str,
                                                        re.IGNORECASE
                                                        )
                        text.region.x1 = Decimal(text_bbox_search.group(1))
                        text.region.y1 = Decimal(text_bbox_search.group(2))
                        text.region.x2 = Decimal(text_bbox_search.group(3))
                        text.region.y2 = Decimal(text_bbox_search.group(4))
                        text.text = text_el.text

                        textline.text_elements.append(text)

                        if anchor_region_in_abs_pos.contains(text.region):
                            result_text = result_text + text.text

                textline.text = result_text

                if self.rule.anchor_text in textline.text:
                    start_pos = textline.text.find(self.rule.anchor_text)
                    textline.text_elements[start_pos]

                    result.x1 = textline.text_elements[start_pos].region.x1 / page.region.x2 * 100
                    result.x2 = textline.text_elements[start_pos].region.x1 / page.region.x2 * 100
                    result.y1 = textline.text_elements[start_pos].region.y1 / page.region.y2 * 100
                    result.y2 = textline.text_elements[start_pos].region.y1 / page.region.y2 * 100

                    return result

        result.x1 = self.rule.anchor_x_1
        result.x2 = self.rule.anchor_x_2
        result.y1 = self.rule.anchor_y_1
        result.y2 = self.rule.anchor_y_2

        return result

    def extract_anchored_textfield(self):

        page = self.pages[0]

        anchor_region = Region()
        anchor_region.x1 = self.rule.anchor_x_1
        anchor_region.y1 = self.rule.anchor_y_1
        anchor_region.x2 = self.rule.anchor_x_2
        anchor_region.y2 = self.rule.anchor_y_2

        anchor = self.extract_anchor()

        anchored_textfield_region = Region()

        result = []

        document_serializer = DocumentGetWithXMLSerializer(self.document)
        xml = document_serializer.data['documentPages'][page.page_no-1]['xml']

        root = ET.fromstring(xml)
        textline_els = root.findall('.//textline')

        textlines = []

        for textline_el in textline_els:
            textline_bbox_str = textline_el.attrib['bbox']
            textline_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                textline_bbox_str,
                                                re.IGNORECASE
                                                )

            textline = TextLine(page)

            textline.region.x1 = Decimal(textline_bbox_search.group(1))
            textline.region.y1 = Decimal(textline_bbox_search.group(2))
            textline.region.x2 = Decimal(textline_bbox_search.group(3))
            textline.region.y2 = Decimal(textline_bbox_search.group(4))
            textline.textline_el = textline_el

            textlines.append(textline)

        for textline in textlines:
            result_text = ""
            for text_el in textline.textline_el:
                if text_el.text != '\n' and 'bbox' in text_el.attrib:
                    text = Text()
                    text_bbox_str = text_el.attrib['bbox']
                    text_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                    text_bbox_str,
                                                    re.IGNORECASE
                                                    )
                    text.region.x1 = Decimal(text_bbox_search.group(1))
                    text.region.y1 = Decimal(text_bbox_search.group(2))
                    text.region.x2 = Decimal(text_bbox_search.group(3))
                    text.region.y2 = Decimal(text_bbox_search.group(4))
                    text.text = text_el.text

                    textline.text_elements.append(text)

                    if anchored_textfield_region.contains(text.region):
                        result_text = result_text + text.text

            if result_text != "":
                result.append(result_text)

        return result

    def extract_table(self):

        text_x_size_of_current_textline = Decimal(3.80)

        result_body = []

        # calculate all table column postions
        table_column_xs_splitted_string = self.rule.table_column_xs.split(",")
        if (len(table_column_xs_splitted_string) > 0) and not table_column_xs_splitted_string[0] == "":
            table_column_xs = [Decimal(x) for x in table_column_xs_splitted_string]
            table_column_xs = list(
                filter(lambda x: x > self.rule.x_1, table_column_xs))
            table_column_xs = list(
                filter(lambda x: x < self.rule.x_2, table_column_xs))
        else:
            table_column_xs = []
        table_column_xs.insert(0, Decimal(self.rule.x_1))
        table_column_xs.append(Decimal(self.rule.x_2))

        for page in self.pages:
            # group all textlines into columns
            textlines_in_columns = []
            for xIndex in range(len(table_column_xs)-1):

                textlines_in_column = []

                area = RuleArea()
                area.region.x1 = Decimal(
                    table_column_xs[xIndex]) / Decimal(100.00) * page.region.x2
                area.region.y1 = Decimal(self.rule.region.y1)
                area.region.x2 = Decimal(
                    table_column_xs[xIndex+1]) / Decimal(100.00) * page.region.x2
                area.region.y2 = Decimal(self.rule.region.y2)

                for textline in page.textlines:

                    if area.region.overlaps(textline.region):
                        copied_textline = TextLine(textline.page)
                        copied_textline.region = copy.deepcopy(textline.region)
                        copied_textline.text = textline.text
                        copied_textline.text_elements = copy.deepcopy(textline.text_elements)
                        copied_textline.textline_el = copy.deepcopy(textline.textline_el)
                        result_text = ""
                        for text_el_index, text_el in enumerate(copied_textline.textline_el):
                            if text_el.text != '\n' and 'bbox' in text_el.attrib:
                                text = Text()
                                text_bbox_str = text_el.attrib['bbox']
                                text_bbox_search = re.search('([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3}),([-]*[0-9]{1,4}.[0-9]{3})',
                                                             text_bbox_str,
                                                             re.IGNORECASE
                                                             )
                                text.region.x1 = Decimal(
                                    text_bbox_search.group(1))
                                text.region.y1 = Decimal(
                                    text_bbox_search.group(2))
                                text.region.x2 = Decimal(
                                    text_bbox_search.group(3))
                                text.region.y2 = Decimal(
                                    text_bbox_search.group(4))
                                text.text = text_el.text
                                if (area.region.contains(text.region)):
                                    result_text = result_text + text.text
                                elif (area.region.overlaps(text.region)) and area.region.x2 < text.region.x2:
                                    result_text = result_text + text.text
                        copied_textline.text = result_text

                        textlines_in_column.append(copied_textline)

                textlines_in_columns.append(textlines_in_column)

            # group all textlines into rows
            textlines_in_rows = []
            while(True):
                textlines_in_row = []
                for xIndex in range(len(table_column_xs)-1):
                    textlines_in_row.append([])

                most_top_column = 0
                most_top_y2 = Decimal(0.00)
                most_top_textline = None

                # find out the toppest element
                for xIndex, textlines_in_column in enumerate(textlines_in_columns):
                    if len(textlines_in_columns[xIndex]) == 0:
                        continue

                    if textlines_in_columns[xIndex][0].region.y2 > most_top_y2:
                        most_top_textline = textlines_in_columns[xIndex][0]
                        most_top_column = xIndex
                        most_top_y2 = textlines_in_columns[xIndex][0].region.y2

                # add toppest element to textlines_in_row
                textlines_in_row[most_top_column] = [textlines_in_columns[most_top_column][0]]
                textlines_in_columns[most_top_column].pop(0)

                # exit loop if no more textlines
                total_num_of_cells = sum(len(t) for t in textlines_in_columns)
                if total_num_of_cells == 0:
                    textlines_in_rows.append(textlines_in_row)
                    break

                # append table row
                covered_xs_s = []
                delete_indexes = []
                for xIndex in range(len(textlines_in_columns)):
                    for yIndex in range(len(textlines_in_columns[xIndex])):
                        if most_top_textline.region.is_in_same_line(textlines_in_columns[xIndex][yIndex].region):
                            does_xs_overlap_with_prev_lines = False
                            for covered_xs in covered_xs_s:
                                if covered_xs[1] > textlines_in_columns[xIndex][yIndex].region.x1 and covered_xs[1] < textlines_in_columns[xIndex][yIndex].region.x2:
                                    does_xs_overlap_with_prev_lines = True
                                elif covered_xs[0] > textlines_in_columns[xIndex][yIndex].region.x1 and covered_xs[0] < textlines_in_columns[xIndex][yIndex].region.x2:
                                    does_xs_overlap_with_prev_lines = True
                            if does_xs_overlap_with_prev_lines:
                                continue
                            textlines_in_row[xIndex].append(textlines_in_columns[xIndex][yIndex])
                            covered_xs_s.append([textlines_in_columns[xIndex][yIndex].region.x1, textlines_in_columns[xIndex][yIndex].region.x2])
                            delete_indexes.append([xIndex, yIndex])

                delete_indexes.reverse()
                for delete_index in delete_indexes:
                    textlines_in_columns[delete_index[0]].pop(delete_index[1])

                # sort textlines in cell
                def region_x1(el):
                    return el.region.x1
                for xIndex in range(len(textlines_in_row)):
                    textlines_in_row[xIndex].sort(key=region_x1)

                textlines_in_rows.append(textlines_in_row)

                # exit loop if no more textlines
                total_num_of_cells = sum(len(t) for t in textlines_in_columns)
                if total_num_of_cells == 0:
                    #textlines_in_rows.append(textlines_in_row)
                    break

            # append page result to pages result
            is_first_row = True
            last_row = None
            text_y_size_of_current_textline = Decimal(10.0)
            last_textline = None
            for row_index in range(len(textlines_in_rows)):
                y_difference = 0
                is_y_difference_calculated = False
                for col_index in range(len(textlines_in_rows[row_index])):
                    for textline_index, textline in enumerate(textlines_in_rows[row_index][col_index]):
                        if is_first_row:
                            if not (textline.region.y2 - textline.region.y1) <= Decimal(0.00):
                                y_difference = math.floor((self.rule.region.y2 - textline.region.y2) / text_y_size_of_current_textline)
                                is_y_difference_calculated = True
                                break
                        else:
                            if not (textline.region.y2 - textline.region.y1) <= Decimal(0.00):
                                if last_textline == None:
                                    break
                                y_difference = math.floor((last_textline.region.y1 - textline.region.y2) / text_y_size_of_current_textline)
                                is_y_difference_calculated = True
                                break
                    if is_y_difference_calculated:
                        break

                for i in range(y_difference):
                    result_body.append([''] * len(textlines_in_rows[row_index]))

                is_first_row = False

                result_in_row = []
                for col_index in range(len(textlines_in_rows[row_index])):
                    result_in_col = ""
                    for textline_index, textline in enumerate(textlines_in_rows[row_index][col_index]):
                        table_column_x_in_abs_value = table_column_xs[col_index] / 100 * page.region.x2
                        if re.match("[.]+", textline.text):
                            textline.text = re.sub("[.]+", "", textline.text)
                        if col_index == 0:
                            x_difference = math.floor((textline.region.x1 - table_column_x_in_abs_value) / text_x_size_of_current_textline) - len(result_in_col)
                            spaces = " " * x_difference
                            result_in_col = result_in_col + spaces + textline.text
                        else:
                            x_difference = math.floor((textline.region.x1 - table_column_x_in_abs_value) / text_x_size_of_current_textline) - len(result_in_col)
                            if x_difference <= 0 and len(result_in_col) > 0:
                                x_difference = 0
                            spaces = " " * x_difference
                            result_in_col = result_in_col + spaces + textline.text
                        if col_index == (len(textlines_in_rows[row_index])):
                            x_difference = math.floor((self.rule.region.x2 - textline.region.x1) / text_x_size_of_current_textline) - len(result_in_col)
                            spaces = " " * x_difference
                            result_in_col = result_in_col + spaces + textline.text
                        last_textline = textline
                    result_in_row.append(result_in_col)

                result_body.append(result_in_row)


        result_header = list(range(0, len(result_body[0])))
        result = {
            'header': result_header,
            'body': result_body
        }
        return result"""