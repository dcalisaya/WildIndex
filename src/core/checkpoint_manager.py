import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple
from src.database.db_manager import DatabaseManager

logger = logging.getLogger("WildIndex.Checkpoint")

class CheckpointManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def calculate_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calcula el hash SHA-256 de un archivo de manera eficiente."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"❌ Error calculando hash para {file_path}: {e}")
            raise

    def should_process(self, file_path: str) -> Tuple[bool, str]:
        """
        Determina si un archivo debe ser procesado.
        Retorna: (should_process: bool, file_hash: str)
        """
        try:
            # 1. Calcular Hash
            file_hash = self.calculate_hash(file_path)
            
            # 2. Consultar DB
            existing_record = self.db.get_image_by_hash(file_hash)
            
            if existing_record:
                status = existing_record.get('status')
                if status == 'PROCESSED':
                    logger.debug(f"⏭️  Saltando {Path(file_path).name} (Ya procesado)")
                    return False, file_hash
                elif status == 'ERROR':
                    logger.info(f"🔄 Reintentando {Path(file_path).name} (Estado previo: ERROR)")
                    return True, file_hash
                else:
                    # PENDING o desconocido
                    return True, file_hash
            
            # No existe registro
            return True, file_hash
            
        except Exception as e:
            logger.error(f"⚠️ Error verificando checkpoint para {file_path}: {e}")
            # Ante la duda, procesar (o fallar seguro, depende de la estrategia. Aquí fallamos seguro)
            return False, ""

