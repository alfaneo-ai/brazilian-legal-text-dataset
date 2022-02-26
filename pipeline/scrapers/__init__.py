from .cjf import CjfThesaurusScraper
from .planalto import PlanaltoLawScraper
from .puc import PucEnciclopediaJuridicaScraper
from .stf import StfSumulaScraper, StfIudiciumScraper
from .stj import StjPesquisaProntaScraper
from .tjrj import TjrjPesquisaProntaScrapper

mlm_scrapers = [CjfThesaurusScraper(), PlanaltoLawScraper(), PucEnciclopediaJuridicaScraper(),
                StfSumulaScraper(), StfIudiciumScraper()]

# sts_scrapers = [TjrjPesquisaProntaScrapper(), StjPesquisaProntaScraper()]

sts_scrapers = [TjrjPesquisaProntaScrapper()]
