import pandas as pd

from utils import WorkProgress, DatasetManager, PathUtil


class IudiciumParser:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.rootpath = PathUtil.build_path('output', 'unsupervised', 'stf', 'iudicium')

    def execute(self):
        self.work_progress.show('Staring iudicium parser')
        self._process_relatorio()
        self._process_votos()
        self._process_acordaos()
        self.work_progress.show('Iudicium parser has finished!')

    def _process_relatorio(self):
        self.work_progress.show(f'Parsing AcordaosRelatorios.json')
        input_filepath = PathUtil.join(self.rootpath, 'AcordaosRelatorios.json')
        output_filepath = PathUtil.join(self.rootpath, 'AcordaosRelatorios.txt')
        outfile = open(output_filepath, 'wb')
        with pd.read_json(input_filepath, lines=True, chunksize=10000) as file:
            for chunk in file:
                for line in chunk.texto:
                    outfile.write(f'{line}\n'.encode())
        outfile.close()

    def _process_votos(self):
        self.work_progress.show(f'Parsing AcordaosVotos.json')
        input_filepath = PathUtil.join(self.rootpath, 'AcordaosVotos.json')
        output_filepath = PathUtil.join(self.rootpath, 'AcordaosVotos.txt')
        outfile = open(output_filepath, 'wb')
        with pd.read_json(input_filepath, lines=True, chunksize=10000) as file:
            for chunk in file:
                for line in chunk.texto:
                    outfile.write(f'{line}\n'.encode())
        outfile.close()

    def _process_acordaos(self):
        self.work_progress.show(f'Parsing DocumentosAcordaos.json')
        input_filepath = PathUtil.join(self.rootpath, 'DocumentosAcordaos.json')
        output_filepath = PathUtil.join(self.rootpath, 'DocumentosAcordaos.txt')
        outfile = open(output_filepath, 'wb')
        with pd.read_json(input_filepath, lines=True, chunksize=10000) as file:
            for chunk in file:
                for ementa, acordao in zip(chunk.acordao, chunk.ementa):
                    line1 = ementa['texto']
                    line2 = acordao['texto']
                    outfile.write(f'{line1}\n'.encode())
                    outfile.write(f'{line2}\n'.encode())
        outfile.close()
