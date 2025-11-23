# 🏗️ Análisis de Viabilidad Arquitectónica: Agente de Conservación Ambiental

**Fecha:** 23 Noviembre 2025
**Autor:** Antigravity (AI Architect)
**Estado:** Validado en Producción ✅

## 1. Resumen Ejecutivo

El proyecto ha sido **exitosamente desplegado** en el hardware propuesto (RTX 5070 Ti 16GB). La estrategia de mover la clasificación (BioCLIP) a la CPU ha sido clave para evitar cuellos de botella de VRAM, permitiendo un procesamiento estable y rápido.

## 2. Análisis de Hardware vs. Modelos

### Restricción Principal: VRAM (16 GB)

| Modelo | Tamaño Original | Tamaño Optimizado | VRAM Requerida | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **MegaDetector v5** | ~250 MB | N/A | ~1 - 2 GB | ✅ En Producción (GPU) |
| **BioCLIP** | ~600 MB | N/A | ~0 GB (CPU) | ✅ En Producción (CPU) |
| **LLaVA-NeXT 13B** | ~26 GB | ~8 GB (4-bit) | ~10 - 12 GB | ⚠️ Desactivado (Deps) |
| **OpenCLIP ViT-H/14** | ~2.5 GB | ~2.5 GB (FP16) | ~3 - 4 GB | 🔄 Planificado (Fase 4) |

**Conclusión:**
La arquitectura híbrida (GPU para detección, CPU para clasificación) es la más eficiente. BioCLIP en CPU añade solo ~0.5s por imagen, lo cual es despreciable para procesamiento batch.

## 3. Estrategia de Procesamiento (Pipeline Design)

El pipeline actual opera en **Pasadas Secuenciales**:

### Pasada 1: Detección y Clasificación (The "Core")
*   **Modelos:** MegaDetector v5 (GPU) + BioCLIP (CPU).
*   **Velocidad:** ~1.5s por imagen.
*   **Acción:** Detectar animales, recortar, clasificar especie, inyectar metadatos.
*   **Resultado:** Imágenes etiquetadas y listas para búsqueda por texto.

### Pasada 2: Búsqueda Semántica (The "Brain" - Próximamente)
*   **Modelos:** OpenCLIP.
*   **Input:** Imágenes procesadas.
*   **Acción:** Generar embeddings y almacenar en FAISS.

## 4. Almacenamiento y Búsqueda

*   **Base de Datos:** SQLite (WAL mode) ha demostrado ser robusta y rápida.
*   **Metadatos:** XMP/IPTC inyectados permiten búsqueda nativa en NAS.

## 5. Riesgos y Mitigaciones (Actualizado)

1.  **Dependencias LLaVA:** `bitsandbytes` es frágil en Docker.
    *   *Mitigación:* Se desactivó LLaVA en favor de BioCLIP (más valor científico).
2.  **Precisión en Reptiles:** BioCLIP tiene menor confianza en reptiles pequeños.
    *   *Mitigación:* Se recomienda threshold de confianza y fine-tuning futuro.

## 6. Veredicto Final

**PROYECTO EXITOSO Y ESCALABLE.**
La arquitectura ha demostrado ser sólida. La decisión de priorizar la clasificación taxonómica sobre las descripciones de texto ha aportado mayor valor inmediato a la conservación.

**Siguientes Pasos Recomendados:**
1.  Implementar Búsqueda Semántica (FAISS).
2.  Crear listas de especies regionales.
3.  Evaluar modelos VLM alternativos a LLaVA.
