import pandas as pd
from more_itertools import pairwise, zip_offset
from sklearn.model_selection import train_test_split

from pipeline.utils import WorkProgress, DatasetManager, PathUtil, correct_spelling


class StsScaleExporter:
    TEXT_FIELD = 'ementa'
    GROUP_FIELDS = ['area', 'tema', 'discussao']
    FILENAME = 'pesquisas-prontas-stf.csv'

    def __init__(self):
        self.progress = Progress()
        self.sts_dataset = StsDataset()
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
        filepath = PathUtil.build_path('resources', self.FILENAME)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _process_same_discussion_sentences(self):
        self.progress.section_header('1) SAME DISCUSSION AND DIFFERENT EMENTAS')
        samples = self.sts_dataset.create_instance()
        discussion = self.source_dataset.groupby(['area', 'tema', 'discussao'])
        for discussion_name, discussion in discussion:
            self.progress.show(f'\t"{discussion_name[2]}" with {len(discussion)} itens')
            pairs = list(pairwise(discussion.index))
            for pair in pairs:
                sentence1 = discussion.loc[pair[0]]
                sentence2 = discussion.loc[pair[1]]
                samples = self._add_sample(samples, sentence1, sentence2, similarity=3)
        self.sts_dataset.accumulate(samples)
        self.progress.section_footer(samples)

    def _process_same_theme_sentences(self):
        self.progress.section_header('2) SAME THEME AND DIFFERENT DISCUSSION')
        samples = self.sts_dataset.create_instance()
        areas = self.source_dataset.groupby(['area'])
        for area_name, area in areas:
            self.progress.show('')
            self.progress.show(f'AREA: {area_name}')
            themes = area.groupby(['tema'])
            for theme_name, theme in themes:
                self.progress.show(f'TEMA: {theme_name}')
                discussions = theme.groupby(['discussao'])
                discussions_pairs = list(pairwise(discussions))
                samples = self._add_group_pairs(samples, discussions_pairs, similarity=2)
        self.sts_dataset.accumulate(samples)
        self.progress.section_footer(samples)

    def _process_same_area_sentences(self):
        self.progress.section_header('3) SAME AREA AND DIFFERENT THEMES')
        samples = self.sts_dataset.create_instance()
        areas = self.source_dataset.groupby(['area'])
        for area_name, area in areas:
            themes = area.groupby(['tema'])
            if len(themes) > 1:
                self.progress.show('')
                self.progress.show(f'AREA: {area_name}')
                themes_pairs = list(pairwise(themes))
                samples = self._add_group_pairs(samples, themes_pairs, similarity=1)
        self.sts_dataset.accumulate(samples)
        self.progress.section_footer(samples)

    def _process_diff_area_sentences(self):
        self.progress.section_header('4) DIFFERENT AREAS')
        samples = self.sts_dataset.create_instance()
        areas = self.source_dataset.groupby(['area'])
        areas_pairs = list(pairwise(areas))
        samples = self._add_group_pairs(samples, areas_pairs, similarity=0)
        self.sts_dataset.accumulate(samples)
        self.progress.section_footer(samples)

    def _add_group_pairs(self, dataset, group_pairs, similarity):
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
                dataset = self._add_sample(dataset, sentence1, sentence2, similarity=similarity)
        return dataset

    def _add_sample(self, samples, sentence1, sentence2, similarity):
        item = {
            'ementa1': correct_spelling(sentence1[self.TEXT_FIELD]),
            'ementa2': correct_spelling(sentence2[self.TEXT_FIELD]),
            'similarity': similarity
        }
        return samples.append(item, ignore_index=True)

    def _save_results(self):
        all_samples = self.sts_dataset.samples
        train_samples, eval_samples, test_samples = self.sts_dataset.split_train()
        self.sts_dataset.save(all_samples, 'full')
        self.sts_dataset.save(train_samples, 'train')
        self.sts_dataset.save(eval_samples, 'eval')
        self.sts_dataset.save(test_samples, 'test')


class Progress:
    def __init__(self):
        self.work_progress = WorkProgress()

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
        self.work_progress.show(f'')
        self.work_progress.show(f'Step has processed {len(dataset)} rows')
        self.work_progress.show('')
        self.work_progress.show('')
        self.work_progress.show('')


class StsDataset:
    HEADER = {'ementa1': [], 'ementa2': [], 'similarity': []}

    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.samples = pd.DataFrame(self.HEADER)

    def create_instance(self):
        return pd.DataFrame(self.HEADER)

    def accumulate(self, dataset):
        self.samples = self.samples.append(dataset, ignore_index=True)

    def split_train(self):
        train_samples, alltest_samples = train_test_split(self.samples,
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

    def read(self, filepath):
        return self.dataset_manager.from_csv(filepath)

    def save(self, dataset, name):
        train_filepath = PathUtil.build_path('output', 'sts', f'{name}.csv')
        self.dataset_manager.to_csv(dataset, train_filepath)
