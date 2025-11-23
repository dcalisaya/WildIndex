import os
import shutil
import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from src.database.db_manager import DatabaseManager
from src.core.checkpoint_manager import CheckpointManager
from src.core.ai_engine import AIEngine
from src.core.metadata_injector import MetadataInjector

logger = logging.getLogger("WildIndex.BatchProcessor")

class BatchProcessor:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        db_manager: DatabaseManager,
        checkpoint_manager: CheckpointManager,
        ai_engine: AIEngine,
        metadata_injector: MetadataInjector
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.db = db_manager
        self.checkpoint = checkpoint_manager
        self.ai = ai_engine
        self.metadata = metadata_injector
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.arw', '.cr2', '.mp4', '.avi'}

    def scan_files(self) -> List[Path]:
        """Escanea recursivamente el directorio de entrada buscando archivos soportados."""
        files = []
        logger.info(f"🔍 Escaneando {self.input_dir}...")
        for root, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                if Path(filename).suffix.lower() in self.supported_extensions:
                    files.append(Path(root) / filename)
        logger.info(f"📄 Encontrados {len(files)} archivos candidatos.")
        return files

    def process_batch(self, batch_size: int = 10):
        """Procesa un lote de archivos."""
        all_files = self.scan_files()
        
        # Filtrar los que ya están procesados
        pending_files = []
        for f in all_files:
            should_process, file_hash = self.checkpoint.should_process(str(f))
            if should_process:
                pending_files.append((f, file_hash))
                if len(pending_files) >= batch_size:
                    break
        
        if not pending_files:
            logger.info("✅ No hay archivos pendientes de procesamiento.")
            return

        logger.info(f"🚀 Procesando lote de {len(pending_files)} imágenes...")
        
        for file_path, file_hash in pending_files:
            self._process_single_file(file_path, file_hash)

    def _process_single_file(self, file_path: Path, file_hash: str):
        """Procesa un archivo individual: IA -> Copia -> Metadatos -> DB."""
        try:
            logger.info(f"📸 Procesando: {file_path.name}")
            
            # 1. Ejecutar IA
            ai_result = self.ai.analyze_image(str(file_path))
            
            # 2. Preparar destino (Organizado por Fecha/Categoría)
            # 2. Preparar destino (Organizado por Fecha/Categoría)
            category = ai_result.get('md_category', 'unknown')
            dest_folder = self.output_dir / category
            
            # Lógica defensiva para creación de directorios (NAS friendly)
            if dest_folder.exists():
                if dest_folder.is_file():
                    logger.warning(f"⚠️ {dest_folder} existe y es un archivo. Renombrando...")
                    backup_name = f"{dest_folder}_backup_{datetime.now().timestamp()}"
                    dest_folder.rename(backup_name)
                    dest_folder.mkdir(parents=True, exist_ok=True)
            else:
                try:
                    dest_folder.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    # Concurrencia o filesystem raro
                    if dest_folder.is_file():
                        raise # Es un archivo, error real
                    # Si es directorio, ignoramos el error
                    pass

            dest_path = dest_folder / file_path.name
            
            # 3. Copiar archivo
            if not dest_path.exists():
                shutil.copy2(file_path, dest_path)
            
            # 4. Inyectar Metadatos (Sobre la copia)
            # Detectar si es RAW para usar sidecar
            is_raw = dest_path.suffix.lower() in ['.arw', '.cr2', '.dng', '.nef', '.orf', '.rw2']
            
            if is_raw:
                # RAW -> Generar .xmp sidecar
                self.metadata.write_metadata(str(dest_path), ai_result, sidecar=True)
            elif dest_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff']:
                # Imagen normal -> Inyectar dentro del archivo
                self.metadata.write_metadata(str(dest_path), ai_result, sidecar=False)
            
            # 5. Guardar en DB
            record = {
                "id": file_hash,
                "file_hash": file_hash,
                "original_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "capture_timestamp": datetime.now().isoformat(),
                "md_category": category,
                "md_confidence": ai_result.get('md_confidence'),
                "md_bbox": json.dumps(ai_result.get('md_bbox')) if ai_result.get('md_bbox') else None,
                "llava_caption": ai_result.get('llava_caption'),
                "species_prediction": ai_result.get('species_prediction'),
                "status": "PROCESSED"
            }
            
            self.db.upsert_image(record)
            logger.info(f"✅ Completado: {file_path.name} -> {category}")

        except Exception as e:
            logger.error(f"❌ Error procesando {file_path.name}: {e}")
            error_record = {
                "id": file_hash,
                "file_hash": file_hash,
                "original_path": str(file_path),
                "file_name": file_path.name,
                "status": "ERROR",
                "error_message": str(e)
            }
            self.db.upsert_image(error_record)
