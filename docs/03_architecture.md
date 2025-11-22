# 🏗️ Análisis de Viabilidad Arquitectónica: Agente de Conservación Ambiental

**Fecha:** 21 Noviembre 2025
**Autor:** Antigravity (AI Architect)
**Estado:** Borrador de Revisión

## 1. Resumen Ejecutivo

El proyecto es **altamente viable** con el hardware propuesto (RTX 5070 Ti 16GB), pero requiere una **orquestación estricta de la memoria VRAM**. No es posible mantener todos los modelos (MegaDetector, LLaVA, CLIP) cargados simultáneamente en la GPU sin optimizaciones agresivas (cuantización).

La arquitectura debe evolucionar de un "Pipeline Monolítico" a un "Pipeline por Etapas (Staged Pipeline)" para maximizar el throughput y evitar OOM (Out Of Memory).

## 2. Análisis de Hardware vs. Modelos

### Restricción Principal: VRAM (16 GB)

| Modelo | Tamaño Original (FP16) | Tamaño Optimizado (4-bit/Int8) | VRAM Requerida (Estimada) | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **MegaDetector v5** | ~250 MB | N/A | ~1 - 2 GB | ✅ Cabe holgadamente |
| **LLaVA-NeXT 13B** | ~26 GB | ~8 GB (4-bit GGUF/EXL2) | ~10 - 12 GB (con contexto) | ⚠️ **Crítico** |
| **OpenCLIP ViT-H/14** | ~2.5 GB | ~2.5 GB (FP16) | ~3 - 4 GB | ⚠️ Justo |
| **Sistema/Display** | N/A | N/A | ~1 - 2 GB | Reservado |

**Conclusión:**
*   **Escenario A (Carga Simultánea):** 2GB (MD) + 10GB (LLaVA) + 3GB (CLIP) + 1GB (Sys) = **16GB+**. **RIESGO ALTO DE OOM.**
*   **Escenario B (Carga Secuencial):** Cargar MD -> Procesar Lote -> Descargar MD -> Cargar LLaVA -> Procesar Lote... **VIABLE.**

## 3. Estrategia de Procesamiento (Pipeline Design)

Para procesar 500GB+ de imágenes de manera eficiente, recomiendo un enfoque de **Pasadas Secuenciales (Multi-Pass Approach)** en lugar de procesar imagen por imagen con todos los modelos.

### Pasada 1: Filtrado Rápido (The "Cull")
*   **Modelos:** Solo MegaDetector v5.
*   **Velocidad:** Muy alta (>20 FPS).
*   **Acción:** Escanear todo el disco. Generar JSONs con bounding boxes. Mover imágenes "Vacías" a una carpeta `archive/empty`.
*   **Resultado:** Reducción del dataset en un 30-50% (típico en cámaras trampa).

### Pasada 2: Inferencia Profunda (The "Brain")
*   **Modelos:** LLaVA-NeXT (4-bit) + OpenCLIP.
*   **Input:** Solo imágenes con detecciones confirmadas en Pasada 1.
*   **Acción:**
    1.  Recortar (Crop) el bounding box detectado.
    2.  Pasar el crop a LLaVA para descripción detallada.
    3.  Pasar la imagen completa a CLIP para embedding.
*   **Optimización:** Usar `llama-cpp-python` o `ExLlamaV2` para LLaVA.

## 4. Almacenamiento y Búsqueda

*   **Base de Datos Relacional (SQL):** SQLite es suficiente para 500k-1M de registros si se maneja bien (WAL mode). PostgreSQL es mejor si se planea acceso concurrente o expansión futura. Recomendación: **SQLite** para empezar (simplicidad, archivo único), migrar a Postgres si crece.
*   **Vector Store:** FAISS es excelente. Usar `IndexFlatL2` para exactitud o `IndexIVFFlat` para velocidad si superamos 1M de vectores.
*   **Sistema de Archivos:** Mantener la estructura de carpetas original en el NAS o reorganizar por `YYYY/MM/DD`? Recomendación: **No modificar estructura original** (read-only) y guardar metadatos apuntando a rutas absolutas. Solo mover archivos si es un requisito explícito de limpieza.

## 5. Riesgos y Mitigaciones

1.  **Alucinaciones de LLaVA:** Los modelos VLM pueden "inventar" animales si la imagen es borrosa.
    *   *Mitigación:* Usar el score de confianza de MegaDetector como filtro primario. Si MD dice "Empty" con 99%, no preguntar a LLaVA.
2.  **Corrupción de Datos:** Fallo de energía durante la escritura en DB.
    *   *Mitigación:* Transacciones ACID en SQLite. Backups automáticos del archivo `.db` y del índice FAISS.
3.  **Tiempo de Proceso:** 500GB pueden tardar días.
    *   *Mitigación:* Checkpoints. El script debe poder reanudarse donde se quedó sin reprocesar nada.

## 6. Veredicto Final

**APROBADO CON OBSERVACIONES.**
El proyecto es técnicamente sólido y el hardware es capaz. La clave del éxito está en la ingeniería de software (gestión de recursos, manejo de errores, pipeline secuencial) más que en la IA pura.

**Siguientes Pasos Recomendados:**
1.  Implementar script de "Pasada 1" (MegaDetector) y medir reducción de volumen.
2.  Prototipar LLaVA en 4-bit para verificar calidad de descripciones vs. velocidad.
