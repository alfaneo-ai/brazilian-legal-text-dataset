import pandas as pd

from pipeline.utils import WorkProgress, DatasetManager, PathUtil, correct_spelling


class QueyExporter:
    TEXT_FIELD = 'ementa'
    ID_FIELD = 'titulo'
    GROUP_FIELDS = ['area', 'tema', 'discussao']
    SOURCE_FILENAME = 'pesquisas-prontas-stf.csv'
    HEADER = {'query_id': [], 'query_text': [], 'doc_id': [], 'doc_text': [], 'relevant': []}

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.annotated_dataset = None
        self.query_dataset = pd.DataFrame(self.HEADER)

    def execute(self):
        self.work_progress.show('Preparing dataset for Query')
        self._read_annotated_dataset()
        self._prepare_query_pairs()
        self.work_progress.show('Query dataset has finished!')

    def _read_annotated_dataset(self):
        self.work_progress.show('Reading annotated dataset')
        annotated_filepath = PathUtil.build_path('resources', self.SOURCE_FILENAME)
        self.annotated_dataset = self.dataset_manager.from_csv(annotated_filepath)

    def _prepare_query_pairs(self):
        self.work_progress.show('Preparing query pairs')
        groups = self.annotated_dataset.groupby(self.GROUP_FIELDS)
        for group_name, group in groups:
            if group.shape[0] < 20:
                queries = group.sample(frac=0.20)
            else:
                queries = group.sample(frac=0.05)
            self.work_progress.show(f'Preparing group {group_name} with {queries.shape[0]} rows')
            for qindex, query_row in queries.iterrows():
                self.query_dataset = pd.DataFrame(self.HEADER)

                query_id = query_row['titulo']
                query_text = query_row['ementa']
                area = query_row['area']
                tema = query_row['tema']
                discussao = query_row['discussao']
                self.work_progress.show('')
                self.work_progress.show(f'Query id: {query_id} - {qindex}/{self.annotated_dataset.shape[0]}')

                relevant_query = f'area=="{area}" & tema=="{tema}" & discussao=="{discussao}" '
                relevants = self.annotated_dataset.query(relevant_query)
                self.work_progress.show(f'\tRelevants: {relevants.shape[0]}')
                for rindex, relevant_row in relevants.iterrows():
                    doc_id = relevant_row['titulo']
                    doc_text = relevant_row['ementa']
                    if doc_id != query_id:
                        item = self._create_item(query_id, query_text, doc_id, doc_text, relevant=1)
                        self.query_dataset = self.query_dataset.append(item, ignore_index=True)

                nonrelevant_query = f'area!="{area}" | tema!="{tema}" | discussao!="{discussao}" '
                nonrelevants = self.annotated_dataset.query(nonrelevant_query)
                self.work_progress.show(f'\tNon-Relevants: {nonrelevants.shape[0]}')
                for nrindex, nonrelevant_row in nonrelevants.iterrows():
                    doc_id = nonrelevant_row['titulo']
                    doc_text = nonrelevant_row['ementa']
                    item = self._create_item(query_id, query_text, doc_id, doc_text, relevant=0)
                    self.query_dataset = self.query_dataset.append(item, ignore_index=True)

                self._save_query_dataset(self.query_dataset, query_id)

    @staticmethod
    def _create_item(query_id, query_text, doc_id, doc_text, relevant):
        return {
            'query_id': query_id,
            'query_text': correct_spelling(query_text),
            'doc_id': doc_id,
            'doc_text': correct_spelling(doc_text),
            'relevant': relevant
        }

    def _save_query_dataset(self, dataset, name):
        filename =  f'{name}.csv'
        filepath = PathUtil.build_path('output', 'query', filename)
        self.dataset_manager.to_csv(dataset, filepath)
        self.work_progress.show(f'Dataset {filename} saved')
