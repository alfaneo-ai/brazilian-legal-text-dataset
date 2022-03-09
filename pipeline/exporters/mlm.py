import os

from sklearn.model_selection import train_test_split

from pipeline.utils import WorkProgress, DatasetManager, PathUtil, Statistic


class MlmExporter:
    MINIMAL_TOKENS = 10

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.statistic = Statistic()
        self.corpus_path = PathUtil.build_path('output', 'mlm')

    def execute(self):
        self.work_progress.show('Merging all text files')
        sourcefiles = self._get_source_files()
        sentences = self._read_sentences(sourcefiles)
        self._show_statistics(sentences)
        train, dev = self._split_sentences(sentences)
        self._save_sentences(train, 'corpus_train.txt')
        self._save_sentences(dev, 'corpus_dev.txt')
        self.work_progress.show('Merging has finished!')

    @staticmethod
    def _get_source_files():
        source_path = PathUtil.build_path('output', 'mlm')
        filepaths = PathUtil.get_files(source_path, '*.txt')
        return filepaths

    def _read_sentences(self, sourcefiles):
        sentences = set()
        for filepath in sourcefiles:
            filename = PathUtil.get_filename(filepath)
            self.work_progress.show(f'Merging {filename}')
            with open(filepath, 'rb') as fileinput:
                lines = fileinput.readlines()
                self._add_sentences(lines, sentences)
        return sentences

    def _add_sentences(self, lines, sentences):
        for line in lines:
            linetext = line.decode('utf-8')
            linetext = linetext.strip()
            tokens = linetext.split()
            size = len(tokens)
            if size >= self.MINIMAL_TOKENS:
                sentences.add(linetext)

    def _show_statistics(self, sentences):
        statistics = self.statistic.calculate_sentences(sentences)
        self.work_progress.show(f'Up to 64: {statistics["64"][0]}% - {statistics["64"][1]} samples')
        self.work_progress.show(f'Up to 128: {statistics["128"][0]}% - {statistics["128"][1]} samples')
        self.work_progress.show(f'Up to 256: {statistics["256"][0]}% - {statistics["256"][1]} samples')
        self.work_progress.show(f'Up to 384: {statistics["384"][0]}% - {statistics["384"][1]} samples')
        self.work_progress.show(f'Up to 512: {statistics["512"][0]}% - {statistics["512"][1]} samples')
        self.work_progress.show(f'Up to 768: {statistics["768"][0]}% - {statistics["768"][1]} samples')
        self.work_progress.show(f'Up to 1024: {statistics["1024"][0]}% - {statistics["1024"][1]} samples')
        self.work_progress.show(f'Greate than 1024: {statistics["more"][0]}% - {statistics["more"][1]} samples')

    @staticmethod
    def _split_sentences(sentences):
        train_samples, dev_samples = train_test_split(list(sentences),
                                                      train_size=0.95,
                                                      test_size=0.05,
                                                      random_state=103,
                                                      shuffle=True)
        return train_samples, dev_samples

    def _save_sentences(self, sentences, filename):
        filepath = PathUtil.join(self.corpus_path, filename)
        self._remove_oldfile(filepath)
        outfile = open(filepath, 'wb')
        for sentence in sentences:
            outfile.write(f'{sentence}\n'.encode())
        outfile.close()

    @staticmethod
    def _remove_oldfile(filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
