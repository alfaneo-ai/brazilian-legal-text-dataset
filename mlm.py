import argparse

from pipeline import MlmPipelineManager


def parse_commands():
    parser = argparse.ArgumentParser(prog='mlm',
                                     usage='%(prog)s task',
                                     description='Run pipeline to generate dataset for BERT MLM trainning')

    parser.add_argument('task',
                        choices=['all', 'scrap', 'parse', 'export'],
                        action='store',
                        default='all',
                        help='Set a target task (scrap, parse, export)')
    args = vars(parser.parse_args())
    return args['task']


if __name__ == '__main__':
    task = parse_commands()
    pipeline = MlmPipelineManager()
    pipeline.execute(task)
