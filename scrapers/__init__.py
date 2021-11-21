from .cjf import CjfThesaurusScraper
from .planalto import PlanaltoLawScraper
from .puc import PucEnciclopediaJuridicaScraper
from .stf import StfSumulaScraper, StfIudiciumScraper

all_scrapers = [CjfThesaurusScraper(), PlanaltoLawScraper(), PucEnciclopediaJuridicaScraper(),
                StfSumulaScraper(), StfIudiciumScraper()]
