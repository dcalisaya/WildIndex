## 1. 🎯 Misión y Alcance (Mission and Scope)

*   **Misión del Agente:** Procesar de forma privada y local grandes volúmenes de imágenes de conservación ambiental, generar metadatos ricos (descripción, detección, embeddings), e indexar los resultados para la búsqueda avanzada y almacenamiento en NAS.
*   **Volumen Objetivo:** Escala de Terabytes (Tanto JPEGs como RAW de alta resolución).
*   **Hardware de Ejecución:** GPU NVIDIA RTX 5070 Ti (16GB VRAM), $64$ GB RAM, Linux/Windows.
*   **Salida Final (Output):** Banco de imágenes indexado y queryable (capaz de ser consultado) en el almacenamiento de red.

## 2. 🧱 Arquitectura del Pipeline (Pipeline Architecture)

Describe la secuencia de procesamiento que el Agente Orquestador seguirá, especificando qué modelo se usa en cada etapa.

### Ingesta de Datos (Data Ingestion):
*   **Función:** Monitorear la carpeta de entrada de imágenes en el NAS.
*   **Herramienta:** Python os y pathlib.

### Filtro Rápido y Detección (MegaDetector):
*   **Modelo:** MegaDetector v5.
*   **Tarea:** Identificar bounding boxes (cajas delimitadoras) para Animal, Persona, Vehículo o Vacío. Descarta imágenes "Vacías" para ahorrar tiempo de procesamiento posterior.

### Clasificación de Especies (BioCLIP):
*   **Modelo:** BioCLIP (`imageomics/bioclip`).
*   **Tarea:** Clasificación taxonómica precisa (95+ especies) utilizando los recortes (crops) generados por MegaDetector.
*   **Ejecución:** CPU (optimizado).

### Descripción Detallada (Captioning & VQA) - *Desactivado Temporalmente*:
*   **Modelo:** LLaVA-NeXT 13B (o 34B).
*   **Tarea:** Generación de descripciones detalladas. Actualmente desactivado por dependencias de compilación CUDA (`bitsandbytes`), priorizando BioCLIP.

### Extracción de Features (Embedding Generation) - *Próximamente*:
*   **Modelo:** OpenCLIP (ViT-H/14).
*   **Tarea:** Genera un vector de embedding de alta calidad para la búsqueda semántica.

### Indexación y Almacenamiento (Indexing & Storage):
*   **Herramientas:** SQLite (metadatos), NAS (imágenes), FAISS (futuro índice vectorial).
*   **Tarea:** Almacenar metadatos enriquecidos (XMP/IPTC) y organizar archivos.

## 3. 🧠 Componentes Clave y Modelos

Detalla el stack técnico necesario para la implementación local.

| Tipo de Componente | Propósito | Tecnología/Modelo Recomendado |
| :--- | :--- | :--- |
| **Orquestación** | Gestionar la secuencia y el flujo de trabajo. | Python Scripting (BatchProcessor) |
| **Aceleración GPU** | Aprovechar la 5070 Ti. | PyTorch + CUDA Toolkit |
| **Detección** | Identificación de fauna. | MegaDetector v5 |
| **Clasificación** | Identificación taxonómica de especies. | BioCLIP (CPU) |
| **Descripción/VQA** | Generación de metadatos de lenguaje. | LLaVA-NeXT (Desactivado) |
| **Búsqueda Semántica** | Extracción de vectores. | OpenCLIP (ViT-H/14) |
| **Base de Datos** | Almacenamiento de metadatos. | SQLite (WAL Mode) |

## 4. 🔏 Consideraciones de Privacidad y Seguridad

*   **Principio de Localidad:** Todo el procesamiento debe ejecutarse localmente en la GPU asignada.
*   **Cero API Externa:** Prohibido el uso de servicios en la nube o APIs de terceros (como Claude API, Google Vision, etc.) para la privacidad de los datos de la ONG.
*   **Aislamiento de Entorno:** Utilizar contenedores Docker/Singularity para encapsular el entorno de ejecución, asegurando que las dependencias sean estables y el código esté aislado de la red si no es necesario.

## 5. ⚙️ Despliegue y Mantenimiento

*   **Despliegue Inicial:** Configuración del entorno de Python, instalación de dependencias de CUDA y PyTorch, y descarga de pesos de los modelos (model weights).
*   **Ejecución:** El agente se ejecuta en modo Batch (procesando todo el dataset) y luego en modo Watchdog (monitoreando nuevas imágenes añadidas).
*   **Mantenimiento:** El pipeline requiere revisiones periódicas de los modelos (e.g., actualizar a una versión más reciente de LLaVA o MegaDetector).


