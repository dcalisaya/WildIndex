import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("WildIndex.DB")

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Crea una conexión a la base de datos con WAL mode habilitado."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Habilitar Write-Ahead Logging para mejor concurrencia y velocidad
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        """Inicializa el esquema de la base de datos si no existe."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        schema = """
        CREATE TABLE IF NOT EXISTS processed_images (
            id TEXT PRIMARY KEY,
            file_hash TEXT UNIQUE,
            original_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            capture_timestamp TEXT,
            
            -- MegaDetector Results
            md_category TEXT, -- 'animal', 'person', 'vehicle', 'empty'
            md_confidence REAL,
            md_bbox TEXT, -- JSON string [x, y, w, h]
            
            -- LLaVA Results
            llava_caption TEXT,
            species_prediction TEXT,
            
            -- BioCLIP Results
            species_common TEXT,
            species_scientific TEXT,
            species_confidence REAL,
            
            -- Processing Status
            status TEXT DEFAULT 'PENDING', -- 'PENDING', 'PROCESSED', 'ERROR', 'SKIPPED'
            error_message TEXT,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_file_hash ON processed_images(file_hash);
        CREATE INDEX IF NOT EXISTS idx_status ON processed_images(status);
        CREATE INDEX IF NOT EXISTS idx_md_category ON processed_images(md_category);
        """
        
        try:
            with self._get_connection() as conn:
                conn.executescript(schema)
            logger.info(f"✅ Base de datos inicializada en: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Error inicializando DB: {e}")
            raise

    def upsert_image(self, image_data: Dict[str, Any]):
        """Inserta o actualiza un registro de imagen."""
        keys = list(image_data.keys())
        values = list(image_data.values())
        placeholders = ",".join(["?"] * len(keys))
        updates = ",".join([f"{k}=excluded.{k}" for k in keys])
        
        sql = f"""
        INSERT INTO processed_images ({",".join(keys)}) 
        VALUES ({placeholders}) 
        ON CONFLICT(id) DO UPDATE SET {updates}, updated_at=CURRENT_TIMESTAMP;
        """
        
        with self._get_connection() as conn:
            conn.execute(sql, values)
            conn.commit()

    def get_image_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Busca una imagen por su hash para evitar reprocesamiento."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM processed_images WHERE file_hash = ?", (file_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_pending_images(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene un lote de imágenes pendientes (si implementamos cola en DB)."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM processed_images WHERE status = 'PENDING' LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
