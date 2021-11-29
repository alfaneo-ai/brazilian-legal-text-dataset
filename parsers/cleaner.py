import re
from copy import deepcopy


class Cleaner:
    def clear(self, paragraphs):
        if not paragraphs:
            return paragraphs
        is_array = isinstance(paragraphs, list)
        texts = deepcopy(paragraphs)
        if not is_array:
            texts = [texts]
        texts = self._remove_undesired_chars(texts)
        texts = self._remove_multiples_spaces(texts)
        texts = self._remove_multiples_dots(texts)
        texts = self._remove_citation(texts)
        texts = self._remove_space_in_last_period(texts)
        texts = self._remove_last_number(texts)
        texts = self._strip_spaces(texts)
        if not is_array:
            texts = texts[0]
        return texts

    @staticmethod
    def _remove_undesired_chars(paragraphs):
        return [re.sub(r'[”“●_\n\t\'\"]', '', paragraph) for paragraph in paragraphs]

    @staticmethod
    def _remove_multiples_spaces(paragraphs):
        return [re.sub(r'\s+', ' ', paragraph) for paragraph in paragraphs]

    @staticmethod
    def _remove_multiples_dots(paragraphs):
        paragraphs = [re.sub(r'\.+', '.', paragraph) for paragraph in paragraphs]
        return [re.sub(r'^\.\s', '', paragraph) for paragraph in paragraphs]

    @staticmethod
    def _remove_citation(paragraphs):
        return [re.sub(r'[\[\(].+[\]\)]', '', paragraph) for paragraph in paragraphs]

    @staticmethod
    def _remove_space_in_last_period(paragraphs):
        return [re.sub(r'\s\.$', '.', paragraph) for paragraph in paragraphs]

    @staticmethod
    def _remove_last_number(paragraphs):
        return [re.sub(r'\.\d+$', '.', paragraph) for paragraph in paragraphs]

    @staticmethod
    def _strip_spaces(paragraphs):
        return [paragraph.strip() for paragraph in paragraphs]


if __name__ == '__main__':
    # text = 'Ementa : AGRAVO INTERNO. RECURSO EXTRAORDINÁRIO COM AGRAVO. FUNDAMENTAÇÃO A RESPEITO DA REPERCUSSÃO GERAL. INSUFICIÊNCIA. REAPRECIAÇÃO DE PROVAS. INADMISSIBILIDADE. SÚMULA 279 DO STF. TEMA 138 DE REPERCUSSÃO GERAL. PRECEDENTES. 1. Os Recursos Extraordinários somente serão conhecidos e julgados, quando essenciais e relevantes as questões constitucionais a serem analisadas, sendo imprescindível ao recorrente, em sua petição de interposição de recurso, a apresentação formal e motivada da repercussão geral, que demonstre, perante o SUPREMO TRIBUNAL FEDERAL, a existência de acentuado interesse geral na solução das questões constitucionais discutidas no processo, que transcenda a defesa puramente de interesses subjetivos e particulares. 2. A obrigação do recorrente em apresentar formal e motivadamente a preliminar de repercussão geral, que demonstre sob o ponto de vista econômico, político, social ou jurídico, a relevância da questão constitucional debatida que ultrapasse os interesses subjetivos da causa, conforme exigência constitucional e legal , examinou a repercussão geral da questão constitucional debatida neste recurso, tendo fixado a seguinte tese: Ao Estado é facultada a revogação de atos que repute ilegalmente praticados; porém, se de tais atos já tiverem decorrido efeitos concretos, seu desfazimento deve ser precedido de regular processo administrativo. 5. Agravo interno a que se nega provimento.'
    text = '__________________. Considerações sobre as relações do estado e do direito na economia. In: Revista Brasileira de Direito Público (RBDP), 14, nº 55, out./dez. Belo Horizonte: Fórum, 2016.'
    result = Cleaner().clear(text)
    print(result)