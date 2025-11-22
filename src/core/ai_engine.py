import logging
import time
import random
from typing import Dict, Any, List

logger = logging.getLogger("WildIndex.AI")

class AIEngine:
    """
    Clase base/interfaz para los modelos de IA.
    En Fase 2, esto orquestará MegaDetector, LLaVA y CLIP.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mock_mode = True # Por ahora, simulamos

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Ejecuta el pipeline de IA sobre una imagen.
        Retorna un diccionario con los resultados.
        """
        if self.mock_mode:
            return self._mock_inference(image_path)
        
        # TODO: Implementar inferencia real
        raise NotImplementedError("Inferencia real no implementada aún")

    def _mock_inference(self, image_path: str) -> Dict[str, Any]:
        """Simula el tiempo de procesamiento y resultados de la IA."""
        # Simular carga de GPU
        time.sleep(0.5) 
        
        # Simular resultados aleatorios pero realistas
        categories = ['animal', 'empty', 'vehicle', 'person']
        category = random.choices(categories, weights=[0.4, 0.4, 0.1, 0.1])[0]
        
        result = {
            "md_category": category,
            "md_confidence": round(random.uniform(0.7, 0.99), 2),
            "md_bbox": "[0.1, 0.1, 0.5, 0.5]" if category == 'animal' else "[]",
            "llava_caption": f"Una foto simulada de un {category} en {image_path}",
            "species_prediction": "Panthera onca" if category == 'animal' else None
        }
        
        logger.debug(f"🧠 Inferencia Mock para {image_path}: {result['md_category']}")
        return result
