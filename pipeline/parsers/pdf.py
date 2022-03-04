import logging
import os.path
import re
import time
from io import StringIO
from os import listdir
from os.path import isfile, join

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pipeline.utils import TextUtil, PathUtil, DirectoryUtil


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


class PdfFgvParser:
    OUTPUT_DIR_PATH = 'output'
    BOOKS_DIR_PATH = 'books'
    EXTRACTED_BOOK_PATH = 'extracted_books'
    PDF_EXTENSION = 'pdf'
    TXT_EXTENSION = 'txt'

    def __init__(self):
        self.complete_book_path = f'{self.OUTPUT_DIR_PATH}/{self.BOOKS_DIR_PATH}'
        self.complete_extracted_book_path = f'{self.OUTPUT_DIR_PATH}/{self.EXTRACTED_BOOK_PATH}'
        self.pdf_reader = PdfReader(self.complete_book_path)
        self.directory_util = DirectoryUtil(self.OUTPUT_DIR_PATH)
        self.file_name_list = []
        self.current_extracted_text = None
        self.current_file_name = None

    def execute(self):
        self.__clean_up_previous_execution()
        self.__get_file_name_list()
        self.__log_number_of_files_found()
        self.__create_extracted_books_directory()
        for file in self.file_name_list:
            self.__extract_text_from_file(file)
            self.__create_txt_file_name(file)
            self.__write_extracted_content()
            self.__log_succes_in_writing()

    def __clean_up_previous_execution(self):
        if self.directory_util.is_there_directory(self.EXTRACTED_BOOK_PATH):
            self.directory_util.delete_directory(self.EXTRACTED_BOOK_PATH)

    def __get_file_name_list(self):
        self.file_name_list = [file for file in listdir(self.complete_book_path) if isfile(join(self.complete_book_path, file))]

    def __log_number_of_files_found(self):
        logging.info(f'Foram encontrados {len(self.file_name_list)} arquivos no diretório {self.complete_book_path}')

    def __create_extracted_books_directory(self):
        self.directory_util.create_directory(self.EXTRACTED_BOOK_PATH)

    def __extract_text_from_file(self, file):
        self.current_extracted_text = self.pdf_reader.read(file)

    def __create_txt_file_name(self, file):
        self.current_file_name = re.sub(self.PDF_EXTENSION, self.TXT_EXTENSION, file)

    def __write_extracted_content(self):
        file_path = os.path.join(f'{self.complete_extracted_book_path}/{self.current_file_name}')
        directory_to_export = PathUtil.build_path(file_path)
        with open(directory_to_export, 'w') as text:
            text.write(self.current_extracted_text)

    def __log_succes_in_writing(self):
        logging.info(f'O texto {self.current_file_name} foi escrito com sucesso')
