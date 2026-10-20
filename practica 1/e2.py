
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
            parrafos.extend(texto.split("\n"))

        return parrafos
    
    def estadisticas_corpus(reader):
        # ficheros
        ficheros = reader.fileids()
        print("TOTAL DE FICHEROS:", len(ficheros))
        print("PRIMEROS FICHEROS:", ficheros[:5])

        # categorías del corpus
        categorias = reader.categories()
        print("\nCATEGORÍAS:", categorias)

        # ficheros de cada categoría
        for categoria in categorias:
            ficheros_categoria = reader.fileids(categories=categoria)
            print(f"\nFICHEROS DE {categoria.upper()}:",
                len(ficheros_categoria))
  
        # Estadísticas generales del corpus
        documentos = [reader.leer_documento(f) for f in ficheros]

        total = len(documentos)
        con_rating = sum(1 for d in documentos if d.get("rating") is not None)
        
        con_texto = sum(1 for d in documentos if d.get("text") and d["text"].strip())
        
        con_rating_texto = sum(
            1 for d in documentos
            if d.get("rating") is not None
            and d.get("text") and d["text"].strip()
        )

        distribucion = {}
        for d in documentos:
            rating = d.get("rating")
            if rating is not None:
                distribucion[rating] = distribucion.get(rating, 0) + 1

        # Comprobar los nombres reales de estos campos en los JSON
        productos = {
            d.get("asin") for d in documentos
            if d.get("asin") is not None
        }
        usuarios = {
            d.get("user_id") for d in documentos
            if d.get("user_id") is not None
        }

        print("\n" + "=" * 45)
        print("ESTADÍSTICAS DEL CORPUS")
        print("=" * 45)
        print("Número de reseñas:", total)
        print("Reseñas con rating:", con_rating)
        print("Reseñas con texto:", con_texto)
        print("Reseñas con rating y texto:", con_rating_texto)
        print("Número de productos únicos:", len(productos))
        print("Número de usuarios únicos:", len(usuarios))

        print("\nDistribución de ratings:")
        for rating in sorted(distribucion):
            print(f"  {rating} estrellas: {distribucion[rating]}")



if __name__ == "__main__":
    reader = AmazonCorpusReader(root=ruta_corpus)
    reader.estadisticas_corpus()
    
 