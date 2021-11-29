import re

import nltk
import nltk.tokenize as nltk_tokenize


class EmentaSegmentation:
    @staticmethod
    def split(text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'E M E N T A', 'EMENTA', text)
        text = re.sub(r'\s–\s', '. ', text)
        return re.split(r'\.\s\d\.\s', text)


class DefaultSegmentation:
    def __init__(self):
        nltk.download('punkt')

    @staticmethod
    def split(text):
        return nltk_tokenize.sent_tokenize(text)


if __name__ == '__main__':
    print('ola')
