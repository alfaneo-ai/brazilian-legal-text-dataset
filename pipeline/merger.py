from utils import WorkProgress, DatasetManager, PathUtil


class Merger:
    MINIMAL_TOKENS = 5

    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()

    def execute(self):
        self.work_progress.show('Merging all text files')
        corpus_path = PathUtil.build_path('output')
        outfilepath = PathUtil.join(corpus_path, 'corpus.txt')

        source_path = PathUtil.build_path('output', 'unsupervised')
        filepaths = PathUtil.get_files(source_path, '*.txt')
        outfile = open(outfilepath, 'wb')
        for filepath in filepaths:
            filename = PathUtil.get_filename(filepath)
            self.work_progress.show(f'Merging {filename}')
            with open(filepath, 'rb') as infile:
                lines = infile.readlines()
                lines = self.pre_process(lines)
                for line in lines:
                    outfile.write(f'{line}\n'.encode())
        outfile.close()
        self.work_progress.show('Merging has finished!')

    def pre_process(self, lines):
        result = []
        for line in lines:
            line_str = line.decode('utf-8')
            line_str = line_str.strip()
            tokens = line_str.split()
            if len(tokens) >= self.MINIMAL_TOKENS:
                result.append(line_str)
        return result
