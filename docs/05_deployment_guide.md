# 🚀 Guía de Despliegue: Ubuntu Server + NVIDIA GPU

**Fecha:** 21 Noviembre 2025
**Hardware Requerido:** Servidor Ubuntu 22.04/24.04 con GPU NVIDIA (RTX 30xx/40xx/50xx).

## 1. Preparación del Host (Ubuntu)

### 1.1. Instalar Drivers y Docker
Ejecuta estos comandos en tu servidor:

```bash
# 1. Instalar Drivers NVIDIA (si no los tienes)
sudo apt update
sudo apt install -y nvidia-driver-535 nvidia-utils-535

# 2. Instalar Docker Engine
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

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

### 1.2. Montar el NAS (NFS)
Asumimos que la IP del NAS es `192.168.1.100` y la carpeta compartida es `/volume1/fotos`.

```bash
# 1. Instalar cliente NFS
sudo apt install -y nfs-common

# 2. Crear punto de montaje
sudo mkdir -p /mnt/nas_data

# 3. Montar (Prueba temporal)
sudo mount -t nfs 192.168.1.100:/volume1/fotos /mnt/nas_data

# 4. Hacer persistente (Editar /etc/fstab)
echo "192.168.1.100:/volume1/fotos /mnt/nas_data nfs defaults 0 0" | sudo tee -a /etc/fstab
```

## 2. Instalación del Agente

### 2.1. Copiar Archivos
Puedes clonar el repositorio directamente (Recomendado) o copiar los archivos manualmente.

#### Opción A: Git Clone (Recomendado)
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

### 2.4. Verificar Logs
```bash
docker compose logs -f
```
Deberías ver: `✅ GPU Detectada: NVIDIA GeForce RTX 5070 Ti`.

## 3. Solución de Problemas Comunes

*   **Error: "could not select device driver"** -> Reinstala `nvidia-container-toolkit` y reinicia docker.
*   **Error: "Permission denied" en /app/data** -> Verifica que el usuario del NAS tenga permisos de lectura/escritura para la IP del servidor, o usa `chmod 777` en la carpeta del NAS (solución rápida, no segura).
