import re

from nltk import tokenize
from .cleaner import Cleaner
from bs4 import BeautifulSoup
from .segmentation import DefaultSegmentation
from pipeline.utils import WorkProgress, DatasetManager, PathUtil, TextUtil


class HtmlParser:
    def __init__(self, selector, folder, enable_segmentation=False):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.cleaner = Cleaner()
        self.selector = selector
        self.rootpath = PathUtil.build_path('output', 'mlm', folder)
        self.enable_segmentation = enable_segmentation
        self.default_segmentation = DefaultSegmentation()

    def execute(self):
        self.work_progress.show('Staring html parser')
        filepaths = PathUtil.get_files(self.rootpath, '*.html')
        for filepath in filepaths:
            self.work_progress.show(f'Parsing {filepath}')
            content = self.dataset_manager.from_text(filepath)
            paragraphs = self.selector.get_text(content)
            paragraphs = self.segmentation_sentences(paragraphs)
            paragraphs = self.cleaner.clear(paragraphs)
            output_filepath = self.get_output_filepath(filepath)
            self.dataset_manager.to_file(output_filepath, paragraphs)
            self.work_progress.show(f'File created in {output_filepath}')
        self.work_progress.show('Html parser has finished!')

    def segmentation_sentences(self, paragraphs):
        if not self.enable_segmentation:
            return paragraphs

        sentences = []
        for paragraph in paragraphs:
            paragraphs_sents = self.default_segmentation.split(paragraph)
            if len(paragraphs_sents) > 0:
                sentences = sentences + paragraphs_sents
        return sentences

    @staticmethod
    def get_output_filepath(source_filepath):
        part = source_filepath.split('.', maxsplit=1)[0]
        return f'{part}.txt'


class SumulaHtmlSelector:
    @staticmethod
    def get_text(html):
        html_parse = BeautifulSoup(html, 'html.parser')
        container = html_parse.find(id='conteudo')
        blocks = container.find_all('div', {'class': 'parCOM'})
        paragraphs = []
        for block in blocks:
            paragraph = block.find('p')
            if paragraph:
                paragraphs.append(paragraph.text)
        return paragraphs


class EnciclopediaHtmlSelector:
    @staticmethod
    def get_text(html):
        html_parse = BeautifulSoup(html, 'html.parser')
        blocks = html_parse.find_all('p')
        paragraphs = []
        exclusion = ['notas-verbetes', 'bibliografia-verbetes', 'citacao-verbetes', 'edicoes-verbetes',
                     'artigos-verbetes']
        for block in blocks:
            if 'class' in block.parent.attrs:
                parent_class = block.parent['class'][0]
                if parent_class not in exclusion:
                    paragraphs.append(block.text)
            else:
                paragraphs.append(block.text)
        return paragraphs


class ParagraphHtmlSelector:
    @staticmethod
    def get_text(html):
        html_parse = BeautifulSoup(html, 'html.parser')
        paragraphs = html_parse.find_all('p')
        return [paragraph.text for paragraph in paragraphs]


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


class StjTotalHtmlParser:
    def __init__(self):
        self.html = None
        self.total_found = None

    def execute(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')
        self.__get_total_from_html()
        return self.total_found

    def __get_total_from_html(self):
        search_container = self.html.find('div', {'id': 'infopesquisa'})
        div_row = search_container.findAll('div', {'class': 'divRow'})
        div_cell = div_row[0].findAll('div', {'class': 'divCell'})
        total_label = div_cell[0].label.text.strip()
        self.total_found = re.sub('[^0-9]', '', total_label)


class StjSearchHtmlParser:
    def __init__(self):
        self.subject = None
        self.html = None
        self.documents_found = None

    def execute(self, response, subject):
        self.subject = subject
        self.html = BeautifulSoup(response.text, 'html.parser')
        self.__get_documents_from_html()
        return self.__extract_metadata_from_documents()

    def __get_documents_from_html(self):
        documents_container = self.html.find('div', {'class': 'listadocumentos'})
        self.documents_found = documents_container.findAll('div', {'class', 'documento'})

    def __extract_metadata_from_documents(self):
        metadata_from_document = []
        for document in self.documents_found:
            metadata = {'assunto': self.subject}
            for field in document.findAll('div', {'class': 'paragrafoBRS'}):
                field_name = field.find('div', {'class': 'docTitulo'}).text
                if field_name == 'Ementa':
                    field_content = self.__remove_unwanted_characters(field.find('div', {'class': 'docTexto'}).text)
                    if self.__does_sentence_exist(field_content):
                        metadata['ementa'] = self.__remove_unwanted_characters(field_content)
                        metadata_from_document.append(metadata)
        return metadata_from_document

    @staticmethod
    def __remove_unwanted_characters(phrase):
        new_phrase = re.sub(' +', ' ', phrase)
        return re.sub('[\r\n]"', ' ', new_phrase)

    @staticmethod
    def __does_sentence_exist(sentence):
        return len(sentence.split()) > 10


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


class CnjTotalHtmlParser:
    def __init__(self):
        self.html = None
        self.total = None

    def execute(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')
        self.__get_total_from_html()
        return int(self.total)

    def __get_total_from_html(self):
        self.total = self.html.find('div', {'class': 'panel-footer text-center'}).text
        self.__remove_alphabetic_charsets()

    def __remove_alphabetic_charsets(self):
        self.total = tokenize.word_tokenize(self.total)
        new_numbers = []
        for splited_word in self.total:
            if splited_word.isdigit() is True:
                new_numbers.append(splited_word)
        self.total = new_numbers[-1]


class CnjSearchHtmlParser:
    def __init__(self):
        self.html = None
        self.main_url = 'https://bibliotecadigital.cnj.jus.br'

    def execute(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')
        return self.__get_urls_from_page()

    def __get_urls_from_page(self):
        urls = []
        docs_table = self.html.find('table', {'class': 'table'})
        for index, document in enumerate(docs_table.findAll('tr')):
            if index != 0:
                doc_info = document.find('td', {'headers': 't2'})
                doc_title = TextUtil.slugify(doc_info.text)
                doc_url = doc_info.find('a')['href']
                urls.append({
                    'titulo': doc_title,
                    'url': self.main_url + doc_url
                })
        return urls
