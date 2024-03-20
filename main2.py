import fitz  # PyMuPDF
import json
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as ETElement
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

# Open the PDF file
doc = fitz.open("Test2.pdf")

def convert_json_to_xml(json_dict):

    xml = ET.fromstring('<pages></pages>')

    page_width = int(json_dict['width'])
    page_height = int(json_dict['height'])
    page = SubElement(xml, "page", attrib={
        "bbox": "0.000,0.000," + str(page_width) + "," + str(page_height)})
    
    for block in json_dict["blocks"]:

        for line in block["lines"]:

            for span in line["spans"]:

                ocr_line_x1 = int(span['bbox'][0])
                ocr_line_y1 = page_height - int(span['bbox'][3])
                ocr_line_x2 = int(span['bbox'][2])
                ocr_line_y2 = page_height - int(span['bbox'][1])

                textline = SubElement(
                    page,
                    "textline",
                    attrib={
                        "bbox": str(ocr_line_x1) + "," + str(ocr_line_y1) + "," + str(ocr_line_x2) + "," + str(ocr_line_y2),
                    },
                )

                ocrx_word = span['text']

                word_in_line_count = 0
                for char in span['text']:

                    char_x1 = (ocr_line_x2 - ocr_line_x1) / \
                        len(ocrx_word) * word_in_line_count + ocr_line_x1
                    char_x2 = (ocr_line_x2 - ocr_line_x1) / \
                        len(ocrx_word) * \
                        (word_in_line_count + 1) + ocr_line_x1
                    char_y1 = ocr_line_y1
                    char_y2 = ocr_line_y2

                    char_x1 = int(char_x1)
                    char_y1 = int(char_y1)
                    char_x2 = int(char_x2)
                    char_y2 = int(char_y2)
                    
                    text = SubElement(
                            textline,
                            "text",
                            attrib={
                                "font": "AAAAAA+invisible",
                                "bbox": str(char_x1) + "," + str(char_y1) + "," + str(char_x2) + "," + str(char_y2),
                                "conf": str(100.00)
                            },
                        )
                    text.text = char

                    word_in_line_count += 1
        
    ET.ElementTree(xml).write("output.xml", xml_declaration=True, encoding="utf-8")

# Loop through each page in the document
for page in doc:
    text_page = page.get_textpage()
    json_dict = json.loads(text_page.extractJSON())
    
    print(json)

    f = open("output.json", "a", encoding="utf-8")
    convert_json_to_xml(json_dict)
    #f.write(json_dict)
    f.close()
