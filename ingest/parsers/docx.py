from typing import List

def load_docx(file_path: str) -> str:
    """
    Placeholder para extraer texto de un archivo DOCX.
    Requiere la librería python-docx.
    """
    print(f"Advertencia: El parser DOCX para {file_path} no está implementado completamente.")
    return "Contenido DOCX de ejemplo.\n"

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunking genérico para DOCX.
    """
    # Implementación de chunking genérico, similar a pdf.py o main_parser.py
    chunks = []
    if not text:
        return chunks

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start += (chunk_size - chunk_overlap)
        if start < 0:
            start = 0
    return chunks
