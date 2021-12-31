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
    TEXT_FIELD = 'ementa'

    SHOULD_SPLIT = False
    # SHOULD_SPLIT = True

    ID_FIELD = 'titulo'
    # ID_FIELD = 'acordao_id'

    GROUP_FIELDS = ['area', 'tema', 'discussao']
    # GROUP_FIELDS = ['assunto']

    SOURCE_FILENAME = 'pesquisas-prontas-stf.csv'
    # SOURCE_FILENAME = 'annotated-queries.csv'

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
        if self.SHOULD_SPLIT:
            train_dataset, dev_dataset = self._split_dataset()
            self._save_sts_dataset(train_dataset, 'train')
            self._save_sts_dataset(dev_dataset, 'dev')
        else:
            self._save_sts_dataset(self.sts_dataset, 'eval')
        self.work_progress.show('STS dataset has finished!')

    def _read_annotated_dataset(self):
        self.work_progress.show('Reading annotated dataset')
        annotated_filepath = PathUtil.build_path('resources', self.SOURCE_FILENAME)
        self.annotated_dataset = self.dataset_manager.from_csv(annotated_filepath)

    def _match_similar_sentences(self):
        self.work_progress.show('Match similar sentences')
        groups = self.annotated_dataset.groupby(self.GROUP_FIELDS)
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
        groups = self.annotated_dataset.groupby(self.GROUP_FIELDS)
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

    def _create_item(self, sentence1, sentence2, similarity):
        key_group = sentence1[self.GROUP_FIELDS]
        key_group = '/'.join(key_group)
        return {
            'assunto': key_group,
            'id1': sentence1[self.ID_FIELD],
            'ementa1': correct_spelling(sentence1[self.TEXT_FIELD]),
            'id2': sentence2[self.ID_FIELD],
            'ementa2': correct_spelling(sentence2[self.TEXT_FIELD]),
            'similarity': similarity
        }

    def _split_dataset(self):
        return split_train_test(self.sts_dataset)

    def _save_sts_dataset(self, dataset, name):
        self.work_progress.show('Saving STS dataset')
        train_filepath = PathUtil.build_path('output', 'sts', f'{name}.csv')
        self.dataset_manager.to_csv(dataset, train_filepath)
