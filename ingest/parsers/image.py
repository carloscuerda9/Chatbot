from typing import List

def load_image_ocr(file_path: str) -> str:
    """
    Placeholder para extraer texto de imágenes usando OCR.
    Requiere librerías como Pillow y pytesseract/tesserocr.
    """
    print(f"Advertencia: El parser de imágenes (OCR) para {file_path} no está implementado completamente.")
    return "Texto extraído de imagen de ejemplo.\n"

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunking genérico para texto de imágenes.
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
