# 🗺️ WildIndex Roadmap

Este documento describe la hoja de ruta de desarrollo para el proyecto WildIndex. Nuestro objetivo es crear la herramienta estándar de código abierto para la indexación de fauna mediante IA.

## 📍 Estado Actual: Fase 3 Completada ✅
Sistema operativo con detección de animales (MegaDetector) y clasificación de especies (BioCLIP) funcionando en producción.

### ✅ Completado

#### Fase 1: Setup e Infraestructura
- [x] **Infraestructura Base:** Docker, NVIDIA GPU, NFS
- [x] **Motor de Orquestación:** BatchProcessor, CheckpointManager
- [x] **Base de Datos:** SQLite con esquema optimizado
- [x] **Inyección de Metadatos:** Escritura de tags XMP/IPTC (Keywords, Description)

#### Fase 2: Procesamiento y Robustez
- [x] **Integración MegaDetector v5:** Detección real de animales/personas/vehículos
- [x] **Soporte RAW:** Manejo seguro de archivos .ARW/.CR2 mediante sidecars .XMP
- [x] **Fallback Storage:** Sistema robusto de almacenamiento con NAS + local backup
- [x] **Dashboard Streamlit:** Visualización de imágenes procesadas y metadatos
- [x] **LLaVA-NeXT (Parcial):** Integración técnica completa, desactivado por limitaciones de `bitsandbytes`

#### Fase 3: Clasificación de Especies (BioCLIP)
- [x] **Integración BioCLIP:** Modelo `imageomics/bioclip` para clasificación taxonómica
- [x] **95 Especies Soportadas:** Mamíferos, aves, reptiles, ganado doméstico
- [x] **Metadata Enriquecida:** Nombres científicos y comunes en XMP/IPTC
- [x] **Filtro por Especie:** Dashboard con búsqueda por taxonomía
- [x] **Validación en Producción:** Probado con cámaras trampa reales (97% precisión en ganado)

## 🚀 Próximos Pasos

### Q1 2026: Búsqueda Semántica y Optimización
*   **Motor de Búsqueda Vectorial:** Implementación de FAISS para indexar embeddings CLIP
*   **API de Búsqueda:** Endpoint REST para consultar "fotos parecidas a esta"
*   **Threshold de Confianza:** Filtrado automático de predicciones de baja confianza (<0.7)
*   **Listas Regionales:** Especies específicas por región (Amazonas, Cerrado, Pantanal)
*   **LLaVA Re-integración:** Resolver `bitsandbytes` CUDA para descripciones de texto

### Q2 2026: Escalabilidad y Comunidad
*   **Soporte Multi-GPU:** Distribución de carga en múltiples tarjetas gráficas
*   **Plugin System:** Arquitectura para que la comunidad añada sus propios detectores
*   **Dashboard de Métricas:** Visualización de estadísticas (conteo de especies, actividad por hora)
*   **Exportación de Datos:** Integración con GBIF y otros estándares de biodiversidad

## 💡 Ideas a Futuro (Backlog)
*   **Re-entrenamiento Automático:** Usar correcciones humanas para mejorar modelos locales
*   **Alertas en Tiempo Real:** Notificación vía Telegram/WhatsApp al detectar especies en peligro
*   **Multi-Label Classification:** Detectar múltiples animales en una sola imagen
*   **Fine-tuning BioCLIP:** Entrenar con dataset regional para mejorar precisión
*   **Mobile App:** Aplicación para revisión y corrección de clasificaciones en campo

## 📊 Métricas de Progreso

| Fase | Estado | Completado | Próximo Hito |
|------|--------|------------|--------------|
| Fase 1: Infraestructura | ✅ Completo | 100% | - |
| Fase 2: Procesamiento | ✅ Completo | 100% | - |
| Fase 3: Clasificación | ✅ Completo | 100% | - |
| Fase 4: Búsqueda Semántica | 🔄 En Planificación | 0% | Q1 2026 |

---
*¿Quieres contribuir? Revisa [CONTRIBUTING.md](../CONTRIBUTING.md)*
