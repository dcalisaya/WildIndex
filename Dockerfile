# Base image de Ultralytics (Ya trae PyTorch + YOLO + CUDA configurado)
FROM ultralytics/ultralytics:latest

# Evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema adicionales (exiftool)
RUN apt-get update && apt-get install -y \
    exiftool \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python (solo las extra que no trae ultralytics)
COPY requirements.txt .

# Instalar dependencias extra (faiss, exiftool, etc.)
# Nota: Ultralytics ya trae torch, torchvision, opencv, pandas, etc.
# Downgrade setuptools to avoid "Multiple top-level packages" error with YOLOv5 git install
RUN pip install --no-cache-dir "setuptools<70.0.0" wheel

# Install YOLOv5 manually with --no-build-isolation to force using the downgraded setuptools
RUN pip install --no-cache-dir --no-build-isolation git+https://github.com/ultralytics/yolov5.git@master

RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios para datos y logs
RUN mkdir -p /app/data/input /app/data/processed /app/data/db /app/logs /app/config

# Copiar el código fuente
COPY . .

# Comando por defecto
CMD ["python", "src/orchestrator.py"]
