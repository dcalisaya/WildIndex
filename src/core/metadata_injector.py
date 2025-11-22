import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("WildIndex.Metadata")

class MetadataInjector:
    def __init__(self, exiftool_path: str = "exiftool"):
        self.exiftool_path = exiftool_path

    def write_metadata(self, file_path: str, metadata: Dict[str, Any], sidecar: bool = False) -> bool:
        """
        Escribe metadatos XMP/IPTC en el archivo de imagen o en un sidecar .xmp.
        Soporta: Keywords (Categoría, Especie), Description (Caption).
        """
        path = Path(file_path)
        target_path = path
        
        if sidecar:
            target_path = path.with_suffix('.xmp')
            logger.info(f"📝 Generando sidecar XMP: {target_path.name}")
        elif not path.exists():
            logger.error(f"❌ Archivo no encontrado: {file_path}")
            return False

        # 1. Preparar Tags
        tags_to_write = []
        
        # Keywords / Subject (Lista acumulativa)
        keywords = set()
        if metadata.get('md_category'):
            keywords.add(metadata['md_category'])
        if metadata.get('species_prediction'):
            keywords.add(metadata['species_prediction'])
        
        # Añadir tag de "Processed by WildIndex"
        keywords.add("WildIndex AI")

        for kw in keywords:
            tags_to_write.append(f"-XMP:Subject+={kw}")
            tags_to_write.append(f"-IPTC:Keywords+={kw}")

        # Description / Caption
        caption = metadata.get('llava_caption')
        if caption:
            # Limpiar texto para evitar problemas de shell
            clean_caption = caption.replace('"', '\\"')
            tags_to_write.append(f'-XMP:Description="{clean_caption}"')
            tags_to_write.append(f'-EXIF:ImageDescription="{clean_caption}"')
            tags_to_write.append(f'-IPTC:Caption-Abstract="{clean_caption}"')

        # Software Agent
        tags_to_write.append(f'-XMP:CreatorTool="WildIndex v1.0"')

        # 2. Construir Comando ExifTool
        # -overwrite_original: No crear archivo _original (ya trabajamos sobre copia en 'processed')
        # -P: Preservar fecha de modificación del archivo
        cmd = [
            self.exiftool_path,
            "-overwrite_original",
            "-P",
            *tags_to_write,
            str(target_path)
        ]

        # 3. Ejecutar
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False # Manejamos el error manualmente
            )
            
            if result.returncode == 0:
                logger.info(f"🏷️  Metadatos inyectados en {path.name}")
                return True
            else:
                logger.error(f"❌ Error ExifTool en {path.name}: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Excepción ejecutando ExifTool: {e}")
            return False
