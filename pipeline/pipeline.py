import argparse

from parsers import all_parsers
from scrapers import all_scrapers
from utils import WorkProgress
from .merger import Merger


def parse_commands():
    parser = argparse.ArgumentParser(prog='CLI', description='Brazilian Legal Texts Scraper')
    parser.add_argument('task',
                        choices=['all', 'scrap', 'parse', 'merge'],
                        action='store',
                        default='all',
                        help='Set a target task to execute')
    args = vars(parser.parse_args())
    return args['task']


class PipelineManager:
    def __init__(self):
        self.work_progress = WorkProgress()

    def execute(self):
        self.work_progress.show('Starting a pipeline')
        task = parse_commands()
        if task in ['all', 'scrap']:
            for scraper in all_scrapers:
                scraper.execute()
        if task in ['all', 'parse']:
            for parser in all_parsers:
                parser.execute()
        if task in ['all', 'merge']:
            Merger().execute()
        self.work_progress.show('Pipeline has finished!')
