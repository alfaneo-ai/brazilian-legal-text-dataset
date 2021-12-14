import logging
from xml.etree import ElementTree

import requests

from pipeline.utils import WorkProgress, DatasetManager, PathUtil


class CjfThesaurusScraper:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.all_terms = []

    def execute(self):
        self.work_progress.show('Starting scraper for CJF thesaurus')
        page = ThesaurusCjfPage()
        all_terms = []
        for i in range(9):
            all_terms += page.next_page()
        targetpath = self.create_folder()
        filepath = PathUtil.join(targetpath, 'cjf_thesaurus.txt')
        self.dataset_manager.to_file(filepath, all_terms)
        self.work_progress.show('Scraper has finished!')

    @staticmethod
    def create_folder():
        targetpath = PathUtil.build_path('output', 'mlm', 'cjf')
        return PathUtil.create_dir(targetpath, targetpath)


class ThesaurusCjfPage:

    def __init__(self):
        self.session = requests.Session()
        self.current_page = 1
        self.header = {
            'Referer': 'https://www.cjf.jus.br/terminologia/service/SrvThesaurus.asp',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        }

    def next_page(self):
        logging.info(f'Making a request for page {self.current_page}')
        url = f'https://www.cjf.jus.br/terminologia/service/SrvThesaurus.asp?task=pesquisaThesaurus&page={self.current_page}&total=1000&order=descricao'
        response = self.session.get(url, headers=self.header)
        logging.debug(f'Getting a status code {response.status_code}')
        self.current_page += 1
        terms = ThesaurusCjfParser.parse(response)
        logging.info(f'{len(terms)} terms has parsed')
        return terms


class ThesaurusCjfParser:
    @staticmethod
    def parse(response):
        terms = []
        root = ElementTree.fromstring(response.content)
        elements = root.findall('Result/Object')
        for element in elements:
            term = element.get('Column2')
            terms.append(term)
        return terms
