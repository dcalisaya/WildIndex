import logging
import torch
import os
from typing import Dict, Any
from PIL import Image
from src.core.detectors.megadetector import MegaDetector
# LLaVA imports
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration, BitsAndBytesConfig

logger = logging.getLogger("WildIndex.AI")

class AIEngine:
    """
    Orquestador de modelos de IA (MegaDetector, LLaVA, CLIP).
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 1. Cargar MegaDetector (Detección)
        self.md_model_path = config.get("megadetector_model_path", "models/md_v5a.0.0.pt")
        self.md_threshold = config.get("megadetector_threshold", 0.2)
        self.megadetector = MegaDetector(self.md_model_path, self.md_threshold, self.device)
        
        # 2. Cargar LLaVA (Descripción) - Solo si hay GPU
        self.llava_model_id = "llava-hf/llava-v1.6-mistral-7b-hf"
        self.llava_processor = None
        self.llava_model = None
        
        if self.device == "cuda":
            self._load_llava()
        else:
            logger.warning("⚠️ GPU no detectada. LLaVA (descripciones) estará desactivado.")

    def _load_llava(self):
        """Carga LLaVA-NeXT con cuantización de 4 bits para ahorrar VRAM."""
        try:
            logger.info(f"🧠 Cargando LLaVA ({self.llava_model_id}) en 4-bit...")
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )

            self.llava_processor = LlavaNextProcessor.from_pretrained(self.llava_model_id)
            self.llava_model = LlavaNextForConditionalGeneration.from_pretrained(
                self.llava_model_id,
                quantization_config=quantization_config,
                device_map="auto"
            )
            logger.info("✅ LLaVA cargado correctamente.")
        except Exception as e:
            logger.error(f"❌ Error cargando LLaVA: {e}")
            logger.warning("⚠️ Continuando sin capacidades de descripción detallada.")

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """

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
