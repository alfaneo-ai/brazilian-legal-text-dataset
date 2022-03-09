from .html import HtmlParser, ParagraphHtmlSelector, SumulaHtmlSelector, EnciclopediaHtmlSelector
from .iudicium import IudiciumParser
from .pdf import PdfParser

law_parser = HtmlParser(ParagraphHtmlSelector(), 'planalto')
sumula_parser = HtmlParser(SumulaHtmlSelector(), 'stf')
enciclopedia_parser = HtmlParser(EnciclopediaHtmlSelector(), 'puc', True)
iudicium_parser = IudiciumParser()
pdf_parser = PdfParser()

mlm_parsers = [law_parser, sumula_parser, enciclopedia_parser, iudicium_parser, pdf_parser]

mlm_parsers = [pdf_parser]

sts_parsers = []
