import re

import pandas as pd
from more_itertools import pairwise, zip_offset
from sklearn.model_selection import train_test_split

from pipeline.utils import WorkProgress, DatasetManager, PathUtil


def correct_spelling(text):
    text = re.sub(r'E\sM\sE\sN\sT\sA[\s\.-–]', 'EMENTA ', text).strip()
    return re.sub(r'A\sC\sÓ\sR\sD\sÃ\sO', 'ACÓRDÃO', text)


def split_train_test(dataset):
    train_samples, test_samples = train_test_split(dataset, train_size=0.80, test_size=0.20, random_state=103,
                                                   shuffle=True)
    return train_samples, test_samples


class StsExporter:
    HEADER = {'assunto': [], 'id1': [], 'ementa1': [], 'id2': [], 'ementa2': [], 'similarity': []}

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.annotated_dataset = None
        self.sts_dataset = pd.DataFrame(self.HEADER)

    def execute(self):
        self.work_progress.show('Preparing dataset for STS')
        self._read_annotated_dataset()
        self._match_similar_sentences()
        self._match_unsimilar_sentences()
        train_dataset, dev_dataset = self._split_dataset()
        self._save_sts_datasets(train_dataset, dev_dataset)
        self.work_progress.show('STS dataset has finished!')

    def _read_annotated_dataset(self):
        self.work_progress.show('Reading annotated dataset')
        annotated_filepath = PathUtil.build_path('resources', 'annotated-queries.csv')
        self.annotated_dataset = self.dataset_manager.from_csv(annotated_filepath)

    def _match_similar_sentences(self):
        self.work_progress.show('Match similar sentences')
        groups = self.annotated_dataset.groupby('assunto')
        for group_name, group in groups:
            self.work_progress.show(f'Processing group {group_name} with {len(group)} itens')
            pairs = list(pairwise(group.index))
            for pair in pairs:
                sentence1 = group.loc[pair[0]]
                sentence2 = group.loc[pair[1]]
                item = self._create_item(sentence1, sentence2, similarity=1)
                self.sts_dataset = self.sts_dataset.append(item, ignore_index=True)

    def _match_unsimilar_sentences(self):
        self.work_progress.show('Match unsimilar sentences')
        groups = self.annotated_dataset.groupby('assunto')
        group_pairs = list(pairwise(groups))
        for group_pair in group_pairs:
            group1_name = group_pair[0][0]
            group1_data = group_pair[0][1]
            group2_name = group_pair[1][0]
            group2_data = group_pair[1][1]
            self.work_progress.show(f'{group1_name} X {group2_name} ')
            sentence_pairs = list(zip(group1_data.index, group2_data.index))
            for pair in sentence_pairs:
                sentence1 = group1_data.loc[pair[0]]
                sentence2 = group2_data.loc[pair[1]]
                item = self._create_item(sentence1, sentence2, similarity=0)
                self.sts_dataset = self.sts_dataset.append(item, ignore_index=True)
            sentence_pairs = list(zip_offset(group1_data.index, group2_data.index, offsets=(0, 1), longest=False))
            for pair in sentence_pairs:
                sentence1 = group1_data.loc[pair[0]]
                sentence2 = group2_data.loc[pair[1]]
                item = self._create_item(sentence1, sentence2, similarity=0)
                self.sts_dataset = self.sts_dataset.append(item, ignore_index=True)

    @staticmethod
    def _create_item(sentence1, sentence2, similarity):
        return {
            'assunto': sentence1['assunto'],
            'id1': sentence1['acordao_id'],
            'ementa1': correct_spelling(sentence1['ementa']),
            'id2': sentence2['acordao_id'],
            'ementa2': correct_spelling(sentence2['ementa']),
            'similarity': similarity
        }

    def _split_dataset(self):
        return split_train_test(self.sts_dataset)

    def _save_sts_datasets(self, train_dataset, dev_dataset):
        self.work_progress.show('Saving STS train and dev datasets')
        train_filepath = PathUtil.build_path('output', 'sts', 'train.csv')
        dev_filepath = PathUtil.build_path('output', 'sts', 'dev.csv')
        self.dataset_manager.to_csv(train_dataset, train_filepath)
        self.dataset_manager.to_csv(dev_dataset, dev_filepath)
