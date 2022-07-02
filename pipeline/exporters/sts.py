import random
from abc import ABC, abstractmethod
from itertools import combinations
from pathlib import Path

import pandas as pd
from more_itertools import pairwise, zip_offset
from sklearn.model_selection import train_test_split

from pipeline.utils import WorkProgress, DatasetManager, PathUtil, correct_spelling

TEXT_FIELD = 'ementa'
GROUP_FIELDS = ['area', 'tema', 'discussao']
FILENAME = 'pesquisas-prontas-stf.csv'
ANTAGONIC_AREAS = {
    'Direito Administrativo': 'Direito Processual Penal',
    'Direito Constitucional': 'Direito Processual Penal',
    'Direito Eleitoral': 'Direito Previdenciário',
    'Direito Penal': 'Direito Processual Civil',
    'Direito Previdenciário': 'Direito Eleitoral',
    'Direito Processual Civil': 'Direito Penal',
    'Direito Processual Penal': 'Direito Processual Civil',
    'Direito Tributário': 'Direito Processual Penal'
}


class BenchmarkStsExporter:
    GROUP_FIELD = 'assunto'
    SOURCE_FILENAMES = {'TJMS': 'pesquisas-prontas-tjms.csv',
                        'STJ': 'pesquisas-prontas-stj.csv',
                        'PJERJ': 'pesquisas-prontas-pjerj.csv'}

    def __init__(self):
        self.progress = Progress()
        self.sts_dataset = BenchmarkStsDataset()
        self.source_dataset = None

    def execute(self):
        self.progress.start_process()
        for source_name in self.SOURCE_FILENAMES.keys():
            self._read_annotated_dataset(source_name)
            self._match_similar_sentences(source_name)
            self._match_unsimilar_sentences(source_name)
        self._save_results()
        self.progress.finish_process()

    def _read_annotated_dataset(self, source_name):
        filename = self.SOURCE_FILENAMES[source_name]
        filepath = PathUtil.build_path('resources', filename)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _match_similar_sentences(self, source_name):
        self.progress.section_header(f'SOURCE: {source_name} - SIMILAR SENTENCES')
        groups = self.source_dataset.groupby(self.GROUP_FIELD)
        for group_name, group in groups:
            pairs = list(pairwise(group.index))
            for pair in pairs:
                sentence1 = group.loc[pair[0]]
                sentence2 = group.loc[pair[1]]
                self.sts_dataset.add_sample(source_name, group_name, sentence1, sentence2, similarity=1)
        self.progress.section_footer(self.sts_dataset.samples)

    def _match_unsimilar_sentences(self, source_name):
        self.progress.section_header(f'SOURCE: {source_name} - UNSIMILAR SENTENCES')
        for index, row in self.source_dataset.iterrows():
            sentence1 = row
            group_name = row[self.GROUP_FIELD]
            diff_group = self.source_dataset.query(f'{self.GROUP_FIELD} != "{group_name}"')
            sentence2 = diff_group.sample(n=1, axis=0)
            self.sts_dataset.add_sample(source_name, group_name, sentence1, sentence2, similarity=0)
        self.progress.section_footer(self.sts_dataset.samples)

    def _save_results(self):
        self.sts_dataset.save_full('benchmark')


class ScaleStsExporter:

    def __init__(self):
        self.progress = Progress()
        self.sts_dataset = ScaleStsDataset()
        self.source_dataset = None

    def execute(self):
        self.progress.start_process()
        self._read_annotated_dataset()
        self._process_same_discussion_sentences()
        self._process_same_theme_sentences()
        self._process_same_area_sentences()
        self._process_diff_area_sentences()
        self._save_results()
        self.progress.finish_process()

    def _read_annotated_dataset(self):
        filepath = PathUtil.build_path('resources', FILENAME)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _process_same_discussion_sentences(self):
        self.progress.section_header('1) SAME DISCUSSION AND DIFFERENT EMENTAS')
        discussion = self.source_dataset.groupby(['area', 'tema', 'discussao'])
        for discussion_name, discussion in discussion:
            self.progress.show(f'\t"{discussion_name[2]}" with {len(discussion)} itens')
            pairs = list(pairwise(discussion.index))
            for pair in pairs:
                sentence1 = discussion.loc[pair[0]]
                sentence2 = discussion.loc[pair[1]]
                self.sts_dataset.add_sample(sentence1, sentence2, similarity=3)
        self.progress.section_footer(self.sts_dataset.samples)

    def _process_same_theme_sentences(self):
        self.progress.section_header('2) SAME THEME AND DIFFERENT DISCUSSION')
        areas = self.source_dataset.groupby(['area'])
        for area_name, area in areas:
            self.progress.show('')
            self.progress.show(f'AREA: {area_name}')
            themes = area.groupby(['tema'])
            for theme_name, theme in themes:
                self.progress.show(f'TEMA: {theme_name}')
                discussions = theme.groupby(['discussao'])
                discussions_pairs = list(pairwise(discussions))
                self._add_group_pairs(discussions_pairs, similarity=2)
        self.progress.section_footer(self.sts_dataset.samples)

    def _process_same_area_sentences(self):
        self.progress.section_header('3) SAME AREA AND DIFFERENT THEMES')
        areas = self.source_dataset.groupby(['area'])
        for area_name, area in areas:
            themes = area.groupby(['tema'])
            if len(themes) > 1:
                self.progress.show('')
                self.progress.show(f'AREA: {area_name}')
                themes_pairs = list(pairwise(themes))
                self._add_group_pairs(themes_pairs, similarity=1)
        self.progress.section_footer(self.sts_dataset.samples)

    def _process_diff_area_sentences(self):
        self.progress.section_header('4) ANTAGONIC AREAS')
        areas = self.source_dataset.groupby(['area'])
        groups = {key: (key, group) for key, group in areas}
        areas_pairs = [((area_name, area), self._get_antagonic_area(groups, area_name)) for area_name, area in areas]
        self._add_group_pairs(areas_pairs, similarity=0)
        self.progress.section_footer(self.sts_dataset.samples)

    @staticmethod
    def _get_antagonic_area(area_groups, area_name):
        return area_groups[ANTAGONIC_AREAS[area_name]]

    def _add_group_pairs(self, group_pairs, similarity):
        for group_pair in group_pairs:
            group_name1 = group_pair[0][0]
            group_itens1 = group_pair[0][1]
            group_name2 = group_pair[1][0]
            group_itens2 = group_pair[1][1]
            self.progress.show(f'\t "{group_name1}" X "{group_name2}"')
            group_pairs = list(
                zip_offset(group_itens1.index, group_itens2.index, offsets=(0, 1), longest=False))
            for pair in group_pairs:
                sentence1 = group_itens1.loc[pair[0]]
                sentence2 = group_itens2.loc[pair[1]]
                self.sts_dataset.add_sample(sentence1, sentence2, similarity=similarity)

    def _save_results(self):
        self.sts_dataset.save_splited('scale')


class TripletAndBinaryStsExporter:
    def __init__(self, is_triplet=True):
        self.progress = Progress()
        self.output_folder = 'triplet' if is_triplet else 'binary'
        self.sts_dataset = TripletStsDataset() if is_triplet else BinaryStsDataset()
        self.source_dataset = None

    def execute(self):
        self.progress.start_process()
        self._read_annotated_dataset()
        self._process_diff_area_sentences()
        self._save_results()
        self.progress.finish_process()

    def _read_annotated_dataset(self):
        filepath = PathUtil.build_path('resources', FILENAME)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _process_diff_area_sentences(self):
        self.progress.section_header('START TRIPLET GENERATION')
        areas = self.source_dataset.groupby(['area'])
        groups = {key: group for key, group in areas}
        for area_name, area in areas:
            antagonic_area_name = ANTAGONIC_AREAS[area_name]
            antagonic_area = groups[antagonic_area_name]
            discussion = area.groupby(['discussao'])
            for discussion_name, discussion in discussion:
                self._create_discussion_samples(antagonic_area, discussion, discussion_name)
        self.progress.section_footer(self.sts_dataset.samples)

    def _create_discussion_samples(self, antagonic_area, discussion, discussion_name):
        indexes = discussion.index
        pairs = list(combinations(indexes, 2) if len(indexes) < 30 else pairwise(indexes))
        for pair in pairs:
            base = discussion.loc[pair[0]]
            similar = discussion.loc[pair[1]]
            ramdom_id = random.choices(list(antagonic_area.index))[0]
            unsimilar = self.source_dataset.loc[ramdom_id]
            self.sts_dataset.add_sample(base, similar, unsimilar)
        self.progress.show(f'Itens: {len(discussion)}, Pairs: {len(pairs)}, Discussion: "{discussion_name}"')

    def _save_results(self):
        self.sts_dataset.save_splited(self.output_folder)


class Progress:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.last_rows = 0

    def show(self, msg):
        self.work_progress.show(msg)

    def start_process(self):
        self.work_progress.show('Starting generation scale STS dataset')

    def finish_process(self):
        self.work_progress.show('Generation scale STS dataset has finished!')

    def section_header(self, msg):
        self.work_progress.show(100 * '-')
        self.work_progress.show(msg)
        self.work_progress.show(100 * '-')

    def section_footer(self, dataset):
        increment = len(dataset) - self.last_rows
        self.work_progress.show(f'')
        self.work_progress.show(f'Step add more {increment} rows')
        self.work_progress.show('')
        self.last_rows = len(dataset)


class StsDataset(ABC):
    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.samples = self.create_instance()

    @abstractmethod
    def create_instance(self):
        pass

    def read(self, filepath):
        return self.dataset_manager.from_csv(filepath)

    def save_full(self, root_dir):
        self._save(self.samples, root_dir, 'full.csv')

    def save_splited(self, root_dir):
        train_samples, dev_samples, test_samples = self._split_train()
        self._save(train_samples, root_dir, 'train.csv')
        self._save(dev_samples, root_dir, 'dev.csv')
        self._save(test_samples, root_dir, 'test.csv')

    def _save(self, dataset, root_dir, filename):
        base_path = PathUtil.build_path('output', 'sts', root_dir)
        Path(base_path).mkdir(parents=True, exist_ok=True)
        filepath = PathUtil.join(base_path, filename)
        self.dataset_manager.to_csv(dataset, filepath)

    def _split_train(self):
        train_samples, alltest_samples = train_test_split(self.samples,
                                                          train_size=0.70,
                                                          test_size=0.30,
                                                          random_state=103,
                                                          shuffle=True)
        dev_samples, test_samples = train_test_split(alltest_samples,
                                                     train_size=0.25,
                                                     test_size=0.75,
                                                     random_state=99,
                                                     shuffle=True)
        train_samples = train_samples.reset_index(drop=True)
        dev_samples = dev_samples.reset_index(drop=True)
        test_samples = test_samples.reset_index(drop=True)
        return train_samples, dev_samples, test_samples


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
        item_similar = {
            'ementa1': correct_spelling(base[TEXT_FIELD]),
            'ementa2': correct_spelling(similar[TEXT_FIELD]),
            'similarity': 1
        }
        item_unsimilar = {
            'ementa1': correct_spelling(base[TEXT_FIELD]),
            'ementa2': correct_spelling(unsimilar[TEXT_FIELD]),
            'similarity': 0
        }
        self.samples = self.samples.append(item_similar, ignore_index=True)
        self.samples = self.samples.append(item_unsimilar, ignore_index=True)


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
