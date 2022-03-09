import logging
import os.path
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from pipeline.utils import DirectoryUtil, PathUtil, DatasetManager, PdfReader, TextUtil, WorkProgress

OUTPUT_DIRECTORY_PATH = 'output'
RESOURCES_DIRECTORY_PATH = 'resources'
FILES_DIRECTORY_PATH = 'files'
FILE_NAME = 'pesquisas-prontas-pjerj.pdf'
DIRECTORY_PATH = f'{OUTPUT_DIRECTORY_PATH}/{FILES_DIRECTORY_PATH}'
COMPLETE_FILE_PATH = f'{OUTPUT_DIRECTORY_PATH}/{FILES_DIRECTORY_PATH}/{FILE_NAME}'
METADATA = []
HEADER = {'assunto': [], 'ementa': []}
SPREAD_SHEET_NAME = 'pesquisas-prontas-pjerj.csv'
SEARCH_URL = 'http://www.tjrj.jus.br/web/guest/institucional/dir-gerais/dgcon/pesquisa-selecionada'


class PjerjPesquisaProntaScrapper:
    def __init__(self):
        self.directory_util = DirectoryUtil(OUTPUT_DIRECTORY_PATH)
        self.html_parser = PjerjHtmlParser()
        self.pdf_reader = PdfReader()
        self.pdf_parser = PdfPjerjParser()
        self.progess = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.links = None
        self.current_content = None
        self.current_pdf_content = None
        self.current_subject = None
        self.current_ementas = []

    def execute(self):
        self.progess.show(f'Starting Scrapper PJERJ Selected Cases execution')
        self.__clean_up_previous_execution()
        self.__get_documents_links()
        self.__create_temporary_directory()
        self.progess.start(len(self.links))
        for link in self.links:
            self.__get_document_content(link)
            self.__download_temporary_file()
            self.__read_temporary_file()
            self.__split_file_content()
            self.__extract_subject_from_file()
            if self.__does_document_has_subject:
                self.__extract_ementas_from_text()
                self.__append_data_to_list()
                self.__reset_current_indexes()
                self.progess.step(f'Download: {link}')
        self.__create_spreadsheet_dataset()
        self.progess.show('Scrapper PJERJ Selected Cases was successfully completed')

    def __clean_up_previous_execution(self):
        if self.directory_util.is_there_directory(FILES_DIRECTORY_PATH):
            self.directory_util.delete_directory(FILES_DIRECTORY_PATH)

    def __get_documents_links(self):
        response = requests.get(SEARCH_URL)
        self.links = self.html_parser.execute(response)

    def __create_temporary_directory(self):
        self.directory_util.create_directory(FILES_DIRECTORY_PATH)

    def __get_document_content(self, url):
        self.current_content = requests.get(url).content

    def __download_temporary_file(self):
        filepath = os.path.join(COMPLETE_FILE_PATH)
        directory_to_export = PathUtil.build_path(filepath)
        with open(directory_to_export, 'wb') as file:
            file.write(self.current_content)

    def __read_temporary_file(self):
        filepath = PathUtil.build_path(FILE_NAME)
        self.current_pdf_content = self.pdf_reader.read(filepath)

    def __split_file_content(self):
        self.current_pdf_content = self.pdf_parser.split_text_by_pattern(self.current_pdf_content)

    def __extract_subject_from_file(self):
        self.current_subject = self.pdf_parser.extract_subject_from_text(self.current_pdf_content[0])

    def __does_document_has_subject(self):
        return bool(self.current_subject)

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


class PjerjHtmlParser:
    def __init__(self):
        self.html = None
        self.unformatted_links = None
        self.links = []
        self.main_container_class = 'webcontent'
        self.target_tag_name = '_blank'
        self.link_starts_with = '/documents/'
        self.base_url = 'http://portaltj.tjrj.jus.br'

    def execute(self, response):
        self.__extract_html_from_response(response)
        self.__get_links_from_html()
        self.__remove_unwanted_urls()
        return self.links

    def __extract_html_from_response(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')

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
