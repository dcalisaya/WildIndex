# 🌿 WildIndex: La inteligencia artificial que cataloga la conservación

> **Inteligencia Artificial Local para la Indexación y Búsqueda de Fauna en NAS.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Phase_3_Complete-green.svg)](docs/ROADMAP.md)

## 📖 Documentación del Proyecto

Toda la documentación estratégica y técnica ha sido organizada en la carpeta `docs/`:

1.  **[Definición del Agente](docs/00_agent_definition.md):** Misión, alcance y visión general del sistema.
2.  **[Estrategia de Producto](docs/01_strategy.md):** Filosofía "Open Core", integración con Synology y modelo de negocio.
3.  **[Análisis Crítico](docs/02_critical_analysis.md):** Evaluación de riesgos, mejoras de arquitectura y hoja de ruta de escalabilidad.
4.  **[Análisis de Arquitectura](docs/03_architecture.md):** Viabilidad técnica, hardware (RTX 5070 Ti) y selección de modelos (MegaDetector, LLaVA, CLIP).
5.  **[Plan de Implementación](docs/04_implementation_plan.md):** Guía paso a paso en 3 fases (Setup, Ejecución, Producto).
6.  **[Roadmap](docs/ROADMAP.md):** Hoja de ruta de desarrollo y estado actual del proyecto.

## ✨ Características

*   **🧬 Species Classification (New - Phase 3):**
    *   **BioCLIP Integration:** Accurate taxonomic classification with 95+ species support
    *   **Scientific & Common Names:** Full taxonomy metadata (e.g., "Bos taurus (Cattle)")
    *   **High Accuracy:** 97% confidence on domestic animals, validated with real camera trap data
    *   **Searchable Metadata:** Species names embedded in XMP/IPTC for Lightroom/Bridge compatibility
*   **🧠 Visual Intelligence:**
    *   **MegaDetector v5:** State-of-the-art detection for animals, people, and vehicles
    *   **LLaVA-NeXT (Planned):** Natural language descriptions (currently disabled due to `bitsandbytes` CUDA requirements)
*   **📸 RAW Support:**
    *   Native support for `.ARW`, `.CR2`, and other RAW formats
    *   **Non-destructive:** Generates standard `.xmp` sidecar files compatible with Lightroom, Capture One, and Bridge
*   **⚡ High Performance:**
    *   **GPU Acceleration:** Optimized for NVIDIA GPUs (CUDA 12.1)
    *   **Smart Batching:** Processes thousands of images efficiently
    *   **CPU Fallback:** Automatically switches to CPU if GPU is unavailable
*   **📊 Metadata Injection:** Writes XMP/IPTC tags directly to files (or sidecars) for seamless workflow integration
*   **🎨 Interactive Dashboard:** Streamlit-based UI with species filtering and confidence scores
*   **🔍 Vector Search (Coming Soon):** Semantic search capabilities using CLIP and FAISS

## 🚀 Inicio Rápido (Próximamente)

El proyecto se encuentra actualmente en la **Fase 1: Setup e Infraestructura**.

### Prerrequisitos
*   NVIDIA GPU (8GB+ VRAM recomendado).
*   Docker & NVIDIA Container Toolkit.
*   NAS montado vía NFS.

### Estructura de Carpetas
```bash
.
├── docs/               # Documentación del proyecto
├── src/                # Código fuente (Próximamente)
├── config/             # Archivos de configuración
├── docker-compose.yml  # Orquestación de contenedores
└── README.md           # Este archivo
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to help improve WildIndex.es

---
*Desarrollado con ❤️ para la conservación de la biodiversidad.*
