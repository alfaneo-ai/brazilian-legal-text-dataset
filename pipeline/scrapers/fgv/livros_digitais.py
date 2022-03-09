import os.path

import requests
from bs4 import BeautifulSoup

from pipeline.utils import DirectoryUtil, PathUtil, TextUtil, WorkProgress

SEARCH_URL = 'https://direitosp.fgv.br/publicacoes/livros-digitais'
OUTPUT_DIRECTORY_PATH = 'output/mlm'
BOOKS_DIRECTORY_PATH = 'fgv'


class FgvLivrosDigitais:
    def __init__(self):
        self.directory_util = DirectoryUtil(OUTPUT_DIRECTORY_PATH)
        self.html_parser = FgvHtmlParser()
        self.progress = WorkProgress()
        self.books = None
        self.current_content = None
        self.current_filepath = None

    def execute(self):
        self.progress.show('Starting Scrapper FGV Livros Digitais')
        self.__get_documents_urls()
        self.__append_constitution_book_to_list()
        self.__create_temporary_directory()
        self.progress.start(len(self.books))
        for book in self.books:
            self.__set_current_book_attributes(book)
            self.__download_book()
            self.progress.step(f'Book {book["titulo"]} download done')
        self.progress.show('FGV Livros Digitais scrapper has finished')

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
        self.current_filepath = PathUtil.build_path(OUTPUT_DIRECTORY_PATH, BOOKS_DIRECTORY_PATH, f'{book["titulo"]}')

    def __download_book(self):
        filepath = os.path.join(self.current_filepath)
        directory_to_export = PathUtil.build_path(filepath)
        with open(directory_to_export, 'wb') as book:
            book.write(self.current_content)


class FgvHtmlParser:
    def __init__(self):
        self.html = None
        self.main_div_class = 'view view-livro-digital view-id-livro_digital view-display-id-block_1 view-dom-id-3'
        self.list_content_class = 'item-list'
        self.book_title_class = 'views-field-title'
        self.book_download_url_class = 'views-field-field-livrodig-arquivo-fid'
        self.url_list = []

    def execute(self, response):
        self.__extract_html_from_response(response)
        self.__get_urls_from_page()
        return self.url_list

    def __extract_html_from_response(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')

    def __get_urls_from_page(self):
        main_div = self.html.find('div', {'class': self.main_div_class})
        for books_list in main_div.findAll('div', {'class': self.list_content_class}):
            for book in books_list.ul.findAll('li'):
                book_title = book.find('div', {'class': self.book_title_class}).text
                book_url = book.find('div', {'class': self.book_download_url_class}).find('a')['href']
                self.url_list.append({
                    'titulo': TextUtil.slugify(book_title) + '.pdf',
                    'url': book_url
                })
