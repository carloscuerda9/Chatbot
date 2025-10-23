from typing import Dict

class Document:
    """Una clase simple para contener el contenido y metadatos de un documento."""
    def __init__(self, content: str, metadata: Dict = None):
        self.page_content = content # Usamos page_content para compatibilidad con Langchain
        self.metadata = metadata if metadata is not None else {}
