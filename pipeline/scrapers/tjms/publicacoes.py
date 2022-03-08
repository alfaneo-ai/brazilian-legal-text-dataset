import logging
import os.path

import requests

from pipeline.utils import DirectoryUtil, PathUtil

URLS = ['https://www.tjms.jus.br/storage/cms-arquivos/315fb9ed6a14ebd859c932e47e042a0e.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/e91a0438b8e7f1b60ec87eabdca89d2d.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/0ef807f511efa48e2c48be4ecf393c4f.pdf',
        'https://www.tjms.jus.br/areas/comunicacao/Relatorio10anos.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/046c18c89043188433ebfe2fb28abd36.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/59900338a2d1396702702e8ccc4ea5e0.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/214887218bb04dc91c851900b077a7c2.pdf',
        'https://www.tjms.jus.br/areas/comunicacao/LivroEstrelasnaCabana.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/8027bf43bc8b412e51f3ff31e03ab453.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/7a8b1c9a6c549c228b90aff1e3010860.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/2b05ce8801d38740adba516ba4e1a9bc.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/728dad6f35193394e260b8bca2ddd13f.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/be91ec96fde6dff2621bbf937e5f8077.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/c18c5fb28ef133bd48b2f1e8da2caf2d.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/5d3c9cd236177bd0028fcb968b592e6d.pdf',
        'https://www.tjms.jus.br/areas/comunicacao/RelatorioBienioPaschoal.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/30408dc2f804af5871b375541f7bb9de.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/1739597a78c5ef7e0121a3e37d94e4f4.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/b5a5b92be3b65a3d4591c5d621231e90.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/fed08987a24721a397e2f0e5b4c8f65c.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/a4936b7ea580205982a6bb12ba1b1308.pdf',
        'https://www.tjms.jus.br/storage/cms-arquivos/124580f40bb889b35172d09e6fd2d7c4.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/audiencia-virtual-google-meet.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/DialogandoIgualdades.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/CartilhaVDCovid.pdf',
        'https://www.tjms.jus.br/areas/comunicacao/Cartilha2021.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/ComitedePriorizacaodoPrimeiroGrau.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/informe_tecnico_2020_prova06.pdf',
        'https://www.tjms.jus.br/violenciadomestica/arquivos/relatorios/RelatoriodeAtividades2017-2019.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatoriotjms10anos.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-feminicidio-2019.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/revista-40anos.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/cartilha-do-homem.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/cartilha-de-genero-raca-e-diversidade-para-o-portal.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/RevistaMulherBrasileira_Ed3.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-corregedoria-2017-2018.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-cij-2017-2018.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2017-2018.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/RevistaMulherBrasileira_Ed2.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/revistamulher.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2015-2016.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-corregedoria-2015-2016.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2014.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2013-2014.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2013.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-corregedoria-2013-2014.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2012.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/revista-cij.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/revista-santini.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/revista-elpidio.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/relatorio-gestao-2009-2010.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/publica20anos.pdf',
        'https://www.tjms.jus.br/_estaticos_/sc/publicacoes/publica15anos.pdf']
OUTPUT_DIRECTORY_PATH = 'output'
BOOKS_DIRECTORY_PATH = 'books'


class TjmsPublicacoesScrapper:
    def __init__(self):
        self.directory_util = DirectoryUtil(OUTPUT_DIRECTORY_PATH)
        self.current_content = None
        self.current_filepath = None

    def execute(self):
        logging.info('Iniciando execução do Scrapper TJMS Publicações')
        self.__create_temporary_directory()
        for index, url in enumerate(URLS):
            self.__set_current_file_attributes(index, url)
            self.__download_file()
        logging.info('O Scrapper TJMS Publicações foi finalizado com sucesso')

    def __create_temporary_directory(self):
        if self.directory_util.is_there_directory(BOOKS_DIRECTORY_PATH) is False:
            self.directory_util.create_directory(BOOKS_DIRECTORY_PATH)

    def __set_current_file_attributes(self, index, url):
        self.current_content = requests.get(url).content
        self.current_filepath = f'{OUTPUT_DIRECTORY_PATH}/{BOOKS_DIRECTORY_PATH}/pub-{index+1}.pdf'

    def __download_file(self):
        filepath = os.path.join(self.current_filepath)
        directory_to_export = PathUtil.build_path(filepath)
        with open(directory_to_export, 'wb') as file:
            file.write(self.current_content)
