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
        ruta = self.abspath(fileid) # ruta absoluta del archivo a partir de su identificador dentro del corpus
        with open(ruta, encoding="utf-8") as fichero:
            return json.load(fichero) # devuelve diccionario del contenido json del archivo

    def rating(self, fileid):
        documento = self.leer_documento(fileid)
        return documento['rating']
    
    def text(self, fileid):
        documento = self.leer_documento(fileid)
        texto = documento['text']
        
        # interpreta el contenido como HTML y devuelve únicamente el texto, sin las etiquetas
        texto = BeautifulSoup(texto, "html.parser").get_text()

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
    
    primer_archivo = reader.fileids()[:2]
    print(reader.words(primer_archivo))
    