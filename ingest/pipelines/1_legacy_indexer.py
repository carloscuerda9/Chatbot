import os
import sys
import asyncio
import shutil
import traceback
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Cargar variables de entorno
load_dotenv()

import yaml

# --- RUTAS DE CONFIGURACIÓN ---
# Ruta fija para el índice FAISS dentro de la nueva estructura
FAISS_INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "index", "vector", "faiss_index"))
# Ruta al archivo de configuración de fuentes
SOURCES_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "sources.yaml"))

def load_sources_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Cargar configuración de fuentes
sources_config = load_sources_config(SOURCES_CONFIG_PATH)
# Extraer todas las rutas de los documentos
ALL_DATA_PATHS = []
for source in sources_config.get('sources', []):
    if 'paths' in source:
        for p in source['paths']:
            ALL_DATA_PATHS.append(p)

# --- FIX event loop (Windows / Python 3.12+ con clientes async) ---
def _ensure_event_loop():
    if sys.platform.startswith("win"):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

def main():
    """Función principal para indexar los documentos."""
    print("Iniciando el proceso de indexación...")
    print(f"Rutas de datos configuradas: {ALL_DATA_PATHS}")
    print(f"Carpeta destino del índice FAISS: {FAISS_INDEX_PATH}")
    print(f"CWD (carpeta desde la que ejecutas): {os.getcwd()}")

    # Asegurar event loop antes de inicializar clientes que usan asyncio
    _ensure_event_loop()

    # Validar API Key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: La variable de entorno GOOGLE_API_KEY no está configurada.")
        return

    # Validar que haya rutas de datos configuradas
    if not ALL_DATA_PATHS:
        print("Error: No se han configurado rutas de datos en sources.yaml.")
        return

    try:
        # 1) Cargar documentos
        all_documents = []
        for path in ALL_DATA_PATHS:
            if not os.path.exists(path):
                print(f"Advertencia: La ruta de datos '{path}' no existe y será omitida.")
                continue
            print(f"Cargando documentos desde: {path}")
            loader = DirectoryLoader(
                path,
                glob="**/*.*",
                show_progress=True,
                use_multithreading=True,
                silent_errors=True,
            )
            documents = loader.load()
            all_documents.extend(documents)

        if not all_documents:
            print("No se encontraron documentos para indexar en ninguna de las rutas configuradas. Revisa las carpetas y los formatos.")
            return

        documents = all_documents # Usar el nombre de variable original para el resto del script

        if not documents:
            print("No se encontraron documentos para indexar. Revisa la carpeta y los formatos.")
            return

        print(f"Se cargaron {len(documents)} documentos.")

        # 2) Split en chunks
        print("Dividiendo documentos en chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)
        print(f"Se han creado {len(docs)} chunks de texto.")

        # 3) Embeddings (forzar REST si la versión lo permite; si no, fallback)
        print("Creando embeddings con el modelo de Google...")
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", transport="rest")
        except TypeError:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

        # 4) Crear y guardar índice FAISS
        print("Creando y guardando el índice FAISS... (esto puede tardar)")

        if os.path.exists(FAISS_INDEX_PATH):
            print(f"Eliminando índice antiguo en '{FAISS_INDEX_PATH}'...")
            shutil.rmtree(FAISS_INDEX_PATH)

        db = FAISS.from_documents(docs, embeddings)
        db.save_local(FAISS_INDEX_PATH)

        print("\n¡Proceso de indexación completado con éxito!")
        print(f"El índice ha sido guardado en: '{FAISS_INDEX_PATH}'")
        print("Archivos esperados: 'index.faiss' y 'index.pkl' dentro de esa carpeta.")

    except Exception as e:
        print("\nOcurrió un error durante la indexación:")
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()

