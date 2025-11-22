# 🗺️ WildIndex Roadmap

Este documento describe la hoja de ruta de desarrollo para el proyecto WildIndex. Nuestro objetivo es crear la herramienta estándar de código abierto para la indexación de fauna mediante IA.

## 📍 Estado Actual: Fase 2 (Procesamiento y Robustez)
Estamos construyendo el núcleo del sistema de procesamiento por lotes y la inyección de metadatos.

- [x] **Infraestructura Base:** Docker, NVIDIA GPU, NFS.
- [x] **Motor de Orquestación:** BatchProcessor, CheckpointManager.
- [x] **Base de Datos:** SQLite con esquema optimizado.
- [x] **Inyección de Metadatos:** Escritura de tags XMP/IPTC (Keywords, Description).
- [ ] **Integración de Modelos Reales:** Reemplazar Mock AI con MegaDetector v5 y LLaVA.

## 🚀 Próximos Pasos

### Q4 2025: Inteligencia Visual (Fase 2 - Cont.)
*   **Integración MegaDetector v5:** Detección real de animales/personas/vehículos.
*   **Integración LLaVA-NeXT:** Generación de descripciones detalladas ("Jaguar caminando de noche...").
*   **Soporte RAW:** Manejo seguro de archivos .ARW/.CR2 mediante sidecars .XMP.

### Q1 2026: Búsqueda Semántica (Fase 3)
*   **Motor de Búsqueda Vectorial:** Implementación de FAISS para indexar embeddings CLIP.
*   **API de Búsqueda:** Endpoint REST simple para consultar "fotos parecidas a esta".
*   **Web UI (Prototipo):** Interfaz ligera en Streamlit para visualizar resultados y corregir etiquetas.

### Q2 2026: Escalabilidad y Comunidad
*   **Soporte Multi-GPU:** Distribución de carga en múltiples tarjetas gráficas.
*   **Plugin System:** Arquitectura para que la comunidad añada sus propios detectores (ej: Clasificador de Aves Amazónicas).
*   **Dashboard de Métricas:** Visualización de estadísticas de detección (conteo de especies, actividad por hora).

## 💡 Ideas a Futuro (Backlog)
*   **Re-entrenamiento Automático:** Usar las correcciones humanas para mejorar los modelos locales.
*   **Alertas en Tiempo Real:** Notificación vía Telegram/WhatsApp al detectar especies en peligro crítico.
*   **Integración con GBIF:** Exportación de datos al estándar Global Biodiversity Information Facility.

---
*¿Quieres contribuir? Revisa [CONTRIBUTING.md](../CONTRIBUTING.md) (Próximamente)*
