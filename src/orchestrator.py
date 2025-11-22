import os
import time
import logging
import sys

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/orchestrator.log')
    ]
)

logger = logging.getLogger("WildIndex")

def main():
    logger.info("🚀 Iniciando WildIndex Agent...")
    logger.info("Verificando entorno...")

    # Verificar GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✅ GPU Detectada: {gpu_name}")
            logger.info(f"ℹ️  CUDA Version: {torch.version.cuda}")
        else:
            logger.warning("⚠️  GPU NO detectada. Ejecutando en modo CPU (Lento).")
    except ImportError:
        logger.error("❌ PyTorch no está instalado.")

    # Verificar Directorios
    input_dir = "/app/data/input"
    if os.path.exists(input_dir):
        files = os.listdir(input_dir)
        logger.info(f"📂 Directorio de entrada montado. Archivos visibles: {len(files)}")
    else:
        logger.warning(f"⚠️  Directorio de entrada no encontrado: {input_dir}")

    logger.info("💤 Entrando en bucle de espera (Mock Loop)...")
    
    while True:
        # Aquí irá la lógica del Watchdog / Batch Processor
        time.sleep(60)
        logger.info("💓 Heartbeat: El agente sigue vivo.")

if __name__ == "__main__":
    main()
