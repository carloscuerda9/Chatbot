# Chatbot de IA Productivo

## Rol y Objetivo

Este proyecto tiene como objetivo desarrollar un chatbot de IA productivo, enfocado en la creación de aplicaciones y agentes de IA (RAG, automatización, copilotos) que entreguen código y arquitectura lista para correr.

## Arquitectura Propuesta

```
[Fuentes de Datos (PDFs, Docs, Web)]
       ↓ (Ingesta)
[Módulo de Carga y Preprocesamiento (Loaders, Chunking, Metadata)]
       ↓
[Módulo de Indexado (Embeddings, Vector DB - FAISS/Chroma/PGVector)]
       ↓
[Módulo RAG (Retrieval-Augmented Generation)]
       ↓
[API/UI (FastAPI/Streamlit)]
       ↓
[Observabilidad (Logging, Tracing, Costes, Tests)]
```

## Stack Sugerido

*   **Lenguaje:** Python
*   **Framework Web/UI:** FastAPI (para API) y Streamlit (para UI interactiva)
*   **Orquestación LLM/RAG:** LangChain o LlamaIndex
*   **Base de Datos Vectorial:** FAISS (local) o Chroma/PGVector (persistente)
*   **Modelos LLM/Embeddings:** OpenAI o Gemini (configurables vía `.env`)
*   **Autenticación:** Básica (si es requerida)

## Configuración del Entorno

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd chatbox
    ```
2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurar variables de entorno:**
    Copia el archivo `.env.example` a `.env` y rellena las variables necesarias (ej. claves de API de OpenAI/Gemini).
    ```bash
    cp .env.example .env
    ```

## Cómo Ejecutar

*(Instrucciones detalladas se añadirán a medida que se implementen los módulos de API/UI.)*

## Cómo Probar

*(Instrucciones detalladas para ejecutar tests se añadirán a medida que se implementen.)*

## DevOps

*(Instrucciones para Dockerfile y despliegue se añadirán a medida que se implementen.)*

## Observabilidad

*(Detalles sobre logging, tracing y gestión de costes se añadirán a medida que se implementen.)*
