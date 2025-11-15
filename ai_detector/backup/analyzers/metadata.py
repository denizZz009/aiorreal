"""Metadata ve EXIF analizi"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from ..config import AI_WATERMARK_STRINGS, AI_SOFTWARE_TAGS
from ..utils.file_parser import (
    read_png_chunks, extract_png_text_chunks,
    read_jpeg_segments, parse_mp4_atoms
)


class MetadataAnalyzer:
    """Dosya metadata ve EXIF analizi"""
    
    def __init__(self):
        self.suspicious_indicators = []
    
    def analyze_exif(self, file_path: str) -> Dict:
        """EXIF metadata analizi"""
        try:
            img = Image.open(file_path)
            exif_data = img._getexif()
            
            if not exif_data:
                self.suspicious_indicators.append("No EXIF data (suspicious for real camera)")
                return {
                    'has_exif': False,
                    'suspicious': True,
                    'ai_indicators': []
                }
            
            # EXIF'i okunabilir formata çevir
            exif = {TAGS.get(k, k): v for k, v in exif_data.items()}
            
            ai_indicators = []
            
            # Software tag kontrolü
            software = exif.get('Software', '').lower()
            for ai_tag in AI_SOFTWARE_TAGS:
                if ai_tag in software:
                    ai_indicators.append(f"AI software detected: {ai_tag}")
            
            # AI watermark string'leri ara
            for key, value in exif.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for watermark in AI_WATERMARK_STRINGS:
                        if watermark in value_lower:
                            ai_indicators.append(f"AI watermark in EXIF: {watermark}")
            
            # Kamera metadata eksikliği
            camera_fields = ['Make', 'Model', 'LensModel', 'FocalLength', 'ISOSpeedRatings']
            missing_camera_data = [f for f in camera_fields if f not in exif]
            
            if len(missing_camera_data) >= 3:
                self.suspicious_indicators.append("Missing camera metadata")
            
            return {
                'has_exif': True,
                'suspicious': len(ai_indicators) > 0 or len(missing_camera_data) >= 3,
                'ai_indicators': ai_indicators,
                'missing_camera_fields': missing_camera_data
            }
            
        except Exception as e:
            return {
                'has_exif': False,
                'suspicious': True,
                'error': str(e)
            }
    
    def analyze_png_metadata(self, file_path: str) -> Dict:
        """PNG chunk metadata analizi"""
        chunks = read_png_chunks(file_path)
        text_data = extract_png_text_chunks(chunks)
        
        ai_indicators = []
        
        # Text chunk'larda AI string'leri ara
        for keyword, text in text_data.items():
            keyword_lower = keyword.lower()
            text_lower = text.lower()
            
            for watermark in AI_WATERMARK_STRINGS:
                if watermark in keyword_lower or watermark in text_lower:
                    ai_indicators.append(f"AI indicator in PNG: {watermark}")
            
            # Software field
            if 'software' in keyword_lower:
                for ai_tag in AI_SOFTWARE_TAGS:
                    if ai_tag in text_lower:
                        ai_indicators.append(f"AI software in PNG: {ai_tag}")
        
        return {
            'has_metadata': len(text_data) > 0,
            'ai_indicators': ai_indicators,
            'suspicious': len(ai_indicators) > 0
        }
    
    def analyze_c2pa(self, file_path: str) -> Dict:
        """C2PA (Content Credentials) metadata kontrolü"""
        # C2PA genelde JPEG APP11 veya PNG chunk'ta bulunur
        file_ext = Path(file_path).suffix.lower()
        
        c2pa_found = False
        is_synthetic = False
        
        if file_ext in ['.jpg', '.jpeg']:
            segments = read_jpeg_segments(file_path)
            for seg_name, data in segments.items():
                data_str = data.decode('latin-1', errors='ignore').lower()
                if 'c2pa' in data_str or 'content credentials' in data_str:
                    c2pa_found = True
                    if 'synthetic' in data_str or 'ai' in data_str:
                        is_synthetic = True
        
        elif file_ext == '.png':
            chunks = read_png_chunks(file_path)
            text_data = extract_png_text_chunks(chunks)
            for keyword, text in text_data.items():
                combined = (keyword + text).lower()
                if 'c2pa' in combined or 'content credentials' in combined:
                    c2pa_found = True
                    if 'synthetic' in combined or 'ai' in combined:
                        is_synthetic = True
        
        if is_synthetic:
            self.suspicious_indicators.append("C2PA indicates synthetic content")
        
        return {
            'c2pa_found': c2pa_found,
            'is_synthetic': is_synthetic,
            'confidence': 1.0 if is_synthetic else 0.0
        }
    
    def analyze_video_metadata(self, file_path: str) -> Dict:
        """Video metadata analizi (MP4)"""
        atoms = parse_mp4_atoms(file_path)
        
        ai_indicators = []
        
        # Encoder signature
        for atom_type, data in atoms.items():
            data_str = data.decode('latin-1', errors='ignore').lower()
            
            for watermark in AI_WATERMARK_STRINGS:
                if watermark in data_str:
                    ai_indicators.append(f"AI watermark in video: {watermark}")
            
            # Synthetic video generator signatures
            synthetic_encoders = ['runway', 'pika', 'sora', 'synthesia']
            for encoder in synthetic_encoders:
                if encoder in data_str:
                    ai_indicators.append(f"Synthetic encoder: {encoder}")
        
        return {
            'ai_indicators': ai_indicators,
            'suspicious': len(ai_indicators) > 0
        }
    
    def analyze(self, file_path: str, is_video: bool = False) -> Dict:
        """Tüm metadata analizini çalıştır"""
        self.suspicious_indicators = []
        
        file_ext = Path(file_path).suffix.lower()
        
        if is_video:
            video_result = self.analyze_video_metadata(file_path)
            return {
                'metadata_suspicious': video_result['suspicious'],
                'indicators': video_result['ai_indicators']
            }
        
        # Image metadata
        exif_result = self.analyze_exif(file_path)
        c2pa_result = self.analyze_c2pa(file_path)
        
        png_result = {}
        if file_ext == '.png':
            png_result = self.analyze_png_metadata(file_path)
        
        # Combine results
        all_indicators = (
            exif_result.get('ai_indicators', []) +
            png_result.get('ai_indicators', []) +
            self.suspicious_indicators
        )
        
        return {
            'metadata_suspicious': (exif_result.get('suspicious', False) or 
                                   png_result.get('suspicious', False)),
            'c2pa_synthetic': c2pa_result['is_synthetic'],
            'indicators': all_indicators,
            'details': {
                'exif': exif_result,
                'c2pa': c2pa_result,
                'png': png_result
            }
        }
