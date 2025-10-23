# Makefile

.PHONY: install run build_docker run_docker clean ingest run_streamlit test

install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt

run:
	@echo "Iniciando la API de FastAPI..."
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

build_docker:
	@echo "Construyendo la imagen Docker..."
	docker build -t chatbot-api -f docker/Dockerfile .

run_docker:
	@echo "Ejecutando el contenedor Docker..."
	docker run -p 8000:8000 chatbot-api

clean:
	@echo "Limpiando archivos temporales y caché..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf index/vector/faiss_index # Eliminar el índice FAISS


ingest:
	@echo "Iniciando el proceso de ingesta y creación de índice FAISS..."
	python ingest/pipelines/ingest_all.py

run_streamlit:
	@echo "Iniciando la aplicación Streamlit..."
	streamlit run app/main_app.py

test:
	@echo "Ejecutando tests..."
	pytest