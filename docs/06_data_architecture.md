# 🏗️ Arquitectura de Datos y Estándares

Este documento define formalmente los estándares de metadatos, el esquema de base de datos y la estrategia de almacenamiento para WildIndex.

## 1. Estándares de Metadatos (Metadata Standards)

Para garantizar la interoperabilidad con software de gestión de activos digitales (DAM) como Synology Photos, Adobe Lightroom, DigiKam y Bridge, WildIndex se adhiere estrictamente a los estándares XMP e IPTC.

### 1.1. Mapeo de Campos (Field Mapping)

| Fuente de Datos | Campo Interno | Estándar XMP (Preferido) | Estándar IPTC (Legacy) | Estándar EXIF |
| :--- | :--- | :--- | :--- | :--- |
| **MegaDetector** | `md_category` | `XMP-dc:Subject` | `IPTC:Keywords` | - |
| **Clasificador** | `species_prediction` | `XMP-dc:Subject` | `IPTC:Keywords` | - |
| **WildIndex** | "WildIndex AI" | `XMP-dc:Subject` | `IPTC:Keywords` | - |
| **LLaVA** | `llava_caption` | `XMP-dc:Description` | `IPTC:Caption-Abstract` | `EXIF:ImageDescription` |
| **Agente** | "WildIndex v1.0" | `XMP-xmp:CreatorTool` | - | `EXIF:Software` |

### 1.2. Estrategia de Escritura (Sidecars vs. Embedded)
*   **JPEGs / PNGs:** Inyección directa (Embedded). Se utiliza `exiftool -overwrite_original` sobre la **copia** procesada. Nunca sobre el original en el input.
*   **RAWs (ARW, CR2, NEF):** Se debe generar un archivo *sidecar* `.xmp` con el mismo nombre base.
    *   *Ejemplo:* `DSC001.ARW` -> `DSC001.xmp`
    *   *Razón:* Evitar corrupción de archivos binarios propietarios y permitir que Lightroom lea los metadatos automáticamente.

## 2. Esquema de Base de Datos (Database Schema)

WildIndex utiliza **SQLite** en modo WAL (Write-Ahead Logging) para persistencia local rápida y fiable.

### 2.1. Tabla: `processed_images`

| Columna | Tipo | Descripción | Indexado |
| :--- | :--- | :--- | :--- |
| `id` | TEXT (PK) | Hash SHA-256 del archivo. Identificador único inmutable. | ✅ |
| `file_hash` | TEXT | Redundante con ID, mantenido por claridad. | ✅ |
| `original_path` | TEXT | Ruta absoluta del archivo en el volumen de entrada. | |
| `file_name` | TEXT | Nombre del archivo (ej. `IMG_1234.JPG`). | |
| `file_size` | INTEGER | Tamaño en bytes. | |
| `capture_timestamp` | TEXT | Fecha de captura (ISO 8601) extraída de EXIF. | |
| `md_category` | TEXT | Categoría principal detectada (animal, person, vehicle, empty). | ✅ |
| `md_confidence` | REAL | Nivel de confianza de la detección (0.0 - 1.0). | |
| `md_bbox` | TEXT | JSON Array `[ymin, xmin, ymax, xmax]` (Norma MegaDetector). | |
| `llava_caption` | TEXT | Descripción generada por LLaVA. | |
| `species_prediction` | TEXT | Especie específica predicha (ej. "Panthera onca"). | |
| `status` | TEXT | Estado del proceso: `PENDING`, `PROCESSED`, `ERROR`. | ✅ |
| `error_message` | TEXT | Detalle del error si `status == ERROR`. | |
| `created_at` | DATETIME | Fecha de registro en el sistema. | |
| `updated_at` | DATETIME | Última modificación del registro. | |

### 2.2. Índices y Optimización
*   `idx_file_hash`: Búsqueda O(1) para evitar duplicados (Checkpoint System).
*   `idx_status`: Recuperación rápida de lotes pendientes o fallidos.
*   `idx_md_category`: Filtrado rápido para estadísticas o post-procesamiento específico.

## 3. Almacenamiento Vectorial (Vector Store) - *Fase 3*

Para la búsqueda semántica ("buscar fotos parecidas a esta"), se utilizará **FAISS** (Facebook AI Similarity Search).

*   **Modelo de Embeddings:** CLIP (ViT-L/14).
*   **Dimensión:** 768 dimensiones.
*   **Índice:** `IndexFlatL2` (Búsqueda exacta) o `IndexIVFFlat` (Búsqueda aproximada rápida para >1M imágenes).
*   **Persistencia:** El índice FAISS se guarda como un archivo binario `.index` junto a la base de datos SQLite.
*   **Mapeo:** Se mantiene un mapeo `ID (int) -> file_hash (str)` en SQLite para relacionar los vectores con los archivos.
