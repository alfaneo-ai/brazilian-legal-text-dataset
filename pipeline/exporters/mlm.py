import os

from pipeline.utils import WorkProgress, DatasetManager, PathUtil, Statistic


class MlmExporter:
    MINIMAL_TOKENS = 10

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.big_sentences_counter = 0
        self.bigger_sentences = []
        self.lines_seen = set()
        self.statistic = Statistic()

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
        stats = self.statistic.calculate_textfile(outfilepath)
        self._show_statistics(stats)
        self.work_progress.show('Merging has finished!')

    def _process_document(self, infilepath, outfile):
        filename = PathUtil.get_filename(infilepath)
        self.work_progress.show(f'Merging {filename}')
        with open(infilepath, 'rb') as infile:
            lines = infile.readlines()
            lines = self._pre_textlines(lines)
            if len(lines) > 0:
                for line in lines:
                    if line not in self.lines_seen:
                        outfile.write(f'{line}\n'.encode())
                        self.lines_seen.add(line)
                # outfile.write('\n'.encode())

    def _pre_textlines(self, textlines):
        result = []
        for line in textlines:
            line_str = line.decode('utf-8')
            line_str = line_str.strip()
            tokens = line_str.split()
            size = len(tokens)
            if size >= self.MINIMAL_TOKENS:
                result.append(line_str)
        return result

    def _show_statistics(self, statistics):
        self.work_progress.show(f'Up to 64: {statistics["64"][0]}% - {statistics["64"][1]} samples')
        self.work_progress.show(f'Up to 128: {statistics["128"][0]}% - {statistics["128"][1]} samples')
        self.work_progress.show(f'Up to 256: {statistics["256"][0]}% - {statistics["256"][1]} samples')
        self.work_progress.show(f'Up to 384: {statistics["384"][0]}% - {statistics["384"][1]} samples')
        self.work_progress.show(f'Up to 512: {statistics["512"][0]}% - {statistics["512"][1]} samples')
        self.work_progress.show(f'Up to 768: {statistics["768"][0]}% - {statistics["768"][1]} samples')
        self.work_progress.show(f'Up to 1024: {statistics["1024"][0]}% - {statistics["1024"][1]} samples')
        self.work_progress.show(f'Greate than 1024: {statistics["more"][0]}% - {statistics["more"][1]} samples')