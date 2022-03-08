from .cjf import CjfThesaurusScraper
from .planalto import PlanaltoLawScraper
from .puc import PucEnciclopediaJuridicaScraper
from .stf import StfSumulaScraper, StfIudiciumScraper
from .stj import StjPesquisaProntaScraper
from .pjerj import PjerjPesquisaProntaScrapper
from .fgv import FgvLivrosDigitais
from .tjms import TjmsPublicacoesScrapper
from .cnj import CnjBibliotecaDigitalScraper

mlm_scrapers = [CjfThesaurusScraper(), PlanaltoLawScraper(), PucEnciclopediaJuridicaScraper(),
                StfSumulaScraper(), StfIudiciumScraper()]


# sts_scrapers = [TjmsPublicacoesScrapper(), FgvLivrosDigitais(), PjerjPesquisaProntaScrapper(), StjPesquisaProntaScraper(), ]
sts_scrapers = [CnjBibliotecaDigitalScraper()]
