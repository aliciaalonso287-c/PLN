import json
import os
import re
import nltk
from nltk.corpus.reader.api import CategorizedCorpusReader, CorpusReader
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

ruta_corpus = os.path.abspath("corpus_amazon")
if ruta_corpus not in nltk.data.path:
    nltk.data.path.append(ruta_corpus)
    
# descargar las stopwords de NLTK por si no estan localmente
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")
    
# cargar conjunto de stopwords ('english' para reseñas de Amazon)
STOPWORDS_EN = set(stopwords.words("english"))
    
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
        texto = BeautifulSoup(texto, "html.parser").get_text(separator="\n\n")
                
        # eliminamos emojis y caracteres no deseados / símbolos especiales (conservando letras, números, signos y puntuación estándar)
        # dejando caracteres unicode alfanuméricos y puntuación
        texto = re.sub(r"[^\w\s.,!?:;\-\'\"]", "", texto)
        
        # para reducir caracteres repetidos de forma consecutiva
        texto = re.sub(r"(.)\1{2,}", r"\1\1", texto)  
        
        # Limpiar espacios sin perder la separación entre párrafos
        texto = re.sub(r"[^\S\n]+", " ", texto)
        texto = re.sub(r"\n\s*\n+", "\n\n", texto)  

        return texto.strip()
    
    def words(self, fileids, keep_stopwords=True):
        if isinstance(fileids, str):
            fileids = [fileids]

        palabras = []
        for fileid in fileids:
            texto = self.text(fileid)
            # filtrar tokens vacíos o que consistan solo en espacios en blanco
            tokens = [w.strip() for w in nltk.word_tokenize(texto) if w and w.strip()]
            
            # filtrar opcionalmente las stopwords
            if not keep_stopwords:
                tokens = [
                    w for w in tokens if w.lower() not in STOPWORDS_EN
                ]
            palabras.extend(tokens)

        return palabras
        
        
    def sents(self, fileids):
        if isinstance(fileids, str):
            fileids = [fileids]

        oraciones = []
        for fileid in fileids:
            texto = self.text(fileid)
            # filtra oraciones vacías o de solo espacios
            oraciones.extend(
            [
                s.strip()
                for s in nltk.sent_tokenize(texto)
                if s and s.strip()
            ]
        )

        return oraciones
    
    def paras(self, fileids):
        if isinstance(fileids, str):
            fileids = [fileids]

        parrafos = []
        for fileid in fileids:
            texto = self.text(fileid)
            
            # filtrar cualquier párrafo que esté vacío o solo contenga espacios
            parrafos.extend(
                [p.strip() for p in re.split(r"\n+", texto) if p and p.strip()]
            )

        return parrafos
    
    def describe_corpus(self):
        documentos = self.fileids()
        
        vocabulario = set()
        total_tokens = 0
        tamano_bytes = 0

        for i, fileid in enumerate(documentos, 1):
            if i % 1000 == 0 or i == len(documentos):
                print(f"  Procesando documento {i}/{len(documentos)}...")
            
            #tamaño real en bytes
            ruta = self.abspath(fileid)
            tamano_bytes += os.path.getsize(ruta)

            # contar tokens del texto limpio, conservando stopwords
            palabras = self.words(fileid, keep_stopwords=True)
            total_tokens += len(palabras)

            # vocabulario de palabras en minúsculas
            vocabulario.update(palabra.lower() for palabra in palabras if palabra.isalnum())

        # convertir bytes a Megabytes para mejor lectura
        tamano_mb = tamano_bytes / (1024 * 1024)
            
        print("\nDESCRIPCIÓN DEL CORPUS")
        print(f"Número de documentos:  {len(documentos)}")
        print(f"Tamaño total en disco: {tamano_mb:.2f} MB ({tamano_bytes} bytes)")
        print(f"Número total tokens:   {total_tokens}")
        print(f"Tamaño del vocabulario: {len(vocabulario)} palabras únicas")
    
if __name__ == "__main__":
    reader = AmazonCorpusReader(root=ruta_corpus)
    
     # 1. Comprobar categorías y archivos
    print("\n--- CATEGORÍAS ---")
    print(reader.categories())

    categorias = reader.categories()
    if categorias:
        categoria = categorias[0]
        print(f"Archivos de {categoria}:")
        print(reader.fileids(categories=categoria)[:5])

    # 2. Obtener archivos individuales
    fileids = reader.fileids()
    print("\n--- ARCHIVOS ---")
    print("Número de archivos:", len(fileids))

    if fileids:
        fileid = fileids[7]
        print("Archivo de prueba:", fileid)

        # 3. Documento completo
        print("\n--- DOCUMENTO JSON ---")
        print(reader.leer_documento(fileid))

        # 4. Rating
        print("\n--- RATING ---")
        print(reader.rating(fileid))

        # 5. Texto limpio
        print("\n--- TEXTO ---")
        print(repr(reader.text(fileid)))

        # 6. Palabras
        print("\n--- PALABRAS ---")
        print(reader.words(fileid)[:30])

        # 7. Palabras sin stopwords
        print("\n--- PALABRAS SIN STOPWORDS ---")
        print(reader.words(fileid, keep_stopwords=False)[:30])

        # 8. Oraciones
        print("\n--- ORACIONES ---")
        print(reader.sents(fileid))

        # 9. Párrafos
        print("\n--- PÁRRAFOS ---")
        print(reader.paras(fileid))

    else:
        print("No se han encontrado archivos JSON.")
        
    reader.describe_corpus()
        