import argparse

from pipeline import StsPipelineManager


def parse_commands():
    parser = argparse.ArgumentParser(prog='mlm',
                                     usage='%(prog)s task',
                                     description='Run pipeline to generate dataset for BERT STS fine-tunning')

    parser.add_argument('task',
                        choices=['all', 'scrap', 'parse', 'export'],
                        action='store',
                        default='all',
                        help='Set a target task (scrap, parse, export)')

    parser.add_argument('--sts_type',
                        action='store',
                        default="binary",
                        type=str,
                        help='Define STS type (binary, scale and triplet)')

    args = vars(parser.parse_args())
    return args['task'], args['sts_type']


if __name__ == '__main__':
    task, sts_type = parse_commands()
    pipeline = StsPipelineManager()
    pipeline.execute(task, sts_type)
