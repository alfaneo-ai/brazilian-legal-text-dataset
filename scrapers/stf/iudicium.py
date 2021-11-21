import requests
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from utils import WorkProgress, PathUtil

URLS = ['http://dadosabertos.c3sl.ufpr.br/acordaos/json/AcordaosRelatorios.json',
        'http://dadosabertos.c3sl.ufpr.br/acordaos/json/AcordaosVotos.json',
        'http://dadosabertos.c3sl.ufpr.br/acordaos/json/DocumentosAcordaos.json']


class StfIudiciumScraper:
    def __init__(self):
        self.work_progress = WorkProgress()

    def execute(self):
        self.work_progress.show('Starting scraper for Iudicium Dataset')
        basepath = PathUtil.build_path('output', 'unsupervised', 'stf')
        rootpath = PathUtil.create_dir(basepath, 'iudicium')
        for url in URLS:
            filename = url.split('/')[-1]
            filepath = PathUtil.join(rootpath, filename)
            self.download_large_file(url, filepath)
        self.work_progress.show('Scraper has finished!')

    @staticmethod
    def download_large_file(url, filepath):
        chunk_size: int = 4096
        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            with open(filepath, 'wb') as f:
                total_length = resp.headers.get('content-length')
                if total_length is None:
                    f.write(resp.content)
                else:
                    total_length = int(total_length)
                    downloaded_length = 0
                    with logging_redirect_tqdm():
                        with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=filepath,
                                  total=total_length) as pbar:
                            for data in resp.iter_content(chunk_size=chunk_size):
                                downloaded_length += len(data)
                                f.write(data)
                                f.flush()
                                pbar.update(len(data))


if __name__ == '__main__':
    scraper = IudiciumScraper()
    scraper.execute()
