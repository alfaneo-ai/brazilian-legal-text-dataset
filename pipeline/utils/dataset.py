import os

import pandas as pd


class DatasetManager:

    @staticmethod
    def from_csv(filepath):
        if not os.path.exists(filepath):
            raise RuntimeError(f'Not found file in {filepath}')
        return pd.read_csv(filepath, sep='|', encoding='utf-8-sig')

    @staticmethod
    def to_csv(dataset, filepath, index=False):
        if os.path.exists(filepath):
            os.remove(filepath)
        dataset = pd.DataFrame(dataset)
        dataset.to_csv(filepath, sep='|', encoding='utf-8-sig', index_label='index', index=index)

    @staticmethod
    def to_file(filepath, texts):
        textfile = open(filepath, 'w')
        if isinstance(texts, list):
            for element in texts:
                textfile.write(element + '\n')
        else:
            textfile.write(texts)
        textfile.close()

    @staticmethod
    def from_text(filepath):
        textfile = open(filepath, 'r')
        text = textfile.read()
        textfile.close()
        return text
