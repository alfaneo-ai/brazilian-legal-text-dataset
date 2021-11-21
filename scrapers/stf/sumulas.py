from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import WorkProgress, DatasetManager, PathUtil

WAIT_TIMEOUT = 10


class StfSumulaScraper:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.index_url = 'http://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=30'
        self.rootpath = PathUtil.build_path('output', 'unsupervised', 'stf')

    def execute(self):
        self.work_progress.show('Starting scraper stf for getting sumulas')
        targetpath = self._create_folder(self.rootpath, 'sumulas')
        index = IndexPage(self.index_url)
        names, hrefs = index.get_links()
        for name, href in zip(names, hrefs):
            self._process_detail(targetpath, name, href)
        self.work_progress.show('Scraper has finished!')

    def _process_detail(self, targetpath, name, href):
        try:
            detail = DetailPage(href)
            content = detail.get_content()
            filename = f'{name}.html'
            filepath = PathUtil.join(targetpath, filename)
            self.dataset_manager.to_file(filepath, content)
            self.work_progress.show(f'A file {filename} was created.')
        except WebDriverException:
            self.work_progress.show(f'Error getting {name} in {href}')

    @staticmethod
    def _get_foldername(url):
        return url.split('/')[-1]

    @staticmethod
    def _create_folder(rootpath, foldername):
        return PathUtil.create_dir(rootpath, foldername)


class IndexPage:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

    def __del__(self):
        self.driver.close()
        self.driver.quit()

    def get_links(self):
        xpath_container = "//div[@class='sumarioSumulas']"
        condition = EC.presence_of_element_located((By.XPATH, xpath_container))
        container = WebDriverWait(self.driver, WAIT_TIMEOUT).until(condition)
        links = container.find_elements_by_tag_name('a')
        hrefs = [link.get_attribute('href') for link in links]
        hrefs = [href for href in hrefs if not href.endswith('.doc') and not href.endswith('.pdf')]
        titles = [href.split('=')[-1].replace('.htm', '') for href in hrefs]
        return titles, hrefs


class DetailPage:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

    def __del__(self):
        self.driver.close()
        self.driver.quit()

    def get_content(self):
        condition = EC.presence_of_element_located((By.TAG_NAME, 'p'))
        WebDriverWait(self.driver, WAIT_TIMEOUT).until(condition)
        html = self.driver.page_source
        return html
