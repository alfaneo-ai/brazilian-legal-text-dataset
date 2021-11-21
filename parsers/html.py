import re

from bs4 import BeautifulSoup

from utils import WorkProgress, DatasetManager, PathUtil


class HtmlParser:
    def __init__(self, selector, folder):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.cleaner = Cleaner()
        self.selector = selector
        self.rootpath = PathUtil.build_path('output', 'unsupervised', folder)

    def execute(self):
        self.work_progress.show('Staring html parser')
        filepaths = PathUtil.get_files(self.rootpath, '*.html')
        for filepath in filepaths:
            self.work_progress.show(f'Parsing {filepath}')
            content = self.dataset_manager.to_text(filepath)
            paragraphs = self.selector.get_text(content)
            paragraphs = self.cleaner.clear(paragraphs)
            output_filepath = self.get_output_filepath(filepath)
            self.dataset_manager.to_file(output_filepath, paragraphs)
            self.work_progress.show(f'File created in {output_filepath}')
        self.work_progress.show('Html parser has finished!')

    @staticmethod
    def get_output_filepath(source_filepath):
        part = source_filepath.split('.', maxsplit=1)[0]
        return f'{part}.txt'


class Cleaner:
    @staticmethod
    def clear(paragraphs):
        paragraphs = [re.sub(r'[\n\t●]', '', paragraph) for paragraph in paragraphs]
        paragraphs = [re.sub(r'\s+', ' ', paragraph) for paragraph in paragraphs]
        paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
        return paragraphs


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
