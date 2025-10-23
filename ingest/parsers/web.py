
import requests
from bs4 import BeautifulSoup

# Usaremos la clase Document definida en main_parser, no la de Langchain
# from langchain.docstore.document import Document 
from chatbox.ingest.parsers.base import Document

def parse_web(url: str) -> Document:
    """
    Extrae el contenido de texto de una URL y lo devuelve como nuestro objeto Document custom.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas HTTP no exitosas
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer texto y limpiar espacios en blanco
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Crear nuestro documento custom
        metadata = {'source': url, 'file_name': url}
        return Document(content=text_content, metadata=metadata)
        
    except requests.RequestException as e:
        print(f"Error al acceder a la URL {url}: {e}")
        return None

