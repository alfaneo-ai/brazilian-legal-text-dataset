import logging

import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

from pipeline.utils import PathUtil, DatasetManager

FIRST_PAGE_COUNT = 0
HEADER = {'assunto': [], 'ementa': []}
METADATA = []
PAGE_SIZE = 50
PAGE_INCREMENT = 1
SESSION = requests.Session()
URL = 'https://scon.stj.jus.br/SCON/pesquisar.jsp'


def update_body(current_search_code, page_counter):
    return {
        'numDocsPagina': PAGE_SIZE,
        'tipo_visualizacao': '',
        'filtroPorNota': '',
        'b': 'ACOR',
        'O': 'RR',
        'preConsultaPP': current_search_code,
        'thesaurus': 'JURIDICO',
        'p': True,
        'operador': 'E',
        'l': PAGE_SIZE,
        'i': page_counter
    }


def html_extractor(response):
    return BeautifulSoup(response.text, 'html.parser')


class SearchMapper:
    def __init__(self):
        self.map = {
            'SERVIDOR PÚBLICO': '000007226/0',
            'INFRAÇÃO AMBIENTAL': '000007498/0',
            'CONTRATO DE COMPRA E VENDA': '000007307/0',
            'RESPONSABILIDADE CIVIL': '000007274/0',
            'PRESCRIÇÃO': '000007384/0',
            'AÇÃO RESCISÓRIA': '000007313/0',
            'AÇÃO PENAL': '000007203/0',
            'COVID-19': '000006903/0',
            'CÉSIO-137': '000005746/0',
            'OPERAÇÃO LAVA-JATO': '000004803/0',
            'DEMARCAÇÃO DE TERRA INDÍGENA RAPOSA SERRA DO SOL': '000002201/0',
            'REMESSAS ILEGAIS DE DIVISAS PARA O EXTERIOR POR MEIO DO BANCO DO ESTADO DO PARANÁ': '000002213/0',
            'OPERAÇÃO CARAVELAS': '000002209/0',
            'OPERAÇÃO CANAÃ': '000002208/0',
            'OPERAÇÃO CAIXA DE PANDORA': '000002207/0',
            'OPERAÇÃO BOLA DE FOGO': '000002205/0',
            'OPERAÇÃO ALFA': '000002204/0',
            'MICROVLAR - PÍLULAS DE FARINHA': '000002200/0',
            'FURTO AO BANCO CENTRAL DE BRASIL EM FORTALEZA': '000002203/0',
            'CHACINA DE UNAÍ': '000002194/0',
            'ACIDENTE AÉREO - JATO LEGACY E BOEING 737-800 - GOL VOO 1907': '000002195/0',
            'MASSACRE ELDORADO DE CARAJÁS': '000002197/0',
            'PRISÃO EM CONTÊINERES': '000002198/0',
            'ORGANIZAÇÃO CRIMINOSA LIGA DA JUSTIÇA': '000002199/0',
            'OPERAÇÃO TELHADO DE VIDRO': '000002222/0',
            'OPERAÇÃO SÓFIA': '000002221/0',
            'OPERAÇÃO SATIAGRAHA': '000002220/0',
            'OPERAÇÃO SANGUESSUGA': '000002223/0',
            'OPERAÇÃO PLATA': '000002219/0',
            'OPERAÇÃO NAVALHA': '000002218/0',
            'OPERAÇÃO KOLIBRA': '000002216/0',
            'OPERAÇÃO GRANDES LAGOS': '000002215/0',
            'OPERAÇÃO FURACÃO': '000002214/0',
            'OPERAÇÃO DIAMANTE': '000002211/0',
            'OPERAÇÃO CONEXÃO CRICIÚMA': '000002210/0'
        }

    def get_map_value_by_key(self, key):
        return self.map[key]


class StjPesquisaProntaScraper(SearchMapper):
    def __init__(self):
        super(StjPesquisaProntaScraper, self).__init__()
        self.rootpath = PathUtil.build_path('output', 'sts')
        self.total_page = TotalPage()
        self.search_page = SearchPage()
        self.dataset_manager = DatasetManager()
        self.current_search_code = None
        self.total = None
        self.current_page = None
        self.count_page = None

    def execute(self):
        logging.info('Iniciando a execução do Scrapper STJ Pesquisa Pronta')
        for subject in self.map.keys():
            self.current_search_code = self.get_map_value_by_key(subject)
            self.__get_total_found()
            self.__set_pages_counters()
            logging.info(f'A consulta "{subject}" retornou {self.total} documento(s) em {self.count_page} página(s)')
            while self.__has_next_page():
                logging.info(f'Iniciando busca na página {self.current_page + PAGE_INCREMENT}')
                self.search_page.execute(self.current_search_code, subject, self.current_page)
                self.__increment_page_counters()
        logging.info(f'O Scrapper processou um total de {len(METADATA)} documento(s) e está escrevendo o dataset '
                     f'"pesquisas-prontas-stj.csv"')
        self.__create_spreasheet_dataset()
        logging.info(f'O Scrapper STJ Pesquisa Pronta foi finalizado com sucesso')

    def __get_total_found(self):
        self.total = int(self.total_page.execute(self.current_search_code))

    def __set_pages_counters(self):
        self.current_page = FIRST_PAGE_COUNT
        self.count_page = (int(self.total) // PAGE_SIZE) + PAGE_INCREMENT

    def __has_next_page(self):
        return (self.current_page + PAGE_INCREMENT) <= self.count_page

    def __increment_page_counters(self):
        self.current_page += PAGE_INCREMENT

    def __create_spreasheet_dataset(self):
        dataframe = pd.DataFrame(HEADER)
        dataframe = dataframe.append(METADATA, ignore_index=True)
        filepath = PathUtil.build_path('resources', 'pesquisas-prontas-stj.csv')
        self.dataset_manager.to_csv(dataframe, filepath, index=False)


class TotalPage:
    def __init__(self):
        self.html = None
        self.body = {}
        self.current_search_code = None
        self.parser = TotalParser()
        self.total_found = None

    def execute(self, search_code):
        self.__update_current_code(search_code)
        self.__update_body()
        self.__make_request()
        return self.total_found

    def __update_current_code(self, search_code):
        self.current_search_code = search_code

    def __update_body(self):
        self.body = update_body(self.current_search_code, PAGE_INCREMENT)

    def __make_request(self):
        response = requests.post(url=URL, data=self.body)
        self.total_found = self.parser.execute(response)


class SearchPage:
    def __init__(self):
        self.body = {}
        self.current_search_code = None
        self.current_page_counter = None
        self.parser = SearchParser()

    def execute(self, search_code, subject, current_page):
        self.__update_current_code(search_code, current_page)
        self.__update_body()
        self.__make_request(subject)

    def __update_current_code(self, search_code, current_page):
        self.current_search_code = search_code
        self.current_page_counter = (current_page * PAGE_SIZE) + PAGE_INCREMENT

    def __update_body(self):
        self.body = update_body(self.current_search_code, self.current_page_counter)

    def __make_request(self, subject):
        response = requests.post(url=URL, data=self.body)
        self.parser.execute(response, subject)


class TotalParser:
    def __init__(self):
        self.html = None
        self.total_found = None

    def execute(self, response):
        self.html = html_extractor(response)
        self.__get_total_from_html()
        return self.total_found

    def __get_total_from_html(self):
        search_container = self.html.find('div', {'id': 'infopesquisa'})
        div_row = search_container.findAll('div', {'class': 'divRow'})
        div_cell = div_row[0].findAll('div', {'class': 'divCell'})
        total_label = div_cell[0].label.text.strip()
        self.total_found = re.sub("[^0-9]", "", total_label)


class SearchParser:
    def __init__(self):
        self.subject = None
        self.html = None
        self.documents_found = None

    def execute(self, response, subject):
        self.subject = subject
        self.html = html_extractor(response)
        self.__get_documents_from_html()
        self.__extract_metadata_from_documents()

    def __get_documents_from_html(self):
        documents_container = self.html.find('div', {'class': 'listadocumentos'})
        self.documents_found = documents_container.findAll('div', {'class', 'documento'})

    def __extract_metadata_from_documents(self):
        for document in self.documents_found:
            metadata = {'assunto': self.subject}
            for field in document.findAll('div', {'class': 'paragrafoBRS'}):
                field_name = field.find('div', {'class': 'docTitulo'}).text
                if field_name == 'Ementa':
                    field_content = self.__remove_unwanted_characters(field.find('div', {'class': 'docTexto'}).text)
                    if self.__does_sentence_exist(field_content):
                        metadata['ementa'] = self.__remove_unwanted_characters(field_content)
                        METADATA.append(metadata)

    @staticmethod
    def __remove_unwanted_characters(phrase):
        new_phrase = re.sub(' +', ' ', phrase)
        return re.sub('[\r\n]"', ' ', new_phrase)

    @staticmethod
    def __does_sentence_exist(sentence):
        return len(sentence.split()) > 10
