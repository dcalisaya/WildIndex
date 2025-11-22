import os
import time
import logging
import sys
from pathlib import Path

from src.database.db_manager import DatabaseManager
from src.core.checkpoint_manager import CheckpointManager
from src.core.ai_engine import AIEngine
from src.core.batch_processor import BatchProcessor
from src.core.metadata_injector import MetadataInjector

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
    
    # 1. Configuración
    input_dir = os.getenv("NAS_INPUT_PATH", "/app/data/input")
    output_dir = os.getenv("NAS_PROCESSED_PATH", "/app/data/processed")
    db_path = os.getenv("DB_PATH", "/app/data/db/wildindex.db")
    
    logger.info(f"📂 Input: {input_dir}")
    logger.info(f"📂 Output: {output_dir}")
    logger.info(f"💾 DB: {db_path}")

    # 2. Inicializar Componentes
    try:
        db_manager = DatabaseManager(db_path)
        checkpoint_manager = CheckpointManager(db_manager)
        ai_engine = AIEngine(config={"use_gpu": True}) # Configuración placeholder
        metadata_injector = MetadataInjector()
        
        processor = BatchProcessor(
            input_dir=input_dir,
            output_dir=output_dir,
            db_manager=db_manager,
            checkpoint_manager=checkpoint_manager,
            ai_engine=ai_engine,
            metadata_injector=metadata_injector
        )
        logger.info("✅ Componentes inicializados correctamente.")
        
    except Exception as e:
        logger.critical(f"❌ Error fatal inicializando componentes: {e}")
        sys.exit(1)

    # 3. Bucle Principal (Watchdog)
    logger.info("🏁 Iniciando bucle de procesamiento...")
    
    while True:
        try:
            # Procesar un lote
            processor.process_batch(batch_size=10)
            
            # Esperar antes del siguiente ciclo para no saturar
            # En producción, esto podría ser más sofisticado (eventos)
            time.sleep(5) 
            
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo agente por solicitud de usuario...")
            break
        except Exception as e:
            logger.error(f"❌ Error en bucle principal: {e}")
            time.sleep(10) # Esperar antes de reintentar tras error

if __name__ == "__main__":
    main()
