import logging


def create_logger():
    console_handler = logging.StreamHandler()
    lineformat = '[%(asctime)s] | %(levelname)s | [%(process)d - %(processName)s]: %(message)s'
    dateformat = '%d-%m-%Y %H:%M:%S'
    logging.basicConfig(format=lineformat, datefmt=dateformat, level=20, handlers=[console_handler])
    logging.getLogger('pdfminer').setLevel(logging.WARNING)
    return logging.getLogger()


class WorkProgress:
    def __init__(self):
        self.logger = create_logger()
        self.total_steps = 0
        self.current_step = 0

    def show(self, message):
        self.logger.info(message)

    def show_metrics(self, metrics):
        self.logger.info('')
        self.logger.info('-----------------------------------------')
        self.logger.info(f'F1: {metrics[0]}')
        self.logger.info(f'Precision: {metrics[1]}')
        self.logger.info(f'Recall: {metrics[2]}')
        self.logger.info('-----------------------------------------')
        self.logger.info('')

    def start(self, steps):
        self.total_steps = steps
        self.current_step = 0

    def step(self, message):
        self.current_step += 1
        self.logger.info(f'{self.current_step} de {self.total_steps} - {message}')
