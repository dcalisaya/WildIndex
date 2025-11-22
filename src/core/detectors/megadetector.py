import logging
import torch
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("WildIndex.MegaDetector")

class MegaDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.1, device: str = 'cuda'):
        self.model_path = model_path
        self.conf_thres = confidence_threshold
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.model = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo YOLOv5 (MegaDetector)."""
        try:
            logger.info(f"🔌 Cargando MegaDetector desde {self.model_path} en {self.device}...")
            # Usamos torch.hub para cargar custom model. 
            # 'source="local"' asume que yolov5 está instalado o clonado, pero 'ultralytics/yolov5' es más estándar.
            # Para evitar descargas en runtime, lo ideal es usar yolov5 package.
            
            # Opción A: Usando yolov5 pip package (si funciona bien con MD)
            import yolov5
            self.model = yolov5.load(self.model_path, device=self.device)
            
            # Opción B: torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path)
            # self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path, device=self.device)
            
            self.model.conf = self.conf_thres
            logger.info("✅ MegaDetector cargado correctamente.")
            
        except Exception as e:
            logger.error(f"❌ Error cargando MegaDetector: {e}")
            # Fallback o re-raise
            raise e

    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Realiza detección sobre una imagen.
        Retorna el 'mejor' resultado (la categoría con mayor confianza).
        """
        if not self.model:
            return {"error": "Model not loaded"}

        try:
            # Inferencia
            results = self.model(image_path)
            
            # Procesar resultados (Pandas dataframe es lo más fácil con yolov5)
            df = results.pandas().xyxy[0]
            
            if df.empty:
                return {
                    "md_category": "empty",
                    "md_confidence": 0.0,
                    "md_bbox": []
                }
            
            # Obtener la detección con mayor confianza
            best_detection = df.iloc[0]
            
            # Mapeo de clases MDv5a: 0=empty (no suele salir), 1=animal, 2=person, 3=vehicle
            # Nota: MDv5 classes son {1: 'animal', 2: 'person', 3: 'vehicle'}
            # Pero el modelo raw puede devolver índices 0-based dependiendo de cómo se cargue.
            # Asumiremos nombres si el modelo los tiene, sino mapeamos.
            
            category_name = best_detection['name'] # 'animal', 'person', etc.
            confidence = float(best_detection['confidence'])
            bbox = [
                float(best_detection['xmin']),
                float(best_detection['ymin']),
                float(best_detection['xmax']),
                float(best_detection['ymax'])
            ]
            
            return {
                "md_category": category_name,
                "md_confidence": confidence,
                "md_bbox": bbox
            }

        except Exception as e:
            logger.error(f"❌ Error en inferencia MD para {image_path}: {e}")
            return {"error": str(e)}
