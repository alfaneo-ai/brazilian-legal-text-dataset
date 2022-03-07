from .exporters import mlm_exporter, sts_exporter, query_exporter
from .parsers import mlm_parsers, sts_parsers
from .scrapers import mlm_scrapers, sts_scrapers
from .utils import WorkProgress


class MlmPipelineManager:
    def __init__(self):
        self.work_progress = WorkProgress()

    def execute(self, task):
        self.work_progress.show('Starting a MLM pipeline')
        if task in ['all', 'scrap']:
            for scraper in mlm_scrapers:
                scraper.execute()
        if task in ['all', 'parse']:
            for parser in mlm_parsers:
                parser.execute()
        if task in ['all', 'export']:
            mlm_exporter.execute()
        self.work_progress.show('MLM Pipeline has finished!')


class StsPipelineManager:
    def __init__(self):
        self.work_progress = WorkProgress()

    def execute(self, task):
        self.work_progress.show('Starting a STS pipeline')
        if task in ['all', 'scrap']:
            for scraper in sts_scrapers:
                scraper.execute()
        if task in ['all', 'parse']:
            for parser in sts_parsers:
                parser.execute()
        if task in ['all', 'export']:
            sts_exporter.execute()
        self.work_progress.show('STS Pipeline has finished!')


class QueryPipelineManager:
    def __init__(self):
        self.work_progress = WorkProgress()

    def execute(self):
        self.work_progress.show('Starting a Query pipeline')
        query_exporter.execute()
        self.work_progress.show('Query Pipeline has finished!')
