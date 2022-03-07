import logging
import requests

from pipeline.parsers import CnjTotalHtmlParser, CnjSearchHtmlParser

MAIN_URL = 'https://bibliotecadigital.cnj.jus.br/jspui/browse?'
DOC_PER_PAGE = 100
URLS = []


class CnjBibliotecaDigitalScraper:
    def __init__(self):
        self.total_page = TotalPage()
        self.search_page = SearchPage()
        self.total = None
        self.current_page = 0
        self.count_page = None

    def execute(self):
        logging.info('Iniciando a execução do Scrapper Cnj Biblioteca Digital')
        self.__get_total_found()
        logging.info(f'Forma encontrados {self.total} livros em {self.count_page} páginas')
        while self.__has_next_page():
            logging.info(f'Iniciando busca na página {self.current_page + 1}')
            self.search_page.execute(self.current_page)
            self.__increment_page()
        print(URLS)
        logging.info('O Scrapper Cnj Biblioteca Digital foi finalizado com sucesso')

    def __get_total_found(self):
        self.total = self.total_page.execute()
        self.count_page = (self.total // DOC_PER_PAGE) + 1

    def __has_next_page(self):
        return self.current_page < self.count_page

    def __increment_page(self):
        self.current_page += 1

    def __reset_page_counters(self):
        self.current_page = 0
        self.count_page = 0


class TotalPage:
    def __init__(self):
        self.parser = CnjTotalHtmlParser()
        self.total_found = None

    def execute(self):
        self.__make_request()
        return self.total_found

    def __make_request(self):
        body = {
            'type': 'title',
            'sort_by': 1,
            'order': 'ASC',
            'rpp': DOC_PER_PAGE,
            'etal': -1,
            'null': '',
            'submit_browse': 'Atualizar'
        }
        response = requests.get(MAIN_URL, data=body)
        self.total_found = self.parser.execute(response)


class SearchPage:
    def __init__(self):
        self.parser = CnjSearchHtmlParser()
        self.body = {}
        self.urls_found = None

    def execute(self, current_page):
        self.__update_body(current_page)
        self.__make_request()
        self.__append_urls_to_main_list()

    def __update_body(self, current_page):
        self.body = {
            'type': 'title',
            'sort_by': 1,
            'order': 'ASC',
            'rpp': DOC_PER_PAGE,
            'etal': -1,
            'null': '',
            'offset': current_page * DOC_PER_PAGE
        }

    def __make_request(self):
        response = requests.get(MAIN_URL, data=self.body)
        self.urls_found = self.parser.execute(response)

    def __append_urls_to_main_list(self):
        for url in self.urls_found:
            URLS.append(url)
