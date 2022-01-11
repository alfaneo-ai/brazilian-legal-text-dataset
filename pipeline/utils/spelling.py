import re


def correct_spelling(text):
    text = re.sub(r'E\sM\sE\sN\sT\sA[\s\.-–]', 'EMENTA ', text).strip()
    return re.sub(r'A\sC\sÓ\sR\sD\sÃ\sO', 'ACÓRDÃO', text)
