from pipeline.utils import *


class Statistic:

    @staticmethod
    def calculate(sentences: list):
        total = len(sentences)
        less_than_32 = 0
        less_than_64 = 0
        less_than_128 = 0
        less_than_256 = 0
        less_than_384 = 0
        less_than_512 = 0
        less_than_768 = 0
        less_than_1024 = 0
        greater_than_1024 = 0
        for sent in sentences:
            tokens_length = len(sent.lower().split())
            if 0 < tokens_length <= 32:
                less_than_32 += 1
            elif 32 < tokens_length <= 64:
                less_than_64 += 1
            elif 64 < tokens_length <= 128:
                less_than_128 += 1
            elif 128 < tokens_length <= 256:
                less_than_256 += 1
            elif 256 < tokens_length <= 384:
                less_than_384 += 1
            elif 384 < tokens_length <= 512:
                less_than_512 += 1
            elif 512 < tokens_length <= 768:
                less_than_768 += 1
            elif 768 < tokens_length <= 1024:
                less_than_1024 += 1
            elif tokens_length > 1024:
                greater_than_1024 += 1

        less_than_32_percent = round((less_than_32 / total) * 100, 2)
        less_than_64_percent = round((less_than_64 / total) * 100, 2)
        less_than_128_percent = round((less_than_128 / total) * 100, 2)
        less_than_256_percent = round((less_than_256 / total) * 100, 2)
        less_than_384_percent = round((less_than_384 / total) * 100, 2)
        less_than_512_percent = round((less_than_512 / total) * 100, 2)
        less_than_768_percent = round((less_than_768 / total) * 100, 2)
        less_than_1024_percent = round((less_than_1024 / total) * 100, 2)
        greater_than_1024_percent = round((greater_than_1024 / total) * 100, 2)

        statics = {
            '32': (less_than_32_percent, less_than_32),
            '64': (less_than_64_percent, less_than_64),
            '128': (less_than_128_percent, less_than_128),
            '256': (less_than_256_percent, less_than_256),
            '384': (less_than_384_percent, less_than_384),
            '512': (less_than_512_percent, less_than_512),
            '768': (less_than_768_percent, less_than_768),
            '1024': (less_than_1024_percent, less_than_1024),
            'more': (greater_than_1024_percent, greater_than_1024)
        }

        return statics


class StatisticsForDatasets:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()

    def execute(self):
        self.work_progress.show('Starting a MLM pipeline')
        pjerj = self.dataset_manager.from_csv('resources/pesquisas-prontas-pjerj.csv')
        pjerj = pjerj['ementa'].tolist()

        stf = self.dataset_manager.from_csv('resources/pesquisas-prontas-stf.csv')
        stf = stf['ementa'].tolist()

        stj = self.dataset_manager.from_csv('resources/pesquisas-prontas-stj.csv')
        stj = stj['ementa'].tolist()

        tjms = self.dataset_manager.from_csv('resources/pesquisas-prontas-tjms.csv')
        tjms = tjms['ementa'].tolist()

        mlm = self._read_mlm_file()

        sentences = list(set(pjerj + stf + stj + tjms + mlm))
        statics = Statistic.calculate(sentences)
        print(statics)

        self.work_progress.show('MLM Pipeline has finished!')

    @staticmethod
    def _read_mlm_file():
        sentences = list()
        filepath = PathUtil.build_path('output/mlm/corpus_train.txt')
        with open(filepath, 'rb') as fileinput:
            lines = fileinput.readlines()
            for line in lines:
                linetext = line.decode('utf-8')
                sentences.append(linetext)
        return sentences


if __name__ == '__main__':
    StatisticsForDatasets().execute()
