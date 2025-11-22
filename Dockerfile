# Base image con PyTorch y CUDA 12.1 (Compatible con RTX 30xx/40xx/50xx)
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
# - exiftool: Para leer/escribir metadatos
# - libgl1-mesa-glx: Necesario para OpenCV
# - git: Para clonar repos si es necesario
RUN apt-get update && apt-get install -y \
    exiftool \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios para datos y logs
RUN mkdir -p /app/data/input /app/data/processed /app/data/db /app/logs /app/config

# Copiar el código fuente (aunque se sobreescribe con volumen en dev)
COPY . .

# Comando por defecto (se sobreescribe en docker-compose)
CMD ["python", "src/orchestrator.py"]
