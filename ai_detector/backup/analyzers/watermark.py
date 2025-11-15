"""Watermark tespit modülü"""

import numpy as np
import cv2
from typing import Dict, List, Tuple
from ..config import AI_WATERMARK_STRINGS


class WatermarkDetector:
    """Görünür ve görünmez watermark tespiti"""
    
    def __init__(self):
        self.detected_watermarks = []
    
    def detect_text_watermarks(self, image: np.ndarray) -> Dict:
        """OCR-free text pattern detection (basit edge-based)"""
        # Bu basitleştirilmiş versiyonda corner/edge yoğunluğuna bakıyoruz
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape
        
        # Corner bölgelerini kontrol et
        corners = [
            gray[0:h//10, 0:w//10],           # Top-left
            gray[0:h//10, -w//10:],           # Top-right
            gray[-h//10:, 0:w//10],           # Bottom-left
            gray[-h//10:, -w//10:],           # Bottom-right
        ]
        
        corner_names = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        detected = False
        location = None
        
        for i, corner in enumerate(corners):
            # Edge detection
            edges = cv2.Canny(corner, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Yüksek edge density = potansiyel watermark
            if edge_density > 0.05:  # %5'ten fazla edge
                detected = True
                location = corner_names[i]
                self.detected_watermarks.append(f"Corner watermark at {location}")
                break
        
        return {
            'detected': detected,
            'location': location,
            'confidence': 0.6 if detected else 0.0
        }
    
    def detect_frequency_watermark(self, image: np.ndarray) -> Dict:
        """FFT/DCT domain'de gömülü watermark tespiti"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # DCT hesapla
        gray_float = np.float32(gray) / 255.0
        dct = cv2.dct(gray_float)
        
        # Yüksek frekans bandında periyodik pattern ara
        h, w = dct.shape
        high_freq_band = dct[h//2:, w//2:]
        
        # Autocorrelation ile periyodik pattern tespit
        fft_band = np.fft.fft2(high_freq_band)
        power = np.abs(fft_band) ** 2
        autocorr = np.fft.ifft2(power)
        autocorr = np.abs(autocorr)
        
        # Merkez dışında güçlü peak var mı?
        autocorr_normalized = autocorr / autocorr.max()
        center = (autocorr.shape[0] // 2, autocorr.shape[1] // 2)
        
        # Merkez dışı maksimum
        autocorr_copy = autocorr_normalized.copy()
        autocorr_copy[center[0]-5:center[0]+5, center[1]-5:center[1]+5] = 0
        max_peak = autocorr_copy.max()
        
        detected = max_peak > 0.3  # Eşik değer
        
        if detected:
            self.detected_watermarks.append("Frequency domain watermark pattern")
        
        return {
            'detected': detected,
            'peak_strength': float(max_peak),
            'confidence': min(float(max_peak), 1.0)
        }
    
    def detect_lsb_steganography(self, image: np.ndarray) -> Dict:
        """LSB (Least Significant Bit) steganografi tespiti"""
        # LSB plane'i çıkar
        lsb_plane = image & 1
        
        # LSB plane'de randomness testi (chi-square)
        lsb_flat = lsb_plane.flatten()
        
        # Beklenen: %50 0, %50 1
        zeros = np.sum(lsb_flat == 0)
        ones = np.sum(lsb_flat == 1)
        total = len(lsb_flat)
        
        expected = total / 2
        chi_square = ((zeros - expected) ** 2 + (ones - expected) ** 2) / expected
        
        # Chi-square > 3.84 (p=0.05) ise anormal
        detected = chi_square > 3.84
        
        if detected:
            self.detected_watermarks.append("LSB steganography anomaly")
        
        return {
            'detected': detected,
            'chi_square': float(chi_square),
            'confidence': min(chi_square / 10.0, 1.0) if detected else 0.0
        }
    
    def analyze(self, image: np.ndarray) -> Dict:
        """Tüm watermark testlerini çalıştır"""
        self.detected_watermarks = []
        
        text_result = self.detect_text_watermarks(image)
        freq_result = self.detect_frequency_watermark(image)
        lsb_result = self.detect_lsb_steganography(image)
        
        overall_detected = (text_result['detected'] or 
                          freq_result['detected'] or 
                          lsb_result['detected'])
        
        max_confidence = max(
            text_result['confidence'],
            freq_result['confidence'],
            lsb_result['confidence']
        )
        
        return {
            'watermark_detected': overall_detected,
            'confidence': max_confidence,
            'detections': self.detected_watermarks,
            'details': {
                'text_watermark': text_result,
                'frequency_watermark': freq_result,
                'lsb_steganography': lsb_result
            }
        }
