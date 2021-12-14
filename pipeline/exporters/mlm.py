import os

from pipeline.utils import WorkProgress, DatasetManager, PathUtil


class MlmExporter:
    MINIMAL_TOKENS = 10
    MAX_TOKENS = 500

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.big_sentences_counter = 0
        self.bigger_sentences = []

    def execute(self):
        self.work_progress.show('Merging all text files')
        corpus_path = PathUtil.build_path('output', 'mlm')
        outfilepath = PathUtil.join(corpus_path, 'corpus.txt')
        if os.path.exists(outfilepath):
            os.remove(outfilepath)

        source_path = PathUtil.build_path('output', 'mlm')
        filepaths = PathUtil.get_files(source_path, '*.txt')
        outfile = open(outfilepath, 'wb')
        for filepath in filepaths:
            self._process_document(filepath, outfile)
        outfile.close()
        self.work_progress.show(f'{self.big_sentences_counter} sentences bigger than maximum')
        self.work_progress.show('Merging has finished!')

    def _process_document(self, infilepath, outfile):
        filename = PathUtil.get_filename(infilepath)
        self.work_progress.show(f'Merging {filename}')
        with open(infilepath, 'rb') as infile:
            lines = infile.readlines()
            lines = self._pre_textlines(lines)
            if len(lines) > 0:
                for line in lines:
                    outfile.write(f'{line}\n'.encode())
                outfile.write('\n'.encode())

    def _pre_textlines(self, textlines):
        result = []
        for line in textlines:
            line_str = line.decode('utf-8')
            line_str = line_str.strip()
            tokens = line_str.split()
            size = len(tokens)
            if size >= self.MINIMAL_TOKENS:
                result.append(line_str)
            if size > self.MAX_TOKENS:
                self.big_sentences_counter += 1
                self.bigger_sentences.append(line_str)
        return result
