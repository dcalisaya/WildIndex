# 📅 Plan de Implementación Detallado: WildIndex

**Fecha:** 23 Noviembre 2025
**Objetivo:** Hoja de ruta técnica y de producto para el despliegue del Agente de Conservación.

## 1. ⚙️ FASE I: SETUP E INFRAESTRUCTURA (COMPLETADO ✅)

### 1.1. Arquitectura NAS/Cómputo
*   **Montaje de Red:**
    *   Protocolo: **NFSv4** (Preferido sobre SMB por menor latencia en Linux/Docker).
    *   Punto de Montaje: `/mnt/nas_data` en el host, mapeado a `/app/data` en el contenedor.
    *   Permisos: Usuario `1000:1000` (o el ID del usuario del NAS) para evitar problemas de escritura.
*   **Ubicación de Base de Datos:**
    *   **SQLite (.db):** Almacenado en el **SSD local** del host (NVMe) para máxima velocidad de escritura (WAL mode). Backup diario al NAS.

### 1.2. Entorno Dockerizado
*   **Imagen Base:** Ultralytics (PyTorch + CUDA).
*   **Servicios:** `wildindex` con soporte GPU NVIDIA.

## 2. 🚀 FASE II: PROCESAMIENTO Y ROBUSTEZ (COMPLETADO ✅)

### 2.1. Funciones Críticas del Agente
1.  **`BatchProcessor`:** Procesamiento por lotes robusto con manejo de errores.
2.  **`CheckpointManager`:** Persistencia de estado para reanudar tras fallos.
3.  **`MetadataInjector`:** Escritura de XMP/IPTC con `exiftool`.

### 2.2. Diseño de Tabla de Metadatos
Tabla `processed_images` optimizada con columnas para detección (`md_category`) y clasificación (`species_scientific`).

## 3. 🧬 FASE III: CLASIFICACIÓN DE ESPECIES (COMPLETADO ✅)

### 3.1. Integración BioCLIP
*   **Modelo:** `imageomics/bioclip` ejecutándose en CPU.
*   **Capacidad:** Clasificación taxonómica de 95+ especies neotropicales y domésticas.
*   **Precisión:** Validada en producción (97% en ganado).

### 3.2. Dashboard Interactivo
*   **Tecnología:** Streamlit.
*   **Funciones:**
    *   Visualización de imágenes procesadas.
    *   Filtro por especie detectada.
    *   Búsqueda en almacenamiento NAS y local.

## 4. 🌐 FASE IV: BÚSQUEDA SEMÁNTICA Y ESCALABILIDAD (PENDIENTE 🔄)

### 4.1. Motor de Búsqueda Vectorial
*   **Tecnología:** FAISS (Facebook AI Similarity Search).
*   **Modelo:** OpenCLIP (ViT-H/14) para generar embeddings.
*   **Objetivo:** Permitir búsquedas como "animal bebiendo agua" o "jaguar de noche".

### 4.2. API y Web App Avanzada
*   **API REST:** Endpoints para integración con otros sistemas.
*   **Web UI v2:** Interfaz avanzada para gestión de colecciones y corrección de etiquetas.

### 4.3. Optimización LLaVA
*   **Objetivo:** Reactivar descripciones de texto natural.
*   **Estrategia:** Resolver dependencias de `bitsandbytes` o migrar a modelo más ligero.
