from typing import Container
from io import BytesIO, StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def convert_pdf_to_xml(
    path: str,
    format: str = "xml",
    codec: str = "utf-8",
    password: str = "",
    maxpages: int = 0,
    caching: bool = True,
    pagenos: Container[int] = set(),
) -> str:
    """Summary
    Parameters
    ----------
    path : str
        Path to the pdf file
    format : str, optional
        Format of output, must be one of: "text", "html", "xml".
        By default, "text" format is used
    codec : str, optional
        Encoding. By default "utf-8" is used
    password : str, optional
        Password
    maxpages : int, optional
        Max number of pages to convert. By default is 0, i.e. reads all pages.
    caching : bool, optional
        Caching. By default is True
    pagenos : Container[int], optional
        Provide a list with numbers of pages to convert
    Returns
    -------
    str
        Converted pdf file
    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    if format == "text":
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    elif format == "html":
        device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
    elif format == "xml":
        device = XMLConverter(rsrcmgr, retstr, laparams=laparams)
    else:
        raise ValueError("provide format, either text, html or xml!")
    fp = open(path, "rb")
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(
        fp,
        pagenos,
        maxpages=maxpages,
        password=password,
        caching=caching,
        check_extractable=True,
    ):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    text = text.replace('\n', '').replace('\'', '')
    text = text + "</pages>"
    return text


def convert_pdf_bytes_to_xml(
    bytes: BytesIO,
    format: str = "xml",
    codec: str = "utf-8",
    password: str = "",
    maxpages: int = 0,
    caching: bool = True,
    pagenos: Container[int] = set(),
) -> str:
    """Summary
    Parameters
    ----------
    path : str
        Path to the pdf file
    format : str, optional
        Format of output, must be one of: "text", "html", "xml".
        By default, "text" format is used
    codec : str, optional
        Encoding. By default "utf-8" is used
    password : str, optional
        Password
    maxpages : int, optional
        Max number of pages to convert. By default is 0, i.e. reads all pages.
    caching : bool, optional
        Caching. By default is True
    pagenos : Container[int], optional
        Provide a list with numbers of pages to convert
    Returns
    -------
    str
        Converted pdf file
    """
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == "text":
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    elif format == "html":
        device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
    elif format == "xml":
        device = XMLConverter(rsrcmgr, retstr, laparams=laparams)
    else:
        raise ValueError("provide format, either text, html or xml!")
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(
        bytes,
        pagenos,
        maxpages=maxpages,
        password=password,
        caching=caching,
        check_extractable=True,
    ):
        interpreter.process_page(page)
    text = retstr.getvalue().decode()
    device.close()
    retstr.close()
    text = text.replace('\n', '').replace('\'', '')
    text = text + "</pages>"
    return text

