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
        # Force CPU for MegaDetector to avoid CUDA conflicts/zombie states with LLaVA
        self.megadetector = MegaDetector(self.md_model_path, self.md_threshold, device="cpu")
        
        # 2. Cargar LLaVA (Descripción) - Solo si hay GPU
        self.llava_model_id = "llava-hf/llava-v1.6-mistral-7b-hf"
        self.llava_processor = None
        self.llava_model = None
        
        if self.device == "cuda":
            self._load_llava()
        else:
            logger.warning("⚠️ GPU no detectada. LLaVA (descripciones) estará desactivado.")

        # 3. Cargar BioCLIP (Especies)
        self.bioclip_model = None
        self._load_bioclip()

    def _load_llava(self):
        """Carga LLaVA-NeXT en 4-bit (ahorro de VRAM)."""
        try:
            logger.info(f"🧠 Cargando LLaVA ({self.llava_model_id}) en 4-bit...")
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            self.llava_processor = LlavaNextProcessor.from_pretrained(self.llava_model_id)
            self.llava_model = LlavaNextForConditionalGeneration.from_pretrained(
                self.llava_model_id,
                quantization_config=quantization_config,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                device_map="cuda:0" 
            )
            logger.info("✅ LLaVA cargado correctamente (4-bit).")
        except Exception as e:
            logger.error(f"❌ Error cargando LLaVA: {e}")
            logger.warning("⚠️ Continuando sin capacidades de descripción detallada.")

    # ... (analyze_image and _generate_caption methods remain unchanged) ...

    def _analyze_species(self, image_path: str, bbox: list) -> Dict[str, Any]:
        """Clasifica la especie usando BioCLIP en el recorte del animal."""
        if not self.bioclip_model:
            return None
            
        try:
            # 1. Abrir y Recortar
            img = Image.open(image_path).convert("RGB")
            width, height = img.size
            
            # Bbox es [x_min, y_min, width_box, height_box] normalizado (0-1)
            x, y, w, h = bbox
            
            # Validar bbox
            if w <= 0 or h <= 0:
                return None

            left = x * width
            top = y * height
            right = (x + w) * width
            bottom = (y + h) * height
            
            # Margen de seguridad (padding)
            padding = 0.05 * max(right-left, bottom-top)
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(width, right + padding)
            bottom = min(height, bottom + padding)
            
            # Validar coordenadas finales
            if left >= right or top >= bottom:
                logger.warning(f"⚠️ Bbox inválido para BioCLIP: {bbox}")
                return None
            
            crop = img.crop((left, top, right, bottom))
            
            # 2. Preprocesar
            # BioCLIP en CPU
            image_input = self.bioclip_preprocess(crop).unsqueeze(0).to(self.bioclip_device)
            
            # 3. Inferencia
            # No usar autocast si es CPU (o usar torch.cpu.amp.autocast si fuera necesario, pero float32 es mejor en CPU)
            if self.bioclip_device == "cuda":
                 with torch.no_grad(), torch.cuda.amp.autocast():
                    image_features = self.bioclip_model.encode_image(image_input)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    text_probs = (100.0 * image_features @ self.species_embeddings.T).softmax(dim=-1)
            else:
                 with torch.no_grad():
                    image_features = self.bioclip_model.encode_image(image_input)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    text_probs = (100.0 * image_features @ self.species_embeddings.T).softmax(dim=-1)
            
            # ... (resto del código igual) ...

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
            "md_confidence": md_result['md_confidence'],
            "md_bbox": md_result['md_bbox'],
            "llava_caption": None,
            "species_prediction": None # TODO: Fase 3 (Clasificador específico)
        }

        # 2. Descripción (Solo si vale la pena)
        if category in ['animal', 'person'] and self.llava_model:
            result['llava_caption'] = self._generate_caption(image_path, category)
            
        # 3. Clasificación de Especie (BioCLIP)
        if category == 'animal' and self.bioclip_model:
            # Usar el bbox más confiable (MegaDetector devuelve lista, tomamos el primero/mejor?)
            # md_result['md_bbox'] es una lista de bboxes?
            # MegaDetector.detect devuelve el bbox de mayor confianza en 'md_bbox' (single list [x,y,w,h])
            # Verificamos si bbox es válido
            if result['md_bbox'] and len(result['md_bbox']) == 4:
                species_result = self._analyze_species(image_path, result['md_bbox'])
                if species_result:
                    result.update(species_result)
                    # Actualizar species_prediction para compatibilidad
                    result['species_prediction'] = f"{species_result['species_common']} ({species_result['species_scientific']})"

        return result

    def _generate_caption(self, image_path: str, category: str) -> str:
        """Genera una descripción usando LLaVA."""
        try:
            image = Image.open(image_path)
            
            # Asegurar formato RGB
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Prompt manual simplificado para evitar problemas con templates
            # Llava-Next espera [INST] <image>\nTEXT [/INST]
            prompt_text = "Describe the animal in the image in detail." if category == 'animal' else "Describe the person in the image in detail."
            prompt = f"[INST] <image>\n{prompt_text} [/INST]"
            
            # Pasar argumentos explícitamente
            # Asegurar que los inputs estén en el mismo dispositivo que el modelo
            target_device = self.llava_model.device
            inputs = self.llava_processor(text=prompt, images=image, return_tensors="pt").to(target_device)
            
            # Generar (Configuración conservadora para evitar hangs)
            output = self.llava_model.generate(
                **inputs, 
                max_new_tokens=64,
                do_sample=False, # Greedy decoding es más rápido y estable
                pad_token_id=self.llava_processor.tokenizer.eos_token_id
            )
            
            # Decodificar
            full_response = self.llava_processor.decode(output[0], skip_special_tokens=True)
            
            # Limpiar prompt
            if "[/INST]" in full_response:
                caption = full_response.split("[/INST]")[-1].strip()
            else:
                caption = full_response.strip()
            
            return caption
            
        except Exception as e:
            logger.error(f"❌ Error generando caption LLaVA: {e}")
            return None

    def _load_bioclip(self):
        """Carga BioCLIP para identificación de especies."""
        try:
            import open_clip
            logger.info("🧬 Cargando BioCLIP (imageomics/bioclip)...")
            model_name = 'hf-hub:imageomics/bioclip'
            self.bioclip_model, _, self.bioclip_preprocess = open_clip.create_model_and_transforms(model_name)
            self.bioclip_tokenizer = open_clip.get_tokenizer(model_name)
            
            # Mover a CPU para ahorrar VRAM (LLaVA 16-bit ocupa casi todo)
            self.bioclip_device = "cpu"
            self.bioclip_model.to(self.bioclip_device)
            
            # Pre-computar embeddings de texto para la lista de especies
            from src.core.species_list import SPECIES_LIST
            self.species_labels = SPECIES_LIST
            text_tokens = self.bioclip_tokenizer(self.species_labels).to(self.bioclip_device)
            
            with torch.no_grad(), torch.cuda.amp.autocast():
                self.species_embeddings = self.bioclip_model.encode_text(text_tokens)
                self.species_embeddings /= self.species_embeddings.norm(dim=-1, keepdim=True)
                
            logger.info(f"✅ BioCLIP cargado con {len(self.species_labels)} especies.")
            
        except Exception as e:
            logger.error(f"❌ Error cargando BioCLIP: {e}")
            self.bioclip_model = None

    def _analyze_species(self, image_path: str, bbox: list) -> Dict[str, Any]:
        """Clasifica la especie usando BioCLIP en el recorte del animal."""
        if not self.bioclip_model:
            return None
            
        try:
            # 1. Abrir y Recortar
            img = Image.open(image_path).convert("RGB")
            width, height = img.size
            
            # Bbox es [x_min, y_min, width_box, height_box] normalizado (0-1)
            # MegaDetector devuelve [x, y, w, h] (normalized)
            x, y, w, h = bbox
            left = x * width
            top = y * height
            right = (x + w) * width
            bottom = (y + h) * height
            
            # Margen de seguridad (padding)
            padding = 0.05 * max(right-left, bottom-top)
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(width, right + padding)
            bottom = min(height, bottom + padding)
            
            crop = img.crop((left, top, right, bottom))
            
            # 2. Preprocesar
            image_input = self.bioclip_preprocess(crop).unsqueeze(0).to(self.bioclip_device)
            
            # 3. Inferencia
            with torch.no_grad(), torch.cuda.amp.autocast():
                image_features = self.bioclip_model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                
                text_probs = (100.0 * image_features @ self.species_embeddings.T).softmax(dim=-1)
            
            # 4. Top 1
            top_prob, top_idx = text_probs[0].topk(1)
            confidence = top_prob.item()
            label = self.species_labels[top_idx.item()]
            
            # Separar Científico y Común "Panthera onca (Jaguar)"
            if "(" in label:
                scientific = label.split("(")[0].strip()
                common = label.split("(")[1].replace(")", "").strip()
            else:
                scientific = label
                common = label
                
            return {
                "species_scientific": scientific,
                "species_common": common,
                "species_confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Error en BioCLIP: {e}")
            return None
