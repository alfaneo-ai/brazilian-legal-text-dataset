import logging
import re

from nltk import tokenize

from pipeline.utils import TextUtil, PathUtil, DirectoryUtil, FileManager, PdfReader


class PdfParser:
    OUTPUT_DIR_PATH = 'output/mlm'
    PDF_EXTENSION = 'pdf'
    TXT_EXTENSION = 'txt'
    WORD_PER_SENTENCE_THRESHOLD = 10

    def __init__(self):
        self.rootpath = f'{self.OUTPUT_DIR_PATH}'
        self.pdf_reader = PdfReader(self.rootpath)
        self.directory_util = DirectoryUtil(self.OUTPUT_DIR_PATH)
        self.file_util = FileManager(self.OUTPUT_DIR_PATH)
        self.file_name_list = []
        self.current_extracted_text = None
        self.current_tokenized_sentence = None
        self.current_filepath = None
        self.total_sentences = 0
        self.total_words = 0

    def execute(self):
        self.__get_file_name_list()
        self.__log_number_of_files_found()
        for filepath in self.file_name_list:
            self.__create_txt_filename(filepath)
            if not self.__does_file_exists():
                self.__extract_text_from_file(filepath)
                self.__tokenize_text_by_sentences()
                self.__clean_sentences()
                self.__write_extracted_content()
                self.__log_succes_in_writing()
        self.__log_total_words_and_senteces_found()

    def __get_file_name_list(self):
        self.file_name_list = PathUtil.get_files(self.rootpath, f'*.{self.PDF_EXTENSION}')

    def __log_number_of_files_found(self):
        logging.info(f'Foram encontrados {len(self.file_name_list)} arquivos no diretório {self.rootpath}')

    def __create_txt_filename(self, file):
        self.current_filepath = re.sub(self.PDF_EXTENSION, self.TXT_EXTENSION, file)

    def __does_file_exists(self):
        return self.file_util.is_there_file(self.current_filepath)

    def __extract_text_from_file(self, file):
        self.current_extracted_text = self.pdf_reader.read(file)

    def __tokenize_text_by_sentences(self):
        self.current_extracted_text = tokenize.sent_tokenize(self.current_extracted_text, language='portuguese')

    def __clean_sentences(self):
        text_treated = []
        for sentence in self.current_extracted_text:
            self.__remove_unwanted_charset_from_sentence(sentence)
            if self.__is_sentence_over_threshold():
                text_treated.append(self.current_tokenized_sentence)
        self.total_sentences += len(text_treated)
        self.current_extracted_text = '\n'.join(text_treated)

    def __remove_unwanted_charset_from_sentence(self, sentence):
        sentence_without_dashed_breaked_lines = TextUtil.remove_dashed_breaked_line(sentence)
        sentence_without_breaking_lines = TextUtil.remove_breaking_lines(sentence_without_dashed_breaked_lines)
        sentence_without_tabs = TextUtil.remove_tabs(sentence_without_breaking_lines)
        sentence_without_blank_spaces = TextUtil.remove_multiple_blank_spaces(sentence_without_tabs)
        sentence_without_html_tags = TextUtil.remove_html_tags(sentence_without_blank_spaces)
        sentence_with_converted_elipsis = TextUtil.convert_elipsis_to_code(sentence_without_html_tags)
        sentence_without_multiples_dots = TextUtil.remove_multiples_dots(sentence_with_converted_elipsis)
        sentence_without_special_charset = TextUtil.remove_special_charset(sentence_without_multiples_dots)
        self.current_tokenized_sentence = TextUtil.convert_code_to_elipsis(sentence_without_special_charset)

    def __is_sentence_over_threshold(self):
        tokenized_sentence = tokenize.word_tokenize(self.current_tokenized_sentence.strip(), language='portuguese')
        self.total_words += len(tokenized_sentence)
        return len(tokenized_sentence) > self.WORD_PER_SENTENCE_THRESHOLD

    def __write_extracted_content(self):
        with open(self.current_filepath, 'w') as text:
            text.writelines(self.current_extracted_text)

    def __log_succes_in_writing(self):
        logging.info(f'O texto {self.current_filepath} foi escrito com sucesso')

    def __log_total_words_and_senteces_found(self):
        logging.info(f'Foram processadas {self.total_words} palavras em {self.total_sentences} sentenças')
