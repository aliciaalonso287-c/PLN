import json
import os
import urllib.request

BASE_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories"
CATEGORIAS_PRODUCTO = ["Digital_Music", "Amazon_Fashion", "All_Beauty"]

RUTA_DATOS = "datos"
RUTA_CORPUS = "corpus_amazon"
MAX_POR_CLASE = 3000   # None para no limitar

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
        urllib.request.urlretrieve(url, ruta_gz)
        import gzip, shutil
        with gzip.open(ruta_gz, "rb") as f_in, open(ruta, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    return ruta


def main():
    for cat in CLASES:
        os.makedirs(os.path.join(RUTA_CORPUS, cat), exist_ok=True)

    contadores = {c: 0 for c in CLASES}

    for nombre in CATEGORIAS_PRODUCTO:
        ruta_jsonl = descargar(nombre)
        print(f"Procesando {nombre}...")

        with open(ruta_jsonl, encoding="utf-8") as f:
            for linea in f:
                if not linea.strip():
                    continue
                r = json.loads(linea)

                texto = (r.get("text") or "").strip()
                if not texto:
                    continue

                cat = categoria(float(r["rating"]))
                if MAX_POR_CLASE and contadores[cat] >= MAX_POR_CLASE:
                    continue

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

    print("Documentos guardados:", contadores)


if __name__ == "__main__":
    main()