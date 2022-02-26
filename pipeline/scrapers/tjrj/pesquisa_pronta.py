import logging

import requests
from bs4 import BeautifulSoup


def html_extractor(response):
    return BeautifulSoup(response.text, 'html.parser')


class TjrjPesquisaProntaScrapper:
    def __init__(self):
        self.link_page = LinkPage()
        self.links = None

    def execute(self):
        logging.info(f'Iniciando a execução do Scrapper PJERJ Pesquisa Pronta')
        self.__get_documents_links()
        logging.info(f'{self.links}')
        logging.info('O Scrapper PJERJ Pesquisa Pronta foi finalizado com sucesso')

    def __get_documents_links(self):
        self.links = self.link_page.execute()


class LinkPage:
    def __init__(self):
        self.url = 'http://www.tjrj.jus.br/web/guest/institucional/dir-gerais/dgcon/pesquisa-selecionada'
        self.parser = LinkParser()

    def execute(self):
        response = requests.get(self.url)
        return self.parser.execute(response)


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
