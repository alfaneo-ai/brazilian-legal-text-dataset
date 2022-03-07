import logging
import os.path

import requests
import pandas as pd

from pipeline.utils import DirectoryUtil, PathUtil, DatasetManager
from pipeline.parsers import PdfReader, PdfPjerjParser, PjerjHtmlParser


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
        self.pdf_reader = PdfReader(DIRECTORY_PATH)
        self.pdf_parser = PdfPjerjParser()
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
            if self.__does_document_has_subject:
                self.__extract_ementas_from_text()
                self.__append_data_to_list()
                self.__reset_current_indexes()
        self.__create_spreadsheet_dataset()
        logging.info('O Scrapper PJERJ Pesquisa Pronta foi finalizado com sucesso')

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
        self.current_pdf_content = self.pdf_reader.read(FILE_NAME)

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
