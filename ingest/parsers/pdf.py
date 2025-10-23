
from pathlib import Path
from typing import List
from pypdf import PdfReader

def load_pdf(file_path: str) -> str:
    """Carga el texto de un archivo PDF."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Divide el texto en chunks con un tamaño y solapamiento definidos."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += (chunk_size - chunk_overlap)
    return chunks
