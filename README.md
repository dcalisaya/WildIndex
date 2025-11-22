# 🌿 WildIndex: La inteligencia artificial que cataloga la conservación

> **Inteligencia Artificial Local para la Indexación y Búsqueda de Fauna en NAS.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Planning-yellow.svg)](docs/04_implementation_plan.md)

## 📖 Documentación del Proyecto

Toda la documentación estratégica y técnica ha sido organizada en la carpeta `docs/`:

1.  **[Definición del Agente](docs/00_agent_definition.md):** Misión, alcance y visión general del sistema.
2.  **[Estrategia de Producto](docs/01_strategy.md):** Filosofía "Open Core", integración con Synology y modelo de negocio.
3.  **[Análisis Crítico](docs/02_critical_analysis.md):** Evaluación de riesgos, mejoras de arquitectura y hoja de ruta de escalabilidad.
4.  **[Análisis de Arquitectura](docs/03_architecture.md):** Viabilidad técnica, hardware (RTX 5070 Ti) y selección de modelos (MegaDetector, LLaVA, CLIP).
5.  **[Plan de Implementación](docs/04_implementation_plan.md):** Guía paso a paso en 3 fases (Setup, Ejecución, Producto).

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

## 🤝 Contribución

Este proyecto sigue una filosofía **Open Core**. El motor de procesamiento es de código abierto bajo la licencia Apache 2.0.

---
*Desarrollado con ❤️ para la conservación de la biodiversidad.*
