class DatasetManager:

    @staticmethod
    def to_file(filepath, texts):
        textfile = open(filepath, 'w')
        if isinstance(texts, list):
            for element in texts:
                textfile.write(element + "\n")
        else:
            textfile.write(texts)
        textfile.close()

    @staticmethod
    def to_text(filepath):
        textfile = open(filepath, 'r')
        text = textfile.read()
        textfile.close()
        return text
