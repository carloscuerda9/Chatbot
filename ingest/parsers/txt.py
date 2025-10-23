from typing import List

def load_txt(file_path: str) -> str:
    """
    Extrae texto de archivos TXT o MD.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error al leer el archivo TXT/MD {file_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunking genérico para TXT/MD.
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
