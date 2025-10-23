import sys
from pathlib import Path
import yaml
from typing import List, Dict, Union
import hashlib
import datetime
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno desde el archivo .env

from chatbox.ingest.parsers.main_parser import parse_document, chunk_document
from chatbox.ingest.parsers.base import Document
from chatbox.index.vector.faiss_index import FAISSIndexer

def generate_hash(content: str) -> str:
    """
    Genera un hash SHA-256 del contenido para deduplicación.
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def process_source(source: Dict, indexer: FAISSIndexer):
    """
    Procesa una única fuente de datos (directorio local o página web).
    """
    kind = source.get('kind')
    paths = source.get('paths', [])
    
    for path_str in paths:
        if kind == 'local_folder':
            directory_path = project_root / path_str
            ingest_documents_from_directory(directory_path, indexer)
        elif kind == 'web_page':
            ingest_document_from_web(path_str, indexer)

def ingest_document_from_web(url: str, indexer: FAISSIndexer):
    """
    Ingesta un documento desde una URL.
    """
    print(f"Procesando página web: {url}")
    try:
        doc = parse_document(url, source_kind='web_page')
        if not doc or not doc.page_content:
            print(f"Advertencia: No se pudo extraer contenido de {url}. Saltando.")
            return

        # Enriquecer metadatos para la web
        doc.metadata["ingested_at"] = datetime.datetime.now().isoformat()
        doc.metadata["hash"] = generate_hash(doc.page_content)

        chunks = chunk_document(doc)
        if chunks:
            indexer.add_documents(chunks)
            print(f"  -> {len(chunks)} chunks generados y añadidos al índice.")

    except Exception as e:
        print(f"Error al procesar {url}: {e}")

def ingest_documents_from_directory(directory_path: Union[str, Path], 
                                    indexer: FAISSIndexer):
    """
    Ingesta documentos de un directorio, parsea, chunkea y extrae metadatos.
    """
    directory_path = Path(directory_path)
    if not directory_path.is_dir():
        print(f"Error: La ruta no es un directorio válido: {directory_path}")
        return

    for file_path in directory_path.rglob('*'):
        if file_path.is_file():
            print(f"Procesando archivo: {file_path}")
            try:
                doc = parse_document(file_path, source_kind='local_folder')
                if not doc.page_content:
                    print(f"Advertencia: No se pudo extraer contenido de {file_path}. Saltando.")
                    continue

                # Enriquecer metadatos
                doc.metadata["ingested_at"] = datetime.datetime.now().isoformat()
                doc.metadata["hash"] = generate_hash(doc.page_content)

                chunks = chunk_document(doc)
                if chunks:
                    indexer.add_documents(chunks)
                    print(f"  -> {len(chunks)} chunks generados y añadidos al índice.")

            except Exception as e:
                print(f"Error al procesar {file_path}: {e}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    # Cargar configuración de fuentes
    config_path = project_root / 'chatbox' / 'config' / 'sources.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Inicializar el indexador FAISS
    try:
        indexer = FAISSIndexer(llm_provider="openai")
    except Exception as e:
        print(f"Error al inicializar el indexador: {e}")
        print("Asegúrate de que tu API Key (OPENAI_API_KEY o GOOGLE_API_KEY) esté configurada correctamente.")
        exit()

    # Procesar cada fuente definida en el YAML
    for source in config.get('sources', []):
        print(f"\n--- Procesando fuente: {source.get('name')} ({source.get('kind')}) ---")
        process_source(source, indexer)

    print("\n--- Ingesta completada para todas las fuentes ---")