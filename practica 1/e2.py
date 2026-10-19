
import json
import os
import nltk
from nltk.corpus.reader.api import CategorizedCorpusReader, CorpusReader
from bs4 import BeautifulSoup

ruta_corpus = os.path.abspath("corpus_amazon")
if ruta_corpus not in nltk.data.path:
    nltk.data.path.append(ruta_corpus)

class AmazonCorpusReader(CategorizedCorpusReader, CorpusReader):

    def __init__(self, root, fileids=r".*\.json", cat_pattern=r"([^/]+)/.*", encoding="utf-8"):

        CategorizedCorpusReader.__init__(self, {"cat_pattern": cat_pattern})
        CorpusReader.__init__(self, root, fileids, encoding=encoding)

    def leer_documento(self, fileid):
        ruta = self.abspath(fileid)
        with open(ruta, encoding="utf-8") as fichero:
            return json.load(fichero)

    def rating(self, fileid):
        documento = self.leer_documento(fileid)
        return documento['rating']

    def text(self, fileid):
        documento = self.leer_documento(fileid)
        texto = documento['text']

        return texto

    def words(self, fileids):
        if isinstance(fileids, str):
            fileids = [fileids]

        palabras = []
        for fileid in fileids:
            texto = self.text(fileid)
            palabras.extend(nltk.word_tokenize(texto))

        return palabras

    def sents(self, fileids):
        if isinstance(fileids, str):
            fileids = [fileids]

        oraciones = []
        for fileid in fileids:
            texto = self.text(fileid)
            oraciones.extend(nltk.sent_tokenize(texto))

        return oraciones

    def paras(self, fileids):
        if isinstance(fileids, str):
            fileids = [fileids]

        parrafos = []
        for fileid in fileids:
            texto = self.text(fileid)
            parrafos.extend(texto.split("\n\n"))

        return parrafos


if __name__ == "__main__":
    reader = AmazonCorpusReader(root=ruta_corpus)

    primer_archivo = reader.fileids()[3214]

    print("ARCHIVO:", primer_archivo)
    print("DOCUMENTO:", reader.leer_documento(primer_archivo))
    print("RATING:", reader.rating(primer_archivo))
    print("TEXTO:", reader.text(primer_archivo))
    print("PALABRAS:", reader.words(primer_archivo))
    print("ORACIONES:", reader.sents(primer_archivo))
    print("PÁRRAFOS:", reader.paras(primer_archivo))
