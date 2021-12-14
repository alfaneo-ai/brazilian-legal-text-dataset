from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import WorkProgress, DatasetManager, PathUtil

WAIT_TIMEOUT = 10


class PlanaltoLawScraper:
    def __init__(self):
        self.work_progress = WorkProgress()
        self.dataset_manager = DatasetManager()
        self.two_level_deep_urls = [
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/codigos-1',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/estatutos'
        ]
        self.three_level_deep_urls = [
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/leis-ordinarias',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/leis-complementares-1',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/medidas-provisorias',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/decretos1',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/decretos-leis',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/decretos-nao-numerados1',
            'http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/leis-delegadas-1'
        ]
        self.rootpath = PathUtil.build_path('output', 'mlm', 'planalto')

    def execute(self):
        self.work_progress.show('Starting scraper laws from planalto')
        self._process_two_level_deep()
        self._process_three_level_deep()
        self.work_progress.show('Scraper has finished!')

    def _process_three_level_deep(self):
        for url in self.three_level_deep_urls:
            self.work_progress.show(f'Getting links to internal pages from {url}')
            foldername = self._get_foldername(url)
            targetpath = self._create_folder(self.rootpath, foldername)
            index1 = IndexPage(url)
            names, hrefs = index1.get_links()
            for href in hrefs:
                self._process_index(targetpath, href)

    def _process_two_level_deep(self):
        for url in self.two_level_deep_urls:
            self._process_index(self.rootpath, url)

    def _process_index(self, rootpath, url):
        self.work_progress.show(f'Getting links to internal pages from {url}')
        foldername = self._get_foldername(url)
        targetpath = self._create_folder(rootpath, foldername)
        index = IndexPage(url)
        names, hrefs = index.get_links()
        for name, href in zip(names, hrefs):
            self._process_detail(targetpath, name, href)

    def _process_detail(self, targetpath, name, href):
        try:
            detail = DetailPage(href)
            content = detail.get_content()
            filename = f'{name}.html'
            filepath = PathUtil.join(targetpath, filename)
            self.dataset_manager.to_file(filepath, content)
            self.work_progress.show(f'A file {filename} was created.')
        except WebDriverException:
            self.work_progress.show(f'Getting error {name} in {href}')

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
        xpath_container = "//table[@class='visaoQuadrosTabela'] | //div[@id='parent-fieldname-text']"
        condition = EC.presence_of_element_located((By.XPATH, xpath_container))
        container = WebDriverWait(self.driver, WAIT_TIMEOUT).until(condition)
        links = container.find_elements_by_tag_name('a')
        hrefs = [link.get_attribute('href') for link in links]
        hrefs = [href for href in hrefs if not href.endswith('.doc') and not href.endswith('.pdf')]
        titles = [href.split('/')[-1].replace('.htm', '') for href in hrefs]
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
