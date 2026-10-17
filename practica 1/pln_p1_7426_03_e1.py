import json
import os
import urllib.request
import gzip, shutil
import ssl

BASE_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories"
CATEGORIAS_PRODUCTO = ["Digital_Music", "Amazon_Fashion", "All_Beauty"]

RUTA_DATOS = "datos"
RUTA_CORPUS = "corpus_amazon"
MAX_CLASE_CATEGORIA = (
    1000  # 1000 de cada clase por categoría = 3000 en total por clase
)

CLASES = ["negativas", "neutrales", "positivas"]


def categoria(nota):
    if nota <= 2:
        return "negativas"
    elif nota == 3:
        return "neutrales"
    return "positivas"


def descargar(nombre):
    """Descarga el .jsonl (comprimido) si no existe y devuelve su ruta."""
    os.makedirs(RUTA_DATOS, exist_ok=True)
    ruta = os.path.join(RUTA_DATOS, f"{nombre}.jsonl")
    
    if not os.path.exists(ruta):
        url = f"{BASE_URL}/{nombre}.jsonl.gz"
        ruta_gz = ruta + ".gz"
        print(f"Descargando {url}")
        
        # Crear un contexto SSL que no verifique certificados caducados
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Descargar usando el contexto SSL personalizado
        with (
            urllib.request.urlopen(url, context=ctx) as response,
            open(ruta_gz, "wb") as out_file,
        ):
            shutil.copyfileobj(response, out_file)
        
        print(f"Descomprimiendo {nombre}.jsonl.gz...")
        with gzip.open(ruta_gz, "rb") as f_in, open(ruta, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
            
        # Limpiar archivo comprimido tras extraer
        if os.path.exists(ruta_gz):
            os.remove(ruta_gz)
            
    return ruta


def main():
    for cat in CLASES:
        os.makedirs(os.path.join(RUTA_CORPUS, cat), exist_ok=True)

    contadores = {c: 0 for c in CLASES}

    for nombre in CATEGORIAS_PRODUCTO:
        
        ruta_jsonl = descargar(nombre)
        print(f"Procesando {nombre}...")
        
        # Contadores locales para equilibrar la categoría actual
        contadores_cat = {c: 0 for c in CLASES}

        with open(ruta_jsonl, encoding="utf-8") as f:
            for linea in f:
        
                # Si ya completamos las 3 clases para la categoría de producto actual, pasar a la siguiente
                if all(cnt >= MAX_CLASE_CATEGORIA for cnt in contadores_cat.values()):
                    print(f"Límite alcanzado para la categoría de producto: {nombre}")
                    break
                
                if not linea.strip():
                    continue
                
                r = json.loads(linea)

                texto = (r.get("text") or "").strip()
                if not texto:
                    continue

                cat = categoria(float(r["rating"]))

                # Verificar límite local de esta categoría de producto
                if contadores_cat[cat] >= MAX_CLASE_CATEGORIA:
                    continue

                contadores_cat[cat] += 1
                contadores[cat] += 1

                doc_id = f"{contadores[cat]:06d}"

                doc = {
                    "id": doc_id,
                    "categoria_producto": nombre,
                    "rating": r.get("rating"),
                    "title": r.get("title"),
                    "text": texto,
                    "asin": r.get("asin"),
                    "parent_asin": r.get("parent_asin"),
                    "user_id": r.get("user_id"),
                    "timestamp": r.get("timestamp"),
                    "helpful_vote": r.get("helpful_vote"),
                    "verified_purchase": r.get("verified_purchase"),
                }

                ruta = os.path.join(RUTA_CORPUS, cat, f"{doc_id}.json")
                with open(ruta, "w", encoding="utf-8") as out:
                    json.dump(doc, out, ensure_ascii=False)

    print("\nProceso finalizado. Documentos guardados por sentimiento:")
    for cat, count in contadores.items():
        print(f"  - {cat}: {count}")


if __name__ == "__main__":
    main()