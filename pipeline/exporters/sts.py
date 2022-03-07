import pandas as pd
from more_itertools import pairwise, zip_offset
from sklearn.model_selection import train_test_split

from pipeline.utils import WorkProgress, DatasetManager, PathUtil, correct_spelling


class StsExporter:
    TEXT_FIELD = 'ementa'
    GROUP_FIELDS = [['assunto'], ['area', 'tema', 'discussao'], 'assunto', 'assunto']
    SOURCE_FILENAMES = ['pesquisas-prontas-tjms.csv', 'pesquisas-prontas-stf.csv', 'pesquisas-prontas-stj.csv', 'pesquisas-prontas-pjerj.csv']
    HEADER = {'assunto': [], 'ementa1': [], 'ementa2': [], 'similarity': []}

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.sts_dataset = pd.DataFrame(self.HEADER)

    def execute(self):
        self.work_progress.show('Preparing dataset for STS')
        for index, filename in enumerate(self.SOURCE_FILENAMES):
            dataset = self._read_annotated_dataset(filename)
            groups = self._get_groups_from_dataset(dataset, index)
            similar_dataset = self._match_similar_sentences(groups)
            unsimilar_dataset = self._match_unsimilar_sentences(groups)
            self._accumulate_dataset(similar_dataset)
            self._accumulate_dataset(unsimilar_dataset)
        self._print_summary(self.sts_dataset, 'total')
        self._save_sts_dataset(self.sts_dataset, 'full')
        train_dataset, dev_dataset, test_dataset = self._split_train_dataset()
        self._print_summary(train_dataset, 'train')
        self._save_sts_dataset(train_dataset, 'train')
        self._print_summary(dev_dataset, 'dev')
        self._save_sts_dataset(dev_dataset, 'dev')
        self._print_summary(test_dataset, 'test')
        self._save_sts_dataset(test_dataset, 'test')
        self.work_progress.show('STS dataset has finished!')

    def _read_annotated_dataset(self, filename):
        self.work_progress.show('Reading annotated dataset')
        annotated_filepath = PathUtil.build_path('resources', filename)
        return self.dataset_manager.from_csv(annotated_filepath)

    def _get_groups_from_dataset(self, annotated_dataset, index):
        group_fields = self.GROUP_FIELDS[index]
        return annotated_dataset.groupby(group_fields)

    def _match_similar_sentences(self, groups):
        self.work_progress.show('Match similar sentences')
        sts_dataset = pd.DataFrame(self.HEADER)
        for group_name, group in groups:
            self.work_progress.show(f'Processing group {group_name} with {len(group)} itens')
            pairs = list(pairwise(group.index))
            for pair in pairs:
                sentence1 = group.loc[pair[0]]
                sentence2 = group.loc[pair[1]]
                item = self._create_item(group_name, sentence1, sentence2, similarity=1)
                sts_dataset = sts_dataset.append(item, ignore_index=True)
        return sts_dataset

    def _match_unsimilar_sentences(self, groups):
        self.work_progress.show('Match unsimilar sentences')
        sts_dataset = pd.DataFrame(self.HEADER)
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
                item = self._create_item(group1_name, sentence1, sentence2, similarity=0)
                sts_dataset = sts_dataset.append(item, ignore_index=True)
            sentence_pairs = list(zip_offset(group1_data.index, group2_data.index, offsets=(0, 1), longest=False))
            for pair in sentence_pairs:
                sentence1 = group1_data.loc[pair[0]]
                sentence2 = group2_data.loc[pair[1]]
                item = self._create_item(group2_name, sentence1, sentence2, similarity=0)
                sts_dataset = sts_dataset.append(item, ignore_index=True)
        return sts_dataset

    def _create_item(self, keygroup, sentence1, sentence2, similarity):
        assunto = keygroup
        if type(keygroup) == tuple:
            assunto = ' '.join(keygroup)
        return {
            'assunto': assunto,
            'ementa1': correct_spelling(sentence1[self.TEXT_FIELD]),
            'ementa2': correct_spelling(sentence2[self.TEXT_FIELD]),
            'similarity': similarity
        }

    def _accumulate_dataset(self, dataset):
        self.sts_dataset = self.sts_dataset.append(dataset, ignore_index=True)

    def _split_train_dataset(self):
        train_samples, alltest_samples = train_test_split(self.sts_dataset,
                                                          train_size=0.70,
                                                          test_size=0.30,
                                                          random_state=103,
                                                          shuffle=True)
        eval_samples, test_samples = train_test_split(alltest_samples,
                                                      train_size=0.25,
                                                      test_size=0.75,
                                                      random_state=99,
                                                      shuffle=True)
        train_samples = train_samples.reset_index(drop=True)
        eval_samples = eval_samples.reset_index(drop=True)
        test_samples = test_samples.reset_index(drop=True)
        return train_samples, eval_samples, test_samples

    def _print_summary(self, dataset, name):
        self.work_progress.show(f'')
        self.work_progress.show(f'Dataset for {name}')
        self.work_progress.show(f'Rows {len(dataset)}')

    def _save_sts_dataset(self, dataset, name):
        train_filepath = PathUtil.build_path('output', 'sts', f'{name}.csv')
        self.work_progress.show(f'Saving STS dataset {train_filepath}')
        self.dataset_manager.to_csv(dataset, train_filepath)
