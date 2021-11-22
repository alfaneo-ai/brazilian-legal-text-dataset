import pandas as pd

from utils import WorkProgress, DatasetManager, PathUtil


class IudiciumParser:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.rootpath = PathUtil.build_path('output', 'unsupervised', 'stf', 'iudicium')
        self.relatorio_path = None
        self.votos_path = None
        self.ementa_path = None
        self.acordao_path = None

    def execute(self):
        self.work_progress.show('Staring iudicium parser')
        self._create_output_folders()
        self._process_relatorio()
        self._process_votos()
        self._process_acordaos()
        self.work_progress.show('Iudicium parser has finished!')

    def _create_output_folders(self):
        self.relatorio_path = PathUtil.create_dir(self.rootpath, 'relatorio')
        self.votos_path = PathUtil.create_dir(self.rootpath, 'votos')
        self.ementa_path = PathUtil.create_dir(self.rootpath, 'ementa')
        self.acordao_path = PathUtil.create_dir(self.rootpath, 'acordao')

    def _process_relatorio(self):
        self.work_progress.show(f'Parsing AcordaosRelatorios.json')
        input_filepath = PathUtil.join(self.rootpath, 'AcordaosRelatorios.json')
        with pd.read_json(input_filepath, lines=True, chunksize=10000) as file:
            for chunk in file:
                for _id, texto in zip(chunk._id, chunk.texto):
                    oid = _id['$oid']
                    output_filepath = PathUtil.join(self.relatorio_path, f'{oid}.txt')
                    outfile = open(output_filepath, 'wb')
                    outfile.write(f'{texto}\n'.encode())
                    outfile.close()
                    self.work_progress.show(f'Created file: {output_filepath}')

    def _process_votos(self):
        self.work_progress.show(f'Parsing AcordaosVotos.json')
        input_filepath = PathUtil.join(self.rootpath, 'AcordaosVotos.json')
        with pd.read_json(input_filepath, lines=True, chunksize=10000) as file:
            for chunk in file:
                for _id, texto in zip(chunk._id, chunk.texto):
                    oid = _id['$oid']
                    output_filepath = PathUtil.join(self.votos_path, f'{oid}.txt')
                    outfile = open(output_filepath, 'wb')
                    outfile.write(f'{texto}\n'.encode())
                    outfile.close()
                    self.work_progress.show(f'Created file: {output_filepath}')

    def _process_acordaos(self):
        self.work_progress.show(f'Parsing DocumentosAcordaos.json')
        input_filepath = PathUtil.join(self.rootpath, 'DocumentosAcordaos.json')
        with pd.read_json(input_filepath, lines=True, chunksize=10000) as file:
            for chunk in file:
                for _id, ementa, acordao in zip(chunk._id, chunk.acordao, chunk.ementa):
                    oid = _id['$oid']
                    ementa_texto = ementa['texto']
                    output_filepath = PathUtil.join(self.ementa_path, f'{oid}.txt')
                    outfile = open(output_filepath, 'wb')
                    outfile.write(f'{ementa_texto}\n'.encode())
                    outfile.close()
                    self.work_progress.show(f'Created file: {output_filepath}')

                    acordao_texto = acordao['texto']
                    output_filepath = PathUtil.join(self.acordao_path, f'{oid}.txt')
                    outfile = open(output_filepath, 'wb')
                    outfile.write(f'{acordao_texto}\n'.encode())
                    outfile.close()
                    self.work_progress.show(f'Created file: {output_filepath}')
