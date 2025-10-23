from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document as LCDocument
from typing import List, Dict
import os

class Answerer:
    def __init__(self, llm_provider: str = "openai", model_name: str = "gpt-3.5-turbo"):
        self.llm_provider = llm_provider
        self.model_name = model_name

        if self.llm_provider == "openai":
            self.llm = ChatOpenAI(model=self.model_name, temperature=0.7)
        elif self.llm_provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.7)
        else:
            raise ValueError(f"Proveedor LLM no soportado: {llm_provider}. Use 'openai' o 'gemini'.")

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente útil que responde preguntas basándose únicamente en el contexto proporcionado. Si la respuesta no está en el contexto, di 'No hay evidencia suficiente en el contexto proporcionado para responder a esta pregunta.'. Cita tus fuentes al final de la respuesta, mencionando el nombre del archivo o la fuente."),
            ("human", "Contexto: {context}\n\nPregunta: {question}")
        ])
        self.output_parser = StrOutputParser()
        self.chain = self.prompt_template | self.llm | self.output_parser

    def generate_answer(self, question: str, documents: List[LCDocument]) -> Dict:
        """
        Genera una respuesta a la pregunta basándose en los documentos proporcionados.
        Devuelve la respuesta y las fuentes citadas.
        """
        context_str = "\n\n".join([doc.page_content for doc in documents])
        
        # Recopilar fuentes únicas para citación
        sources = set()
        for doc in documents:
            if "file_name" in doc.metadata:
                sources.add(doc.metadata["file_name"])
            elif "source" in doc.metadata: # Para el caso de documentos dummy o de prueba
                sources.add(doc.metadata["source"])
        
        response = self.chain.invoke({"context": context_str, "question": question})
        
        # Añadir citaciones al final de la respuesta
        if sources:
            response += "\n\nFuentes: " + ", ".join(sorted(list(sources)))

        return {"answer": response, "sources": list(sources)}

if __name__ == "__main__":
    # Ejemplo de uso:
    # Asegúrate de tener las variables de entorno GOOGLE_API_KEY o OPENAI_API_KEY configuradas
    
    # Inicializar el generador de respuestas
    try:
        # answerer = Answerer(llm_provider="gemini", model_name="gemini-pro")
        answerer = Answerer(llm_provider="openai") # Usará gpt-3.5-turbo por defecto
    except Exception as e:
        print(f"Error al inicializar el Answerer: {e}")
        print("Asegúrate de que tu API Key (OPENAI_API_KEY o GOOGLE_API_KEY) esté configurada correctamente.")
        exit()

    # Documentos de ejemplo (simulando los recuperados por el Retriever)
    sample_docs = [
        LCDocument(page_content="La capital de Francia es París. París es famosa por la Torre Eiffel y el Museo del Louvre.", metadata={"file_name": "guia_turismo.pdf", "page": 10}),
        LCDocument(page_content="El río Sena atraviesa París. Es un destino turístico popular.", metadata={"file_name": "historia_paris.txt", "page": 2}),
        LCDocument(page_content="La Torre Eiffel fue construida por Gustave Eiffel para la Exposición Universal de 1889.", metadata={"file_name": "historia_paris.txt", "page": 5}),
    ]

    question = "¿Qué atracciones turísticas hay en París y quién construyó la Torre Eiffel?"
    result = answerer.generate_answer(question, sample_docs)

    print(f"\nPregunta: {question}")
    print(f"\nRespuesta: {result['answer']}")
    print(f"\nFuentes citadas: {result['sources']}")

    question_no_evidence = "¿Cuál es la capital de Alemania?"
    result_no_evidence = answerer.generate_answer(question_no_evidence, sample_docs)
    print(f"\nPregunta: {question_no_evidence}")
    print(f"\nRespuesta: {result_no_evidence['answer']}")
