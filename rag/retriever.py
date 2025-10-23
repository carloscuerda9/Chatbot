from langchain_core.documents import Document as LCDocument
from typing import List
import re

from chatbox.index.vector.faiss_index import FAISSIndexer

class Retriever:
    def __init__(self, indexer: FAISSIndexer):
        self.indexer = indexer

    def _get_priority_score(self, doc: LCDocument) -> int:
        metadata = doc.metadata
        source_type = metadata.get("source_type", "unknown")
        file_path = metadata.get("file_path", "")

        if source_type == "video_audio":
            return 300
        if source_type == "web_page":
            return 100
        if source_type in ["pdf", "txt_md", "docx", "pptx", "xlsx_csv"]:
            base_score = 200
            year_match = re.search(r'\\(202[0-9])', file_path)
            if year_match:
                year = int(year_match.group(1))
                year_bonus = year - 2000
                return base_score + year_bonus
            return base_score
        return 0

    def retrieve(self, query: str, k: int = 10) -> List[LCDocument]:
        print(f"Realizando recuperación para la consulta: '{query}'")
        
        # 1. Recuperación Amplia (Fetch)
        initial_results = self.indexer.search(query, k=50)
        print(f"Recuperados {len(initial_results)} documentos iniciales para re-ranking.")

        if not initial_results:
            return []

        # 2. Re-ranking Avanzado (Doble Filtro)
        query_keywords = set(query.lower().split())
        
        scored_docs = []
        for i, doc in enumerate(initial_results):
            content = doc.page_content.lower()
            
            # Score de similitud base (más alto para los primeros resultados)
            similarity_score = 1.0 / (i + 1)
            
            # Score de palabras clave (bonus si contiene todas las palabras)
            keyword_score = 1.0 if all(keyword in content for keyword in query_keywords) else 0.0
            
            # Score de prioridad de fuente
            priority_score = self._get_priority_score(doc)

            # Puntuación final combinada
            # Damos un peso enorme a la prioridad y a las palabras clave
            final_score = (priority_score * 100) + (keyword_score * 50) + similarity_score
            scored_docs.append((doc, final_score))

        # Ordenar por la puntuación final combinada
        reranked_results = sorted(scored_docs, key=lambda x: x[1], reverse=True)
        
        print("\n--- Resultados después de Re-ranking Avanzado ---")
        final_docs = []
        for i, (doc, score) in enumerate(reranked_results[:k]):
            final_docs.append(doc)
            print(f"{i+1}. (Score: {score:.2f}) {doc.metadata.get('file_name')} - Tipo: {doc.metadata.get('source_type')}")

        return final_docs
