import random
import re
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from pipeline.utils import DatasetManager, PathUtil, correct_spelling, TextUtil

TEXT_FIELD = 'ementa'


class EmentaParse:
    MINIMUM_LENGTH_FOR_SHUFFLE = 4

    def __init__(self):
        self.text_util = TextUtil()

    def clean_text(self, sentence):
        sentence = correct_spelling(sentence)
        sentence = self.text_util.remove_dashed_breaked_line(sentence)
        sentence = self.text_util.remove_breaking_lines(sentence)
        sentence = self.text_util.remove_tabs(sentence)
        sentence = self.text_util.remove_multiple_blank_spaces(sentence)
        sentence = self.text_util.remove_html_tags(sentence)
        sentence = self.text_util.remove_elipsis(sentence)
        sentence = self.text_util.remove_multiples_dots(sentence)
        sentence = self.text_util.remove_special_charset(sentence)
        return sentence

    @staticmethod
    def split_paragraphs(sentences):
        return re.split(r'\s\d\.\s', sentences)

    def should_shuffe_paragraphs(self, paragraphs):
        return len(paragraphs) >= self.MINIMUM_LENGTH_FOR_SHUFFLE

    @staticmethod
    def shuffe_paragraphs(paragraphs):
        first = paragraphs.pop(0)
        last = paragraphs.pop(-1)
        random.shuffle(paragraphs)
        paragraphs.insert(0, first)
        paragraphs.append(last)
        new_sentence = ' '.join(paragraphs)
        return new_sentence


class StsDataset(ABC):
    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.samples = self.create_instance()
        self.ementa_parse = EmentaParse()

    @abstractmethod
    def create_instance(self):
        pass

    def read(self, filepath):
        return self.dataset_manager.from_csv(filepath)

    def save_full(self, root_dir, name):
        self._save(self.samples, root_dir, name)

    def save_splited(self, root_dir):
        train_samples, dev_samples = self._split_train()
        self._save(train_samples, root_dir, 'train.csv')
        self._save(dev_samples, root_dir, 'dev.csv')

    def _save(self, dataset, root_dir, filename):
        base_path = PathUtil.build_path('output', 'sts', root_dir)
        Path(base_path).mkdir(parents=True, exist_ok=True)
        filepath = PathUtil.join(base_path, filename)
        self.dataset_manager.to_csv(dataset, filepath)
        print(f'{filename} - {len(dataset)}')
        return filepath

    def _split_train(self):
        train_samples, dev_samples = train_test_split(self.samples, train_size=0.80, test_size=0.20,
                                                      random_state=103, shuffle=True)
        train_samples = train_samples.reset_index(drop=True)
        dev_samples = dev_samples.reset_index(drop=True)
        return train_samples, dev_samples


class TripletStsDataset(StsDataset):
    HEADER = {'ementa1': [], 'ementa2': [], 'ementa3': []}

    def create_instance(self):
        return pd.DataFrame(self.HEADER)

    def add_sample(self, base, similar, unsimilar):
        item = {
            'ementa1': correct_spelling(base[TEXT_FIELD]),
            'ementa2': correct_spelling(similar[TEXT_FIELD]),
            'ementa3': correct_spelling(unsimilar[TEXT_FIELD])
        }
        self.samples = self.samples.append(item, ignore_index=True)


class ScaleStsDataset(StsDataset):
    HEADER = {'ementa1': [], 'ementa2': [], 'similarity': []}

    def create_instance(self):
        return pd.DataFrame(self.HEADER)

    def add_sample(self, sentence1, sentence2, similarity):
        item = {
            'ementa1': correct_spelling(sentence1[TEXT_FIELD]),
            'ementa2': correct_spelling(sentence2[TEXT_FIELD]),
            'similarity': similarity
        }
        self.samples = self.samples.append(item, ignore_index=True)


class BinaryStsDataset(StsDataset):
    HEADER = {'ementa1': [], 'ementa2': [], 'similarity': []}

    def create_instance(self):
        return pd.DataFrame(self.HEADER)

    def add_sample(self, base, similar, unsimilar):
        ementa1 = self.ementa_parse.clean_text(base[TEXT_FIELD])
        ementa2 = self.ementa_parse.clean_text(similar[TEXT_FIELD])
        ementa3 = self.ementa_parse.clean_text(unsimilar[TEXT_FIELD])
        self._add_single_sample(ementa1, ementa2, 1)
        self._add_single_sample(ementa1, ementa3, 0)

        paragraphs = self.ementa_parse.split_paragraphs(ementa1)
        if self.ementa_parse.should_shuffe_paragraphs(paragraphs):
            shuffled = self.ementa_parse.shuffe_paragraphs(paragraphs)
            self._add_single_sample(shuffled, ementa2, 1)
            self._add_single_sample(shuffled, ementa3, 0)

        paragraphs = self.ementa_parse.split_paragraphs(ementa2)
        if self.ementa_parse.should_shuffe_paragraphs(paragraphs):
            shuffled = self.ementa_parse.shuffe_paragraphs(paragraphs)
            self._add_single_sample(ementa1, shuffled, 1)

        paragraphs = self.ementa_parse.split_paragraphs(ementa3)
        if self.ementa_parse.should_shuffe_paragraphs(paragraphs):
            shuffled = self.ementa_parse.shuffe_paragraphs(paragraphs)
            self._add_single_sample(ementa1, shuffled, 0)

    def _add_single_sample(self, ementa1, ementa2, similarity):
        item = {
            'ementa1': ementa1,
            'ementa2': ementa2,
            'similarity': similarity
        }
        self.samples = self.samples.append(item, ignore_index=True)


class BenchmarkStsDataset(StsDataset):
    HEADER = {'source': [], 'group': [], 'ementa1': [], 'ementa2': [], 'similarity': []}

    def create_instance(self):
        return pd.DataFrame(self.HEADER)

    def add_sample(self, source_name, group_name, sentence1, sentence2, similarity):
        item = {
            'source': source_name,
            'group': group_name,
            'ementa1': correct_spelling(str(sentence1[TEXT_FIELD])),
            'ementa2': correct_spelling(str(sentence2[TEXT_FIELD])),
            'similarity': similarity
        }
        self.samples = self.samples.append(item, ignore_index=True)


class BatchTripletStsDataset(StsDataset):
    HEADER = {'ementa1': [], 'group': []}

    def create_instance(self):
        return pd.DataFrame(self.HEADER)

    def add_sample(self, base, group):
        ementa1 = self.ementa_parse.clean_text(base[TEXT_FIELD])
        self._add_single_sample(ementa1, group)

        paragraphs = self.ementa_parse.split_paragraphs(ementa1)
        if self.ementa_parse.should_shuffe_paragraphs(paragraphs):
            shuffled = self.ementa_parse.shuffe_paragraphs(paragraphs)
            self._add_single_sample(shuffled, group)

    def _add_single_sample(self, ementa1, group):
        item = {
            'ementa1': ementa1,
            'group': int(group)
        }
        self.samples = self.samples.append(item, ignore_index=True)
