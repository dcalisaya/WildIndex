import os
import sqlite3
import subprocess
import logging
import json
from pathlib import Path
from typing import Dict, Any, List

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WildIndex.QA")

class QAValidator:
    def __init__(self, db_path: str, processed_dir: str):
        self.db_path = db_path
        self.processed_dir = Path(processed_dir)
        self.stats = {
            "total_records": 0,
            "files_found": 0,
            "files_missing": 0,
            "metadata_ok": 0,
            "metadata_missing": 0,
            "db_errors": 0
        }

    def _get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def _read_metadata(self, file_path: str) -> Dict[str, Any]:
        """Lee metadatos XMP/IPTC usando exiftool."""
        try:
            cmd = [
                "exiftool",
                "-j",
                "-Subject", # Keywords (XMP-dc:Subject)
                "-Description", # Caption (XMP-dc:Description)
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return data[0] if data else {}
        except Exception as e:
            logger.error(f"❌ Error leyendo metadatos de {file_path}: {e}")
            return {}

    def validate(self):
        """Ejecuta la validación completa."""
        logger.info(f"🧪 Iniciando Validación de Calidad (QA)...")
        logger.info(f"📂 DB: {self.db_path}")
        logger.info(f"📂 Processed Dir: {self.processed_dir}")

        if not os.path.exists(self.db_path):
            logger.error("❌ Base de datos no encontrada.")
            return

        try:
            conn = self._get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM processed_images WHERE status = 'PROCESSED'")
            rows = cursor.fetchall()
            
            self.stats["total_records"] = len(rows)
            logger.info(f"📊 Registros procesados en DB: {len(rows)}")

            for row in rows:
                self._validate_record(dict(row))

        except Exception as e:
            logger.error(f"❌ Error fatal en QA: {e}")
            self.stats["db_errors"] += 1
        finally:
            if 'conn' in locals():
                conn.close()
            self._print_report()

    def _validate_record(self, record: Dict[str, Any]):
        """Valida un registro individual."""
        file_name = record['file_name']
        category = record['md_category']
        
        # 1. Verificar existencia del archivo
        expected_path = self.processed_dir / category / file_name
        
        if not expected_path.exists():
            logger.error(f"❌ Archivo faltante: {expected_path}")
            self.stats["files_missing"] += 1
            return

        self.stats["files_found"] += 1
        
        # 2. Verificar Metadatos (Solo JPEGs por ahora)
        if expected_path.suffix.lower() in ['.jpg', '.jpeg']:
            metadata = self._read_metadata(str(expected_path))
            
            # Verificar Keywords (debe contener la categoría)
            keywords = metadata.get('Subject', [])
            if isinstance(keywords, str): keywords = [keywords] # Exiftool a veces devuelve string si es uno solo
            
            if category in keywords:
                # logger.info(f"✅ Metadatos OK: {file_name}")
                self.stats["metadata_ok"] += 1
            else:
                logger.warning(f"⚠️ Metadatos incompletos en {file_name}. Esperado: {category}, Encontrado: {keywords}")
                self.stats["metadata_missing"] += 1

    def _print_report(self):
        """Imprime el reporte final."""
        print("\n" + "="*40)
        print("📑 REPORTE DE CALIDAD (QA)")
        print("="*40)
        print(f"Total Registros DB:   {self.stats['total_records']}")
        print(f"✅ Archivos Encontrados: {self.stats['files_found']}")
        print(f"❌ Archivos Perdidos:    {self.stats['files_missing']}")
        print("-" * 20)
        print(f"✅ Metadatos Correctos:  {self.stats['metadata_ok']}")
        print(f"⚠️ Metadatos Faltantes:  {self.stats['metadata_missing']}")
        print("="*40 + "\n")

if __name__ == "__main__":
    # Rutas por defecto dentro del contenedor
    DB_PATH = "/app/data/db/wildindex.db"
    PROCESSED_DIR = "/app/data/processed"
    
    validator = QAValidator(DB_PATH, PROCESSED_DIR)
    validator.validate()
