from .html import HtmlParser, ParagraphHtmlSelector, SumulaHtmlSelector, EnciclopediaHtmlSelector
from .iudicium import IudiciumParser

law_parser = HtmlParser(ParagraphHtmlSelector(), 'planalto')
sumula_parser = HtmlParser(SumulaHtmlSelector(), 'stf')
enciclopedia_parser = HtmlParser(EnciclopediaHtmlSelector(), 'puc')
iudicium_parser = IudiciumParser()

# all_parsers = [law_parser, sumula_parser, enciclopedia_parser, iudicium_parser]
all_parsers = [iudicium_parser]