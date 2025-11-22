# ♟️ Estrategia de Implementación: Servicio + Open Source

**Fecha:** 21 Noviembre 2025
**Contexto:** Proyecto de Conservación + Producto Open Source (Comunidad)

## 1. Filosofía del Producto: "Open Core"

Para equilibrar la implementación específica con la contribución (Open Source), recomiendo una estrategia de **"Motor Público, Configuración Privada"**.

*   **El Motor (Repositorio Público - MIT/Apache 2.0):**
    *   Contiene toda la lógica de IA: MegaDetector, LLaVA, CLIP, FAISS.
    *   Scripts de procesamiento agnósticos (no hardcoded para el cliente).
    *   Dockerfiles genéricos.
    *   *Valor para la comunidad:* Cualquier ONG con hardware similar puede usarlo.

*   **La Implementación (Repositorio Privado o Configs Locales):**
    *   Archivos `.env` con rutas específicas del almacenamiento.
    *   Scripts de despliegue específicos (cron jobs, rutas de backup).
    *   Personalizaciones de marca o reportes específicos.
    *   *Valor:* Capacidad de desplegar, mantener y garantizar que funcione en hardware específico.

## 2. Integración con Almacenamiento (El "Entregable")

El usuario quiere usar su NAS para su trabajo diario. Tienes dos niveles de integración:

### Nivel 1: Inyección de Metadatos (Nativo y Robusto) 🌟 *Recomendado MVP*
En lugar de obligar al usuario a usar una app web nueva, **enriquecemos los archivos existentes**.
*   **Mecanismo:** El agente escribe los resultados de la IA directamente en los estándares EXIF/IPTC/XMP de las imágenes (usando `exiftool`).
    *   **Especie (MegaDetector)** -> `XMP:Subject` / `IPTC:Keywords` (Tags).
    *   **Descripción (LLaVA)** -> `XMP:Description` / `EXIF:ImageDescription` (Caption).
    *   **Fecha/GPS:** Se preservan o corrigen.
*   **Resultado:** **Photo Managers (Synology Photos, Lightroom, etc.)** indexan automáticamente estos tags. El usuario puede buscar "Jaguar" o "Caminando de noche" directamente en la barra de búsqueda.
*   **Ventaja:** Cero curva de aprendizaje. Funciona en móviles y web nativa del NAS.

### Nivel 2: Web UI Personalizada (Valor Añadido)
Una aplicación web ligera (Streamlit o React) corriendo en Docker dentro del NAS (Container Manager).
*   **Función:** Búsqueda semántica real ("Mostrar fotos parecidas a esta", "Buscar animales agresivos").
*   **Uso:** Para consultas avanzadas que los tags simples no resuelven.
*   **Estrategia:** Ofrecer esto como un "Add-on Premium" o fase 2.

## 3. Arquitectura de Hardware (Redundancia)

Dado que hay 2 volúmenes (Producción y Respaldo):
1.  **Volumen 1 (Producción):**
    *   Carpeta `Input`: Donde vuelcan las tarjetas SD.
    *   Carpeta `Processed`: Donde el agente mueve las fotos finales (organizadas por fecha/especie).
    *   Base de Datos (SQLite/FAISS): Alojada aquí para velocidad.
2.  **Volumen 2 (Respaldo):**
    *   **Hyper Backup:** Configurar tarea diaria para replicar `Processed` y la DB.
    *   **Raw Archive:** (Opcional) Copia de seguridad de los crudos originales antes de procesar.

## 4. Hoja de Ruta (Roadmap) Sugerida

### Fase 1: El "MVP Funcional" (Semanas 1-2)
*   [x] Setup del Repo Open Source.
*   [ ] Pipeline de Ingesta + MegaDetector.
*   [ ] **Feature Clave:** Inyección de Tags XMP (Especie).
*   [ ] Despliegue en Docker en la máquina con GPU (montando el NAS por SMB/NFS).
*   *Entregable:* El usuario ve que sus fotos ahora tienen etiquetas automáticas de "Animal", "Persona", "Vehículo".

### Fase 2: Inteligencia Profunda (Semanas 3-4)
*   [ ] Integración LLaVA para descripciones ("Jaguar macho con cicatriz").
*   [ ] Inyección de descripciones en XMP.
*   *Entregable:* Búsqueda por texto natural en el gestor de fotos.

### Fase 3: Búsqueda Semántica (Mes 2)
*   [ ] Web UI simple para búsqueda por similitud (CLIP).
*   [ ] Publicación del caso de éxito y apertura del repo a la comunidad.

## 5. Visión del Proyecto

*"Entregamos un sistema que 'vive' dentro del flujo de trabajo actual. No hay que aprender un software nuevo hoy. Simplemente, mañana, cuando abran su gestor de fotos, las imágenes ya estarán organizadas y etiquetadas mágicamente."*
