from pathlib import Path
from typing import Union, List, Dict

# Importar parsers específicos
# Estos serán importaciones absolutas ya que main_parser.py se carga directamente
from chatbox.ingest.parsers.base import Document
from chatbox.ingest.parsers.pdf import load_pdf, chunk_text as pdf_chunk_text
from chatbox.ingest.parsers.pptx import load_pptx, chunk_text as pptx_chunk_text
from chatbox.ingest.parsers.docx import load_docx, chunk_text as docx_chunk_text
from chatbox.ingest.parsers.txt import load_txt, chunk_text as txt_chunk_text
from chatbox.ingest.parsers.video import load_video_transcript, chunk_text as video_chunk_text
from chatbox.ingest.parsers.image import load_image_ocr, chunk_text as image_chunk_text
from chatbox.ingest.parsers.xlsx import load_xlsx, chunk_text as xlsx_chunk_text
from chatbox.ingest.parsers.web import parse_web # <-- AÑADIDO



def parse_document(file_path: Union[str, Path], source_kind: str = 'local_folder') -> Document:
    """
    Parsea un documento basado en su extensión o tipo de fuente y devuelve un objeto Document.
    """
    if source_kind == 'web_page':
        return parse_web(str(file_path))

    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    content = ""
    metadata = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_extension": suffix,
        "source_type": "unknown" # Se actualizará por cada parser
    }

    if suffix == ".pdf":
        content = load_pdf(str(file_path))
        metadata["source_type"] = "pdf"
    elif suffix == ".pptx":
        content = load_pptx(str(file_path))
        metadata["source_type"] = "pptx"
    elif suffix == ".docx":
        content = load_docx(str(file_path))
        metadata["source_type"] = "docx"
    elif suffix == ".txt" or suffix == ".md":
        content = load_txt(str(file_path))
        # Comprobar si es una transcripción de video por la ruta
        if 'transcripciones_tiktok' in str(file_path):
            metadata["source_type"] = "video_audio"
        else:
            metadata["source_type"] = "txt_md"
    elif suffix in [".mp4", ".avi", ".mov", ".wav", ".mp3"]:
        content = load_video_transcript(str(file_path))
        metadata["source_type"] = "video_audio"
    elif suffix in [".png", ".jpg", ".jpeg", ".gif"]:
        content = load_image_ocr(str(file_path))
        metadata["source_type"] = "image"
    elif suffix in [".xlsx", ".csv"]:
        content = load_xlsx(str(file_path))
        metadata["source_type"] = "xlsx_csv"
    else:
        print(f"Advertencia: Tipo de archivo no soportado para parseo: {suffix}")
        # Podríamos leerlo como texto plano si es un tipo desconocido pero legible
        try:
            content = file_path.read_text(encoding='utf-8')
            metadata["source_type"] = "unsupported_text"
        except Exception:
            content = ""
            metadata["source_type"] = "unsupported_binary"

    return Document(content=content, metadata=metadata)

def chunk_document(document: Document, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """
    Divide el contenido de un documento en chunks y añade metadatos.
    """
    chunks_data = []
    # Usamos page_content por compatibilidad con la clase Document base
    content = document.page_content if hasattr(document, 'page_content') else ''
    if not content:
        return chunks_data

    metadata = document.metadata

    # Dispatch chunking based on source_type if needed, otherwise use generic
    if metadata.get("source_type") == "pdf":
        raw_chunks = pdf_chunk_text(content, chunk_size, chunk_overlap)
    elif metadata.get("source_type") == "pptx":
        raw_chunks = pptx_chunk_text(content, chunk_size, chunk_overlap)
    elif metadata.get("source_type") == "docx":
        raw_chunks = docx_chunk_text(content, chunk_size, chunk_overlap)
    elif metadata.get("source_type") == "txt_md":
        raw_chunks = txt_chunk_text(content, chunk_size, chunk_overlap)
    elif metadata.get("source_type") == "video_audio":
        raw_chunks = video_chunk_text(content, chunk_size, chunk_overlap)
    elif metadata.get("source_type") == "image":
        raw_chunks = image_chunk_text(content, chunk_size, chunk_overlap)
    elif metadata.get("source_type") == "xlsx_csv":
        raw_chunks = xlsx_chunk_text(content, chunk_size, chunk_overlap)
    else:
        # Chunking genérico por caracteres
        raw_chunks = []
        if not content:
            return chunks_data

        start = 0
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            raw_chunks.append(chunk)
            if end >= len(content):
                break
            start += (chunk_size - chunk_overlap)
            if start < 0: # Evitar solapamiento negativo si chunk_size < chunk_overlap
                start = 0

    for i, chunk_content in enumerate(raw_chunks):
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_id"] = f"{metadata.get('file_name', 'doc')}_{i}"
        chunk_metadata["chunk_index"] = i
        # Aquí se podría añadir lógica para section_title, page_slide, timestamp
        chunks_data.append({"content": chunk_content, "metadata": chunk_metadata})

    return chunks_data

if __name__ == "__main__":
    # Ejemplo de uso (requiere un archivo de prueba)
    # from pathlib import Path
    # test_file_path = Path("path/to/your/document.pdf") # O .txt, .pptx, etc.
    # if test_file_path.exists():
    #     doc = parse_document(test_file_path)
    #     print(f"Documento parseado: {doc.metadata.get('file_name')} ({doc.metadata.get('source_type')})")
    #     print(f"Contenido (primeros 200 chars):\n{doc.content[:200]}...")
    #     chunks = chunk_document(doc)
    #     print(f"Número de chunks: {len(chunks)}")
    #     if chunks:
    #         print(f"Primer chunk:\n{chunks[0]['content'][:200]}...")
    #         print(f"Metadatos del primer chunk: {chunks[0]['metadata']}")
    # else:
    #     print(f"Archivo de prueba no encontrado: {test_file_path}")
    pass
