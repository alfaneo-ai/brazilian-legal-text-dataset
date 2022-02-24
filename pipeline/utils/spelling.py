import re
import time


def correct_spelling(text):
    try:
        text = re.sub(r'E\sM\sE\sN\sT\sA[\s\.-–]', 'EMENTA ', text).strip()
        return re.sub(r'A\sC\sÓ\sR\sD\sÃ\sO', 'ACÓRDÃO', text)
    except TypeError as error:
        print(text)
        print(error)
