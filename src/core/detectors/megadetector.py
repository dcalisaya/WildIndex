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
            import yolov5
            import torch
            
            # PATCH: PyTorch 2.4+ fuerza weights_only=True por defecto, lo que rompe modelos viejos de YOLOv5.
            # Forzamos weights_only=False temporalmente porque confiamos en el modelo MD.
            _original_load = torch.load
            def _safe_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return _original_load(*args, **kwargs)
            
            torch.load = _safe_load
            try:
                self.model = yolov5.load(self.model_path, device=self.device)
            finally:
                torch.load = _original_load # Restaurar original
                
            self.model.conf = self.conf_thres
            logger.info(f"✅ MegaDetector cargado correctamente en {self.device}.")
            
        except Exception as e:
            # Si falla CUDA, intentar con CPU
            if self.device == 'cuda':
                logger.warning(f"⚠️ Error cargando en CUDA: {e}")
                logger.warning("🔄 Reintentando con CPU...")
                try:
                    self.device = 'cpu'
                    # Repetir el patch para el intento en CPU
                    import torch
                    _original_load = torch.load
                    def _safe_load(*args, **kwargs):
                        if 'weights_only' not in kwargs:
                            kwargs['weights_only'] = False
                        return _original_load(*args, **kwargs)
                    
                    torch.load = _safe_load
                    try:
                        import yolov5
                        self.model = yolov5.load(self.model_path, device='cpu')
                    finally:
                        torch.load = _original_load

                    self.model.conf = self.conf_thres
                    logger.info("✅ MegaDetector cargado en CPU (fallback).")
                except Exception as cpu_error:
                    logger.error(f"❌ Error cargando MegaDetector incluso en CPU: {cpu_error}")
                    raise cpu_error
            else:
                logger.error(f"❌ Error cargando MegaDetector: {e}")
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
