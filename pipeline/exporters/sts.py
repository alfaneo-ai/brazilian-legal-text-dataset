import random
from itertools import combinations

from more_itertools import pairwise, zip_offset

from pipeline.utils import WorkProgress, PathUtil
from .datasets import *

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

    def reset(self):
        self.last_rows = 0


class BenchmarkStsExporter:
    GROUP_FIELD = 'assunto'
    SOURCE_FILENAMES = {'TJMS': 'pesquisas-prontas-tjms.csv',
                        'PJERJ': 'pesquisas-prontas-pjerj.csv'}

    def __init__(self):
        self.progress = Progress()
        self.sts_dataset = None
        self.source_dataset = None

    def execute(self):
        self.progress.start_process()
        for source_name in self.SOURCE_FILENAMES.keys():
            self._create_new_sts_dataset()
            self._read_annotated_dataset(source_name)
            self._match_similar_sentences(source_name)
            self._match_unsimilar_sentences(source_name)
            self._save_results(source_name)
        self.progress.finish_process()

    def _create_new_sts_dataset(self):
        self.sts_dataset = BenchmarkStsDataset()
        self.progress.reset()

    def _read_annotated_dataset(self, source_name):
        filename = self.SOURCE_FILENAMES[source_name]
        filepath = PathUtil.build_path('resources', filename)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _match_similar_sentences(self, source_name):
        self.progress.section_header(f'SOURCE: {source_name} - SIMILAR SENTENCES')
        groups = self.source_dataset.groupby(self.GROUP_FIELD)
        for group_name, group in groups:
            pairs = list(combinations(group.index, 2))
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
            random_ids = random.choices(list(diff_group.index), k=5)
            unsimilars = [self.source_dataset.loc[random_id] for random_id in random_ids]
            for unsimilar in unsimilars:
                self.sts_dataset.add_sample(source_name, group_name, sentence1, unsimilar, similarity=0)
        self.progress.section_footer(self.sts_dataset.samples)

    def _save_results(self, source_name):
        self.sts_dataset.save_full('benchmark', f'{source_name}.csv')


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
        self._read_annotated_dataset('pesquisas-prontas-stf.csv')
        self._process_diff_area_sentences()
        self._read_annotated_dataset('pesquisas-prontas-stj.csv')
        self._process_diff_assunto_sentences()
        self._save_results()
        self.progress.finish_process()

    def _read_annotated_dataset(self, source_name):
        filepath = PathUtil.build_path('resources', source_name)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _process_diff_area_sentences(self):
        self.progress.section_header('START STF GENERATION')
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
        # pairs = list(combinations(indexes, 2) if len(indexes) < 30 else pairwise(indexes))
        pairs = list(pairwise(indexes))
        for pair in pairs:
            base = discussion.loc[pair[0]]
            similar = discussion.loc[pair[1]]
            ramdom_id = random.choices(list(antagonic_area.index))[0]
            unsimilar = self.source_dataset.loc[ramdom_id]
            self.sts_dataset.add_sample(base, similar, unsimilar)
        self.progress.show(f'Itens: {len(discussion)}, Pairs: {len(pairs)}, Discussion: "{discussion_name}"')

    def _process_diff_assunto_sentences(self):
        self.progress.section_header('START STJ GENERATION')
        assuntos = self.source_dataset.groupby(['assunto'])
        for assunto_name, assunto in assuntos:
            diff_group = self.source_dataset.query(f'assunto != "{assunto_name}"')
            pairs = list(pairwise(assunto.index))
            for pair in pairs:
                base = assunto.loc[pair[0]]
                similar = assunto.loc[pair[1]]
                random_id = random.choices(list(diff_group.index), k=1)[0]
                unsimilar = self.source_dataset.loc[random_id]
                self.sts_dataset.add_sample(base, similar, unsimilar)
        self.progress.section_footer(self.sts_dataset.samples)

    def _save_results(self):
        self.sts_dataset.save_splited(self.output_folder)
        self.progress.section_footer(self.sts_dataset.samples)


class BatchTripletStsExporter:
    def __init__(self):
        self.progress = Progress()
        self.output_folder = 'batch_triplet'
        self.sts_dataset = BatchTripletStsDataset()
        self.source_dataset = None
        self.group_index = 1

    def execute(self):
        self.progress.start_process()
        self._read_annotated_dataset('pesquisas-prontas-stf.csv')
        self._process_stf_sentences()
        self._read_annotated_dataset('pesquisas-prontas-stj.csv')
        self._process_stj_sentences()
        self._save_results()
        self.progress.finish_process()

    def _read_annotated_dataset(self, source_name):
        filepath = PathUtil.build_path('resources', source_name)
        self.source_dataset = self.sts_dataset.read(filepath)

    def _process_stf_sentences(self):
        self.progress.section_header('START STF GENERATION')
        discussions = self.source_dataset.groupby(['discussao'])
        for index, (discussion_name, discussion) in enumerate(discussions, start=self.group_index):
            for row_id in list(discussion.index):
                row = self.source_dataset.loc[row_id]
                self.sts_dataset.add_sample(row, index)
        self.group_index = index
        self.progress.section_footer(self.sts_dataset.samples)

    def _process_stj_sentences(self):
        self.progress.section_header('START STJ GENERATION')
        discussions = self.source_dataset.groupby(['assunto'])
        for index, (discussion_name, discussion) in enumerate(discussions, start=self.group_index):
            for row_id in list(discussion.index):
                row = self.source_dataset.loc[row_id]
                self.sts_dataset.add_sample(row, index)
        self.progress.section_footer(self.sts_dataset.samples)

    def _save_results(self):
        self.sts_dataset.save_splited(self.output_folder)
        self.progress.section_footer(self.sts_dataset.samples)
