# 📅 Plan de Implementación Detallado: WildIndex

**Fecha:** 21 Noviembre 2025
**Objetivo:** Hoja de ruta técnica y de producto en 3 fases para el despliegue del Agente de Conservación.

## 1. ⚙️ FASE I: SETUP E INFRAESTRUCTURA (Semanas 1-2)

### 1.1. Arquitectura NAS/Cómputo
*   **Montaje de Red:**
    *   Protocolo: **NFSv4** (Preferido sobre SMB por menor latencia en Linux/Docker).
    *   Punto de Montaje: `/mnt/nas_data` en el host, mapeado a `/app/data` en el contenedor.
    *   Permisos: Usuario `1000:1000` (o el ID del usuario del NAS) para evitar problemas de escritura.
*   **Ubicación de Base de Datos:**
    *   **SQLite (.db):** Almacenado en el **SSD local** del host (NVMe) para máxima velocidad de escritura (WAL mode). Backup diario al NAS.
    *   **FAISS Index:** Generado en RAM/NVMe local, guardado periódicamente en NAS.
    *   *Razón:* SQLite sobre NFS puede causar bloqueos de base de datos.

### 1.2. Entorno Dockerizado
*   **Dockerfile (Base):**
    ```dockerfile
    FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime
    RUN apt-get update && apt-get install -y exiftool libgl1-mesa-glx
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install -r requirements.txt
    COPY . .
    CMD ["python", "orchestrator.py"]
    ```
*   **docker-compose.yml:**
    *   Servicio `wildindex`:
        *   `runtime: nvidia`
        *   `volumes`:
            *   `./config:/app/config`
            *   `/mnt/nas_data/input:/app/data/input:ro` (Lectura)
            *   `/mnt/nas_data/processed:/app/data/processed` (Escritura)
        *   `restart: unless-stopped`

## 2. 🚀 FASE II: PROCESAMIENTO INICIAL Y ROBUSTEZ (Semanas 3-6)

### 2.1. Funciones Críticas del Agente (Python)
1.  **`BatchProcessor.process_chunk()`:**
    *   Maneja la carga de imágenes en lotes (ej: 50 fotos).
    *   Implementa `try/except` por imagen para que una foto corrupta no detenga el lote.
    *   Invoca a MegaDetector y LLaVA secuencialmente.
2.  **`CheckpointManager.save_state()`:**
    *   Guarda un JSON/SQLite cada N imágenes procesadas con el último `file_hash` exitoso.
    *   Permite reiniciar el script y saltar instantáneamente lo ya procesado.
3.  **`MetadataInjector.write_xmp()`:**
    *   Wrapper robusto sobre `exiftool`.
    *   Verifica que el archivo de salida exista y sea válido antes de borrar el original (si aplica).

### 2.2. Diseño de Tabla de Metadatos (Schema)
Tabla `processed_images`:

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | UUID | Identificador único. |
| `file_hash` | VARCHAR(64) | Hash SHA-256 para detectar duplicados. |
| `original_path` | TEXT | Ruta origen en NAS. |
| `capture_timestamp` | DATETIME | Extraído de EXIF o inferido del nombre. |
| `gps_lat/lon` | FLOAT | Coordenadas (si existen). |
| `md_category` | VARCHAR | 'animal', 'person', 'vehicle', 'empty'. |
| `md_confidence` | FLOAT | Confianza de MegaDetector (0.0 - 1.0). |
| `llava_caption` | TEXT | Descripción generada ("Jaguar caminando..."). |
| `species_prediction` | VARCHAR | Especie sugerida (requiere validación). |
| `embedding_id` | INT | Puntero al índice FAISS. |

### 2.3. Estrategia de Validación (QA)
*   **Muestreo Aleatorio:** Script que copia el 1% de las imágenes procesadas a una carpeta `QA_Review`.
*   **Validación Humana:** Un revisor humano verifica ese 1% y marca "Correcto/Incorrecto" en un CSV simple.
*   **Métrica de Éxito:** Si el error es < 5%, se aprueba el lote completo.

## 3. 🌐 FASE III: PRODUCTO OPEN SOURCE Y ESCALABILIDAD (Semanas 7+)

### 3.1. Estructura de Repositorio OSS (`WildIndex-Core`)
*   `/core`: Lógica agnóstica (Detectores, Inyectores).
*   `/drivers`: Adaptadores para modelos específicos (MDv5, LLaVA).
    *   `CONTRIBUTING.md`: "Cómo añadir tu propio modelo de fauna local". Guía para crear una clase que herede de `BaseDetector`.
*   `/deploy`: Scripts de Ansible/Docker.
*   `/examples`: Configs de ejemplo para diferentes NAS (Synology, QNAP, TrueNAS).

### 3.2. Prototipo de Interfaz de Búsqueda (Web App)
Componentes clave (Streamlit):
1.  **Barra de Búsqueda Semántica:** Input de texto que convierte a embedding CLIP y consulta FAISS.
2.  **Galería de Resultados:** Grid de imágenes con lazy-loading desde el NAS.
3.  **Panel de Detalles:** Muestra los metadatos XMP y permite corregir la especie manualmente (Feedback Loop).

### 3.3. Propuesta de Valor Recurrente (Servicio)
*   **Suscripción de Mantenimiento:**
    *   Actualización trimestral de modelos (State-of-the-Art).
    *   Monitoreo de salud del NAS y Base de Datos.
*   **Training Personalizado:**
    *   Fine-tuning de un modelo clasificador (ResNet/YOLO) específico para la fauna de *esa* reserva, usando las fotos validadas por ellos.
