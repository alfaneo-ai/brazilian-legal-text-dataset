import re
import string
import unicodedata

from slugify import slugify as slugifylib


class TextUtil:
    @staticmethod
    def remove_whitespace(phrase):
        phrase = re.sub(fr'[{string.whitespace}]', ' ', phrase)
        phrase = TextUtil.remove_multiple_blank_spaces(phrase)
        return phrase

    @staticmethod
    def remove_dashed_breaked_line(phrase):
        return re.sub('-\n+', '', phrase)

    @staticmethod
    def remove_breaking_lines(phrase):
        phrase = re.sub('[\r\n]+', ' ', phrase)
        phrase = TextUtil.remove_multiple_blank_spaces(phrase)
        return phrase

    @staticmethod
    def remove_tabs(phrase):
        phrase = re.sub('[\t]+', ' ', phrase)
        phrase = TextUtil.remove_multiple_blank_spaces(phrase)
        return phrase

    @staticmethod
    def remove_multiple_blank_spaces(phrase):
        phrase = phrase.strip()
        phrase = re.sub(' +', ' ', phrase)
        return phrase

    @staticmethod
    def remove_all_blank_spaces(phrase):
        phrase = re.sub(' ', '', phrase)
        return phrase

    @staticmethod
    def remove_sentence(phrase, sentence):
        return re.sub(sentence, '', phrase)

    @staticmethod
    def remove_alphabetic_characters(phrase):
        return ''.join(filter(str.isdigit, phrase))

    @staticmethod
    def remove_html_tags(phrase):
        phrase = re.sub('<[^>]+>', ' ', phrase)
        return unicodedata.normalize('NFKD', phrase).strip()

    @staticmethod
    def remove_special_charset(phrase):
        return re.sub("", '', phrase)

    @staticmethod
    def convert_elipsis_to_code(phrase):
        return re.sub(r'\(\.\.\.\)', '__ELIPSIS__', phrase)

    @staticmethod
    def remove_multiples_under_line(phrase):
        return re.sub('_+', '', phrase)

    @staticmethod
    def remove_multiples_dots(phrase):
        return re.sub(r'\.\.+', '.', phrase.strip())

    @staticmethod
    def convert_code_to_elipsis(phrase):
        return re.sub('__ELIPSIS__', '(...)', phrase)

    @staticmethod
    def slugify(phrase):
        return slugifylib(phrase)
