from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class PdfReader:

    @staticmethod
    def read(filepath):
        pdf_content = StringIO()

        with open(filepath, 'rb') as pdf_file:
            parser = PDFParser(pdf_file)
            document = PDFDocument(parser)
            pdf_resource_manager = PDFResourceManager()
            device = TextConverter(pdf_resource_manager, pdf_content, laparams=LAParams())
            interpreter = PDFPageInterpreter(pdf_resource_manager, device)
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
        return pdf_content.getvalue()
