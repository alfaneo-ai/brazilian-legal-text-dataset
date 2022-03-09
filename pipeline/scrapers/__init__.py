from .cjf import CjfThesaurusScraper
from .cnj import CnjBibliotecaDigitalScraper
from .fgv import FgvLivrosDigitais
from .pjerj import PjerjPesquisaProntaScrapper
from .planalto import PlanaltoLawScraper
from .puc import PucEnciclopediaJuridicaScraper
from .stf import StfSumulaScraper, StfIudiciumScraper
from .stj import StjPesquisaProntaScraper
from .tjms import TjmsPublicacoesScrapper

mlm_scrapers = [TjmsPublicacoesScrapper(),
                FgvLivrosDigitais(),
                CnjBibliotecaDigitalScraper(),
                CjfThesaurusScraper(),
                PlanaltoLawScraper(),
                PucEnciclopediaJuridicaScraper(),
                StfSumulaScraper(),
                StfIudiciumScraper()]

mlm_scrapers = [FgvLivrosDigitais()]

sts_scrapers = [PjerjPesquisaProntaScrapper(), StjPesquisaProntaScraper()]
