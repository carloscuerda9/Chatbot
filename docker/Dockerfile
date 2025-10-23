# Dockerfile

# Usa una imagen base de Python
FROM python:3.10-slim-buster

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que correrá la API (FastAPI por defecto usa 8000)
EXPOSE 8000

# Comando para ejecutar la aplicación usando Uvicorn
# Asume que tu aplicación FastAPI está en api/main.py y la instancia se llama 'app'
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
