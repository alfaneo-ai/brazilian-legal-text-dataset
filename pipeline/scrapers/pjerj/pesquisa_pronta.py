import logging
import os.path
import re
from io import StringIO

import requests
import pandas as pd
from bs4 import BeautifulSoup
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


from pipeline.utils import DirectoryUtil, PathUtil, TextUtil, DatasetManager


RESOURCES_DIRECTORY_PATH = 'resources'
FILES_DIRECTORY_PATH = 'files'
FILE_NAME = 'pesquisas-prontas-pjerj.pdf'
DIRECTORY_PATH = f'{RESOURCES_DIRECTORY_PATH}/{FILES_DIRECTORY_PATH}'
COMPLETE_FILE_PATH = f'{RESOURCES_DIRECTORY_PATH}/{FILES_DIRECTORY_PATH}/{FILE_NAME}'
METADATA = []
HEADER = {'assunto': [], 'ementa': []}
SPREAD_SHEET_NAME = 'pesquisas-prontas-pjerj.csv'


def html_extractor(response):
    return BeautifulSoup(response.text, 'html.parser')


class PjerjPesquisaProntaScrapper:
    def __init__(self):
        self.directory_util = DirectoryUtil(RESOURCES_DIRECTORY_PATH)
        self.link_page = LinkPage()
        self.document_page = DocumentPage()
        self.pdf_reader = PdfReader(DIRECTORY_PATH)
        self.pdf_parser = PdfParser()
        self.dataset_manager = DatasetManager()
        self.links = None
        self.current_content = None
        self.current_pdf_content = None
        self.current_subject = None
        self.current_ementas = []

    def execute(self):
        logging.info(f'Iniciando a execução do Scrapper PJERJ Pesquisa Pronta')
        self.__clean_up_previous_execution()
        self.__get_documents_links()
        self.__create_temporary_directory()
        for link in self.links:
            self.__get_document_content(link)
            self.__download_temporary_file()
            self.__read_temporary_file()
            self.__split_file_content()
            self.__extract_subject_from_file()
            if bool(self.current_subject):
                self.__extract_ementas_from_text()
                self.__append_data_to_list()
                self.__reset_current_indexes()
        self.__create_spreadsheet_dataset()
        logging.info('O Scrapper PJERJ Pesquisa Pronta foi finalizado com sucesso')

    def __clean_up_previous_execution(self):
        if self.directory_util.is_there_directory(FILES_DIRECTORY_PATH):
            self.directory_util.delete_directory(FILES_DIRECTORY_PATH)

    def __get_documents_links(self):
        self.links = self.link_page.execute()

    def __create_temporary_directory(self):
        self.directory_util.create_directory(FILES_DIRECTORY_PATH)

    def __get_document_content(self, url):
        self.current_content = self.document_page.execute(url)

    def __download_temporary_file(self):
        filepath = os.path.join(COMPLETE_FILE_PATH)
        directory_to_export = PathUtil.build_path(filepath)
        with open(directory_to_export, 'wb') as file:
            file.write(self.current_content)

    def __read_temporary_file(self):
        self.current_pdf_content = self.pdf_reader.read(FILE_NAME)

    def __split_file_content(self):
        self.current_pdf_content = self.pdf_parser.split_text_by_pattern(self.current_pdf_content)

    def __extract_subject_from_file(self):
        self.current_subject = self.pdf_parser.extract_subject_from_text(self.current_pdf_content[0])

    def __extract_ementas_from_text(self):
        for splited_block in self.current_pdf_content:
            try:
                self.current_ementas.append(self.pdf_parser.extract_ementa_from_text(splited_block))
            except AttributeError:
                pass

    def __append_data_to_list(self):
        for ementa in self.current_ementas:
            METADATA.append({
                'assunto': self.current_subject,
                'ementa': ementa
            })

    def __reset_current_indexes(self):
        self.current_content = None
        self.current_pdf_content = None
        self.current_subject = None
        self.current_ementas = []

    def __create_spreadsheet_dataset(self):
        dataframe = pd.DataFrame(HEADER)
        dataframe = dataframe.append(METADATA, ignore_index=True)
        filepath = PathUtil.build_path(RESOURCES_DIRECTORY_PATH, SPREAD_SHEET_NAME)
        self.dataset_manager.to_csv(dataframe, filepath, index=False)


class LinkPage:
    def __init__(self):
        self.url = 'http://www.tjrj.jus.br/web/guest/institucional/dir-gerais/dgcon/pesquisa-selecionada'
        self.parser = LinkParser()

    def execute(self):
        response = requests.get(self.url)
        return self.parser.execute(response)


class DocumentPage:
    def execute(self, url):
        return requests.get(url).content


class LinkParser:
    def __init__(self):
        self.html = None
        self.unformatted_links = None
        self.links = []
        self.main_container_class = 'webcontent'
        self.target_tag_name = '_blank'
        self.link_starts_with = '/documents/'
        self.base_url = 'http://portaltj.tjrj.jus.br'

    def execute(self, response):
        self.html = html_extractor(response)
        self.__get_links_from_html()
        self.__remove_unwanted_urls()
        return self.links

    def __get_links_from_html(self):
        content_container = self.html.find('div', {'class': self.main_container_class})
        self.unformatted_links = content_container.findAll('a', {'target': self.target_tag_name})

    def __remove_unwanted_urls(self):
        for link in self.unformatted_links:
            link_href = link['href']
            if self.__is_link_from_document(link_href):
                formated_link = self.__format_url(link_href)
                self.links.append(formated_link)

    def __is_link_from_document(self, link):
        return link.startswith(self.link_starts_with)

    def __format_url(self, url):
        if self.base_url not in url:
            return self.base_url + url


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


class PdfParser:
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
