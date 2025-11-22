import logging
import time
import os
from typing import Dict, Any
from src.core.detectors.megadetector import MegaDetector

logger = logging.getLogger("WildIndex.AI")

class AIEngine:
    """
    Orquestador de modelos de IA (MegaDetector, LLaVA, CLIP).
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mock_mode = config.get('mock_mode', False)
        self.md_model_path = config.get('md_model_path', 'models/md_v5a.0.0.pt')
        self.detector = None
        
        if not self.mock_mode and os.path.exists(self.md_model_path):
            self.detector = MegaDetector(self.md_model_path)
        else:
            if not self.mock_mode:
                logger.warning(f"⚠️ Modelo MegaDetector no encontrado en {self.md_model_path}. Usando MOCK.")
            self.mock_mode = True

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Ejecuta el pipeline de IA sobre una imagen.
        """
        if self.mock_mode:
            return self._mock_inference(image_path)
        
        # 1. Detección (MegaDetector)
        md_result = self.detector.detect(image_path)
        
        # 2. Captioning (LLaVA) - TODO: Implementar
        # Por ahora devolvemos placeholder si es animal
        llava_caption = None
        if md_result.get('md_category') == 'animal':
            llava_caption = "Descripción pendiente de LLaVA (Fase 2.2)"

        return {
            **md_result,
            "llava_caption": llava_caption,
            "species_prediction": None # Requiere clasificador específico
        }

    def _mock_inference(self, image_path: str) -> Dict[str, Any]:
        """Simula el tiempo de procesamiento y resultados de la IA."""
        import random
        time.sleep(0.1) 
        
        categories = ['animal', 'empty', 'vehicle', 'person']
        category = random.choices(categories, weights=[0.4, 0.4, 0.1, 0.1])[0]
        
        return {
            "md_category": category,
            "md_confidence": round(random.uniform(0.7, 0.99), 2),
            "md_bbox": [0.1, 0.1, 0.5, 0.5] if category == 'animal' else [],
            "llava_caption": f"[MOCK] Un {category} en {image_path}",
            "species_prediction": "Panthera onca [MOCK]" if category == 'animal' else None
        }
