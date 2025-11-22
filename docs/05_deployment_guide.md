# 🚀 Guía de Despliegue: Ubuntu Server + NVIDIA GPU

**Fecha:** 21 Noviembre 2025
**Hardware Requerido:** Servidor Ubuntu 22.04/24.04 con GPU NVIDIA (RTX 30xx/40xx/50xx).

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

### 2.4. Verificar Logs
```bash
docker compose logs -f
```
Deberías ver: `✅ GPU Detectada: NVIDIA GeForce RTX 5070 Ti`.

## 3. Solución de Problemas Comunes

*   **Error: "could not select device driver"** -> Reinstala `nvidia-container-toolkit` y reinicia docker.
*   **Error: "Permission denied" en /app/data** -> Verifica que el usuario del NAS tenga permisos de lectura/escritura para la IP del servidor, o usa `chmod 777` en la carpeta del NAS (solución rápida, no segura).
