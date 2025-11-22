# 🚀 Guía de Despliegue: Ubuntu Server + NVIDIA GPU

**Fecha:** 21 Noviembre 2025
**Hardware Requerido:**

### 🖥️ Requisitos de Hardware (Servidor)
Para un rendimiento óptimo y evitar cuellos de botella durante la construcción (build) y la inferencia:

*   **CPU:** 4+ Cores (Intel Core i5/i7 o AMD Ryzen 5/7 recientes).
*   **RAM:** 16 GB mínimo (32 GB recomendado si planeas usar LLaVA).
*   **Disco:** SSD con al menos **50 GB libres**.
    *   *Nota:* Las imágenes de Docker (PyTorch + CUDA) y los modelos ocupan bastante espacio. Evita usar HDDs mecánicos para el sistema operativo/Docker.
*   **GPU:** NVIDIA RTX 3060 (12GB) o superior.
    *   *Recomendado:* RTX 4070/5070 Ti (16GB VRAM) para correr múltiples modelos.

## 1. Preparación del Host (Ubuntu)

### 1.1. Instalar Drivers y Docker
Ejecuta estos comandos en tu servidor:

```bash
# 1. Verificar si ya tienes drivers (Opcional)
# Ejecuta esto primero:
nvidia-smi
# ✅ Si ves una tabla con tu GPU, SALTA al paso 2 (Instalar Docker).
# ❌ Si dice "command not found", continúa con la instalación:

# 1.1 Instalar Drivers NVIDIA
sudo apt update
sudo apt install -y nvidia-driver-535 nvidia-utils-535

# 2. Instalar Docker Engine
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# ⚠️ IMPORTANTE: Para que esto surta efecto sin reiniciar, ejecuta:
newgrp docker

# 3. Instalar NVIDIA Container Toolkit (CRÍTICO para Docker + GPU)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 1.2. Montar el Almacenamiento (NAS)
Dependiendo de tu NAS (Synology, TrueNAS, QNAP) y protocolo, la configuración varía.

#### Opción A: NFS (Recomendado para Rendimiento) 🚀
**Nota Importante:** NFS valida por **IP**, no por usuario/contraseña. Si el comando se queda "pensando" (hangs), suele ser porque el NAS está bloqueando la IP del servidor.

1.  **Configuración en el NAS:**
    *   **Synology:** Panel de Control > Carpetas Compartidas > Editar > Permisos NFS > Crear > IP del Servidor Ubuntu.
    *   **TrueNAS Scale:** Shares > NFS > Add.
        *   *Networks:* Añade la IP de tu servidor Ubuntu /32 (ej. `192.168.1.50/32`).
        *   *Mapall User/Group:* Configura esto al dueño de los archivos (ej. `apps` o `admin`) para evitar problemas de "Permission Denied".

2.  **Montaje en Ubuntu:**
    ```bash
    sudo apt install -y nfs-common
    sudo mkdir -p /mnt/nas_data
    
    # Reemplaza la IP y la ruta (en TrueNAS suele ser /mnt/pool/dataset)
    sudo mount -t nfs 192.168.1.100:/mnt/pool/fotos /mnt/nas_data
    ```

#### Opción B: SMB/CIFS (Usando Usuario y Contraseña) 🔑
Si prefieres usar autenticación clásica o NFS te da problemas.

1.  **Montaje en Ubuntu:**
    ```bash
    sudo apt install -y cifs-utils
    sudo mkdir -p /mnt/nas_data
    
    # Reemplaza usuario, contraseña, IP y ruta
    # uid/gid aseguran que puedas escribir en los archivos montados
    sudo mount -t cifs -o username=TU_USUARIO,password=TU_CONTRASEÑA,uid=$(id -u),gid=$(id -g) //192.168.1.100/fotos /mnt/nas_data
    ```

#### Hacer persistente (Editar /etc/fstab)
Para que se monte solo al reiniciar:
```bash
# Ejemplo NFS
192.168.1.100:/mnt/pool/fotos /mnt/nas_data nfs defaults 0 0

# Ejemplo SMB (Más seguro usar archivo de credenciales, pero esto sirve de ejemplo)
//192.168.1.100/fotos /mnt/nas_data cifs username=user,password=pass,uid=1000,gid=1000 0 0
```

### 1.3. Verificar Permisos (CRÍTICO) ⚠️
Antes de seguir, **es obligatorio** verificar que puedes leer y escribir en el NAS desde Ubuntu.

```bash
# 1. Prueba de Lectura (Listar archivos)
ls -l /mnt/nas_data
# ✅ Deberías ver tus carpetas de fotos.

# 2. Prueba de Escritura (Crear un archivo vacío)
touch /mnt/nas_data/test_write.txt

# ✅ Si NO da error, bórralo y continúa:
rm /mnt/nas_data/test_write.txt

# ❌ Si dice "Permission denied":
# - Revisa el "Mapall User" en TrueNAS (NFS).
# - Revisa que el usuario SMB tenga permisos de escritura.
# - Revisa el uid/gid en el comando mount.
```

## 2. Instalación del Agente

### 2.1. Copiar Archivos
Puedes clonar el repositorio directamente (Recomendado) o copiar los archivos manualmente.

#### Opción A: Git Clone (HTTPS) - ✅ Más Fácil
No requiere configurar claves SSH. Ideal para despliegues rápidos.
```bash
git clone https://github.com/dcalisaya/WildIndex.git ~/wildindex
```

#### Opción B: Git Clone (SSH)
Solo si ya tienes tus claves SSH configuradas en GitHub.
```bash
git clone git@github.com:dcalisaya/WildIndex.git ~/wildindex
```

#### Opción B: Copia Manual (SCP)
```bash
# Desde tu Mac
scp -r ~/Developer/procesadorfotos usuario@192.168.1.x:~/wildindex
```

### 2.2. Configurar Entorno
En el servidor:

```bash
cd ~/wildindex
cp .env.example .env
# Edita .env si es necesario (aunque los defaults deberían funcionar)
```

### 2.3. Arrancar el Agente
```bash
docker compose up -d --build
```
**⏳ Tiempo estimado:** 5-15 minutos (dependiendo de tu internet).
*   Descarga la imagen base de PyTorch (~3.5 GB).
*   Instala dependencias de Python.
*   *Nota:* Si parece que se detuvo en "Pulling fs layer", ten paciencia.

### 2.4. Descargar Modelos de IA (Primer Uso) 🧠
Una vez que el contenedor esté corriendo, necesitas descargar los "cerebros" (pesos del modelo MegaDetector). Esto solo se hace una vez.

```bash
docker compose exec wildindex python scripts/setup_models.py
```
**⏳ Tiempo estimado:** 2-5 minutos.
*   Esto descargará `md_v5a.0.0.pt` (~250MB) en la carpeta `models/`.
*   Si no lo haces, el agente funcionará en modo "Mock" (simulación).

### 2.5. Verificar Logs
```bash
docker compose logs -f
```
Deberías ver: `✅ GPU Detectada: NVIDIA GeForce RTX 5070 Ti`.

## 3. Solución de Problemas Comunes (FAQ) 🛠️

### 3.1. Conflictos de Dependencias (PyTorch / YOLOv5)
**Síntoma:** Errores como `ModuleNotFoundError: No module named 'huggingface_hub'`, `torchvision is incompatible with torch`, o `AttributeError: 'Upsample' object has no attribute 'recompute_scale_factor'`.
**Causa:** Mezcla de versiones de PyTorch instaladas por `pip` sobre una imagen base antigua.
**Solución:**
1.  Asegúrate de usar la imagen base de **Ultralytics** en el `Dockerfile`: `FROM ultralytics/ultralytics:latest`.
2.  Ejecuta un rebuild limpio:
    ```bash
    docker compose down --rmi all
    docker compose build --no-cache
    docker compose up -d
    ```

### 3.2. Error de Base de Datos: `sqlite3.InterfaceError`
**Síntoma:** `Error binding parameter 8 - probably unsupported type`.
**Causa:** Intentar guardar una lista (ej. `[0.1, 0.2, 0.5, 0.8]`) directamente en una columna `TEXT` de SQLite.
**Solución:** El código ya incluye la corrección (`json.dumps()`), pero si persiste, asegúrate de tener la última versión del código (`git pull origin master`).

### 3.3. El Modelo MegaDetector no carga (Loop de reinicios)
**Síntoma:** El contenedor se reinicia constantemente o log muestra `FileNotFoundError: models/md_v5a.0.0.pt`.
**Causa:** No se ha descargado el modelo o el volumen `./models` no está montado correctamente.
**Solución:**
1.  Verifica que la carpeta `models/` exista en el host.
2.  Ejecuta el script de descarga manual:
    ```bash
    docker compose exec wildindex python scripts/setup_models.py
    ```

### 3.4. Conflicto con ComfyUI / Otros procesos de IA
**Síntoma:** `CUDA out of memory` al correr WildIndex mientras generas imágenes/video en ComfyUI.
**Solución:**
*   **Automática:** WildIndex tiene un sistema de **Fallback a CPU**. Si la GPU está llena, usará el procesador (más lento, pero no falla).
*   **Manual:** Detén el contenedor (`docker compose stop`) cuando necesites toda la VRAM para renderizar video.

### 3.5. Actualización de Código no se refleja
**Síntoma:** Haces `git pull` pero el contenedor sigue con el código viejo.
**Solución:** Docker cachea agresivamente. Fuerza la reconstrucción:
```bash
docker compose build --no-cache
docker compose up -d
```
