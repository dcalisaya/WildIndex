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
        Pipeline principal:
        1. MegaDetector -> Detectar si hay algo.
        2. Si hay animal/persona -> LLaVA -> Describir qué hace.
        """
        # 1. Detección
        md_result = self.megadetector.detect(image_path)
        
        # Fix: MegaDetector devuelve 'md_category', no 'category'
        if 'error' in md_result:
            logger.error(f"Error en detección: {md_result['error']}")
            return {
                "md_category": "error",
                "md_confidence": 0.0,
                "md_bbox": [],
                "llava_caption": None,
                "species_prediction": None
            }

        category = md_result['md_category']
        
        result = {
            "md_category": category,
            "md_confidence": md_result['confidence'],
            "md_bbox": md_result['bbox'],
            "llava_caption": None,
            "species_prediction": None # TODO: Fase 3 (Clasificador específico)
        }

        # 2. Descripción (Solo si vale la pena)
        if category in ['animal', 'person'] and self.llava_model:
            result['llava_caption'] = self._generate_caption(image_path, category)

        return result

    def _generate_caption(self, image_path: str, category: str) -> str:
        """Genera una descripción usando LLaVA."""
        try:
            image = Image.open(image_path)
            
            # Prompt dinámico
            prompt_text = "Describe the animal in the image in detail." if category == 'animal' else "Describe the person in the image in detail."
            prompt = f"[INST] <image>\n{prompt_text} [/INST]"
            
            inputs = self.llava_processor(prompt, image, return_tensors="pt").to(self.device)
            
            # Generar
            output = self.llava_model.generate(
                **inputs, 
                max_new_tokens=100,
                do_sample=True,
                temperature=0.2
            )
            
            # Decodificar
            full_response = self.llava_processor.decode(output[0], skip_special_tokens=True)
            # Limpiar el prompt de la respuesta (LLaVA a veces repite el prompt)
            caption = full_response.split("[/INST]")[-1].strip()
            
            return caption
            
        except Exception as e:
            logger.error(f"❌ Error generando caption LLaVA: {e}")
            return None
