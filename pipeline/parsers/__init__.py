from .html import HtmlParser, ParagraphHtmlSelector, SumulaHtmlSelector, EnciclopediaHtmlSelector, PjerjHtmlParser, \
    StjTotalHtmlParser, StjSearchHtmlParser, FgvHtmlParser, CnjTotalHtmlParser, CnjSearchHtmlParser
from .iudicium import IudiciumParser
from .pdf import PdfReader, PdfPjerjParser, PdfFgvParser

law_parser = HtmlParser(ParagraphHtmlSelector(), 'planalto')
sumula_parser = HtmlParser(SumulaHtmlSelector(), 'stf')
enciclopedia_parser = HtmlParser(EnciclopediaHtmlSelector(), 'puc', True)
iudicium_parser = IudiciumParser()

mlm_parsers = [law_parser, sumula_parser, enciclopedia_parser, iudicium_parser]

sts_parsers = [PdfFgvParser()]
