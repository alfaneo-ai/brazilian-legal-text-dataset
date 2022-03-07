import logging
import os.path

import requests

from pipeline.utils import DirectoryUtil, PathUtil
from pipeline.parsers import FgvHtmlParser


SEARCH_URL = 'https://direitosp.fgv.br/publicacoes/livros-digitais'
OUTPUT_DIRECTORY_PATH = 'output'
BOOKS_DIRECTORY_PATH = 'books'


class FgvLivrosDigitais:
    def __init__(self):
        self.directory_util = DirectoryUtil(OUTPUT_DIRECTORY_PATH)
        self.html_parser = FgvHtmlParser()
        self.books = None
        self.current_content = None
        self.current_filepath = None

    def execute(self):
        logging.info('Iniciando a execução do Scrapper FGV Livros Digitais')
        self.__get_documents_urls()
        self.__append_constitution_book_to_list()
        self.__create_temporary_directory()
        for book in self.books:
            self.__set_current_book_attributes(book)
            self.__download_book()
            logging.info(f'Livro {book["titulo"]} baixado com sucesso')
        logging.info('O Scrapper FGV Livros Digitais foi finalizado com sucesso')

    def __create_temporary_directory(self):
        if self.directory_util.is_there_directory(BOOKS_DIRECTORY_PATH) is False:
            self.directory_util.create_directory(BOOKS_DIRECTORY_PATH)

    def __get_documents_urls(self):
        response = requests.get(SEARCH_URL)
        self.books = self.html_parser.execute(response)

    def __append_constitution_book_to_list(self):
        self.books.append({
            'titulo': 'constituicao-e-o-supremo.pdf',
            'url': 'https://www.editoraforum.com.br/wp-content/uploads/2021/05/Constitui%C3%A7%C3%A3o-e-o-Supremo-Vers%C3%A3o-Completa-__-STF-Supremo-Tribunal-Federall.pdf'
        })

    def __set_current_book_attributes(self, book):
        self.current_content = requests.get(book['url']).content
        self.current_filepath = f'{OUTPUT_DIRECTORY_PATH}/{BOOKS_DIRECTORY_PATH}/{book["titulo"]}'

    def __download_book(self):
        filepath = os.path.join(self.current_filepath)
        directory_to_export = PathUtil.build_path(filepath)
        with open(directory_to_export, 'wb') as book:
            book.write(self.current_content)
