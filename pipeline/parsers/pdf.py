import re
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pipeline.utils import TextUtil, PathUtil


class PdfReader:
    def __init__(self, working_directory):
        self.working_directory = working_directory

    def read(self, file_path):
        complete_file_path = PathUtil.build_path(self.working_directory, file_path)
        pdf_content = StringIO()

        with open(complete_file_path, 'rb') as pdf_file:
            parser = PDFParser(pdf_file)
            document = PDFDocument(parser)
            pdf_resource_manager = PDFResourceManager()
            device = TextConverter(pdf_resource_manager, pdf_content, laparams=LAParams())
            interpreter = PDFPageInterpreter(pdf_resource_manager, device)
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
        return pdf_content.getvalue()


class PdfPjerjParser:
    def __init__(self):
        self.split_pattern = '={3,}'
        self.subject_split_pattern = 'Banco'
        self.ementa_search_pattern = r'CÂMARA CÍVEL(.*?)Íntegra do Acórdão'

    def split_text_by_pattern(self, text):
        return re.split(self.split_pattern, text)

    def extract_subject_from_text(self, text):
        subject = re.split(self.subject_split_pattern, text)
        return TextUtil.remove_breaking_lines(subject[0])

    def extract_ementa_from_text(self, text):
        formated_text = TextUtil.remove_breaking_lines(text)
        return re.search(self.ementa_search_pattern, formated_text).group(1)