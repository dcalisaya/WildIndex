# 🛡️ Análisis Crítico y Hoja de Ruta de Escalamiento

**Fecha:** 21 Noviembre 2025
**Tipo:** Revisión de Arquitectura y Producto
**Objetivo:** Validar la estrategia de "Consultoría + Open Source" y blindar la implementación técnica.

## 1. 🚨 Riesgos Críticos y Mitigaciones

| Riesgo | Impacto | Mitigación Propuesta |
| :--- | :--- | :--- |
| **"Vendor Lock-in" con Synology** | Medio | Si Synology cambia su indexador, la búsqueda falla. **Solución:** Usar estándares estrictos (XMP/IPTC) que sean legibles por cualquier software (Adobe Bridge, Lightroom, DigiKam), no solo Synology. |
| **Alucinaciones de IA** | Alto | LLaVA inventando animales en fotos borrosas. **Solución:** Implementar "Confidence Thresholds". Si `confidence < 0.7`, etiquetar como `Review_Required`. Nunca borrar originales. |
| **Corrupción de Metadatos** | Alto | `exiftool` corrompiendo binarios RAW. **Solución:** Trabajar siempre sobre *sidecar files* (.xmp) para RAWs, y solo incrustar en JPEGs copia. **Nunca tocar el RAW original.** |
| **Desbordamiento de VRAM** | Crítico | OOM matando el proceso a mitad de la noche. **Solución:** Pipeline estrictamente secuencial con `gc.collect()` y `torch.cuda.empty_cache()` agresivo entre etapas. |

## 2. 🛠️ Mejoras Técnicas y de Arquitectura

### A. Estandarización de Metadatos (The "Universal Language")
Para que esto sea útil para *cualquier* ONG, no podemos inventar tags. Debemos usar el esquema **Darwin Core** o estándares IPTC.
*   **Propuesta:**
    *   `XMP-dc:Subject`: Especie (e.g., "Panthera onca").
    *   `XMP-dc:Description`: Caption generado por LLaVA.
    *   `XMP-xmp:CreatorTool`: "ConservationAI-Agent v1.0".
    *   **NUEVO:** `XMP-mwg-rs:RegionInfo`: Inyectar las coordenadas del Bounding Box en el estándar de metadatos de regiones. Esto permite que otros visualizadores muestren el recuadro sobre el animal.

### B. Versionado de Modelos (Data Lineage)
Los modelos cambian. Un "Jaguar" detectado por MegaDetector v5.0 no es lo mismo que uno por v6.0.
*   **Mejora:** Inyectar tags técnicos ocultos o visibles:
    *   `Machine:ModelName`: "MegaDetector v5a"
    *   `Machine:ModelVersion`: "5.0.0"
    *   `Machine:Confidence`: "0.98"
Esto permite "re-procesar" solo las fotos antiguas cuando salga un modelo mejor.

### C. Pipeline "Stateful" con SQLite
No confiar en el sistema de archivos para saber qué se procesó.
*   **Mejora:** Una tabla `processing_log` en SQLite.
    *   `file_hash` (PK), `file_path`, `status` (PENDING, PROCESSED, FAILED), `last_updated`, `model_version`.
    *   Esto permite reanudar el trabajo instantáneamente tras un corte de luz.

## 3. 📦 Estrategia de Producto: Open Source vs. Servicio

### ¿Qué es Open Source? (El "Core")
*   El orquestador Python (`pipeline.py`).
*   Los adaptadores para MegaDetector y LLaVA.
*   La lógica de escritura de metadatos XMP.
*   **Licencia:** Apache 2.0 (Permisiva, amigable con empresas).

### ¿Qué es Privado/Servicio? (El "Value Add")
*   **"The Deployer":** Scripts de Ansible/Bash que configuran el NAS, instalan Docker, drivers de NVIDIA y configuran los cron jobs automáticamente.
*   **Dashboard de Auditoría:** Una pequeña web app que muestra "Fotos procesadas hoy", "Especies detectadas esta semana".
*   **Soporte de Hardware:** Garantía de que funciona en *ese* hardware específico.

## 4. 🚀 Hoja de Ruta Técnica Refinada

### Fase 1: Cimientos Robustos (Semanas 1-2)
1.  **Dockerización:** Crear imagen `conservation-ai:base` con PyTorch y drivers pre-compilados (ahorra horas de install en cliente).
2.  **Pipeline V1 (Solo Detección):** MegaDetector -> JSON -> XMP Injection.
3.  **Validación Synology:** Confirmar que Synology Photos lee los tags XMP inyectados y las regiones.

### Fase 2: Enriquecimiento (Semanas 3-4)
1.  **Pipeline V2 (Captioning):** Integrar LLaVA-NeXT cuantizado (4-bit).
2.  **Filtros de Calidad:** Lógica para descartar fotos "demasiado oscuras" o "borrosas" antes de gastar GPU en ellas.

### Fase 3: "Enterprise Ready" (Mes 2+)
1.  **Reportes Automáticos:** Generar PDF semanal con conteo de especies.
2.  **API Local:** Exponer una API REST simple (`GET /search?q=jaguar`) para integraciones futuras.

## 5. 💡 Sugerencias de Valor Inmediato ("Quick Wins")

1.  **"El Eliminador de Basura":**
    *   Lo primero que debe hacer el script es mover todas las fotos "Vacías" (hojas moviéndose) a una carpeta `_TRASH_CANDIDATE`.
    *   **Valor:** El cliente recupera espacio en disco y limpia su galería inmediatamente. Esto vende el proyecto solo.

2.  **Renombrado Inteligente:**
    *   Opcional: Renombrar archivos a `YYYYMMDD_HHMMSS_Especie_ID.jpg`. Ayuda mucho si sacan los archivos del NAS.

## 6. Veredicto de Viabilidad Escalable

El proyecto tiene un potencial enorme de replicabilidad. La clave no es la IA (que es commodity), sino la **integración perfecta con el flujo de trabajo existente (NAS)**.

*   **Recomendación Final:** No construyas una nueva interfaz de usuario (UI) todavía. Tu "UI" es el explorador de archivos y Synology Photos. Haz que esos funcionen perfecto con tus metadatos. Esa es la victoria rápida y escalable.
