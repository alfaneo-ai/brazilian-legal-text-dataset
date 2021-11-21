import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import WorkProgress, DatasetManager, PathUtil

WAIT_TIMEOUT = 10

URLS = ['https://enciclopediajuridica.pucsp.br/tomo/1',
        'https://enciclopediajuridica.pucsp.br/tomo/2',
        'https://enciclopediajuridica.pucsp.br/tomo/3',
        'https://enciclopediajuridica.pucsp.br/tomo/4',
        'https://enciclopediajuridica.pucsp.br/tomo/5',
        'https://enciclopediajuridica.pucsp.br/tomo/6',
        'https://enciclopediajuridica.pucsp.br/tomo/7',
        'https://enciclopediajuridica.pucsp.br/tomo/8',
        'https://enciclopediajuridica.pucsp.br/tomo/9']


class PucEnciclopediaJuridicaScraper:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.rootpath = PathUtil.build_path('output', 'unsupervised', 'puc')

    def execute(self):
        self.work_progress.show('Starting scraper for PUC Enciclopedia Juridica')
        for url in URLS:
            foldername = FileUtils.get_foldername(url)
            targetpath = FileUtils.create_folder(self.rootpath, foldername)
            index = IndexPage(url)
            names, hrefs = index.get_links()
            for name, href in zip(names, hrefs):
                self._process_detail(targetpath, name, href)
            self.work_progress.show('Scraper has finished!')

    def _process_detail(self, targetpath, name, url):
        try:
            detail = DetailPage(url)
            content = detail.get_content()
            filename, filepath = FileUtils.prepare_filepath(name, targetpath)
            self.dataset_manager.to_file(filepath, content)
            self.work_progress.show(f'A file {filename} was created.')
        except WebDriverException:
            self.work_progress.show(f'Error getting {name} in {url}')


class FileUtils:
    @staticmethod
    def prepare_filepath(name, targetpath):
        filename = f'{name}.html'
        filepath = PathUtil.join(targetpath, filename)
        return filename, filepath

    @staticmethod
    def get_foldername(url):
        return url.split('/')[-1]

    @staticmethod
    def create_folder(rootpath, foldername):
        return PathUtil.create_dir(rootpath, foldername)


class IndexPage:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

    def __del__(self):
        self.driver.close()
        self.driver.quit()

    def get_links(self):
        container = self._load_container()
        links = container.find_elements_by_tag_name('a')
        hrefs = [link.get_attribute('href') for link in links]
        titles = [href.split('/')[-1] for href in hrefs]
        return titles, hrefs

    def _load_container(self):
        xpath_container = "//section[@class='tomos-detail-list']"
        condition = EC.presence_of_element_located((By.XPATH, xpath_container))
        container = WebDriverWait(self.driver, WAIT_TIMEOUT).until(condition)
        self._scroll_page_down()
        self._scroll_page_down()
        self._scroll_page_down()
        return container

    def _scroll_page_down(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)


class DetailPage:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

    def __del__(self):
        self.driver.close()
        self.driver.quit()

    def get_content(self):
        self._load_all_content()
        html = self.driver.page_source
        return html

    def _load_all_content(self):
        condition = EC.presence_of_element_located((By.TAG_NAME, 'p'))
        WebDriverWait(self.driver, WAIT_TIMEOUT).until(condition)
