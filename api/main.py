from fastapi import FastAPI

app = FastAPI(
    title="Chatbot API",
    description="API para el chatbot de IA productivo.",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chatbot API!"}

# Aquí se añadirán los endpoints para RAG, ingestión, etc.
