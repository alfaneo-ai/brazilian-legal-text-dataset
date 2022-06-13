from pipeline.utils import *


class StatisticsForDatasets:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()

    def execute(self):
        self.work_progress.show('Starting a MLM pipeline')
        full = self.dataset_manager.from_csv('output/sts/full.csv')
        stats = full.groupby(['origem']).size().reset_index(name='total')
        self.dataset_manager.to_csv(stats, 'output/stats.csv')
        self.work_progress.show('MLM Pipeline has finished!')


if __name__ == '__main__':
    StatisticsForDatasets().execute()
