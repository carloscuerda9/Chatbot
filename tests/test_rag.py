# tests/test_rag.py

import pytest
from rag.core import RAGSystem

def test_rag_system_initialization():
    rag_system = RAGSystem()
    assert isinstance(rag_system, RAGSystem)

def test_rag_system_query_response():
    rag_system = RAGSystem()
    question = "¿Cuál es la capital de Francia?"
    response = rag_system.query(question)
    assert "Respuesta generada para:" in response
    assert question in response

