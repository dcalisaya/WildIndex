import os
import requests
import logging
from pathlib import Path
import hashlib

# Configuración
MODEL_URL = "https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt"
MODEL_MD5 = "3a690b5d6db6414abb6903f63ce5ac58" # Placeholder MD5, en prod verificar real
DEST_DIR = Path("models")
DEST_PATH = DEST_DIR / "md_v5a.0.0.pt"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SetupModels")

def download_file(url: str, dest: Path):
    if dest.exists():
        logger.info(f"✅ El modelo ya existe en {dest}")
        return

    logger.info(f"⬇️  Descargando modelo desde {url}...")
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                f.write(chunk)
                
        logger.info("✅ Descarga completada.")
    except Exception as e:
        logger.error(f"❌ Error descargando modelo: {e}")
        if dest.exists():
            dest.unlink()
        raise

if __name__ == "__main__":
    print("🦁 Configurando modelos para WildIndex...")
    download_file(MODEL_URL, DEST_PATH)
    print("✨ Listo.")
