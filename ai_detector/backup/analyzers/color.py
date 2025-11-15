"""Renk ve ışık tutarlılığı analizi"""

import numpy as np
import cv2
from typing import Dict
from ..decision.thresholds import ANALYSIS_THRESHOLDS


class ColorAnalyzer:
    """RGB channel ve renk tutarlılığı analizi"""
    
    def analyze_rgb_correlation(self, image: np.ndarray) -> Dict:
        """RGB channel korelasyon analizi"""
        r, g, b = cv2.split(image)
        
        # Flatten
        r_flat = r.flatten()
        g_flat = g.flatten()
        b_flat = b.flatten()
        
        # Korelasyonlar
        r_g_corr = np.corrcoef(r_flat, g_flat)[0, 1]
        r_b_corr = np.corrcoef(r_flat, b_flat)[0, 1]
        g_b_corr = np.corrcoef(g_flat, b_flat)[0, 1]
        
        avg_corr = (r_g_corr + r_b_corr + g_b_corr) / 3
        
        # AI images: often > 0.90 (overly correlated)
        # Real: typically 0.7-0.88
        is_high = avg_corr > ANALYSIS_THRESHOLDS['rgb_correlation_ai_min']
        
        return {
            'avg_correlation': float(avg_corr),
            'r_g': float(r_g_corr),
            'r_b': float(r_b_corr),
            'g_b': float(g_b_corr),
            'is_high': is_high,
            'confidence': 0.6 if is_high else 0.0
        }
    
    def analyze_color_cast(self, image: np.ndarray) -> Dict:
        """Renk cast ve histogram uniformity"""
        r, g, b = cv2.split(image)
        
        # Her channel için histogram mode
        r_hist, _ = np.histogram(r, bins=256, range=(0, 256))
        g_hist, _ = np.histogram(g, bins=256, range=(0, 256))
        b_hist, _ = np.histogram(b, bins=256, range=(0, 256))
        
        r_mode = np.argmax(r_hist)
        g_mode = np.argmax(g_hist)
        b_mode = np.argmax(b_hist)
        
        # Mode'ların std'si
        mode_std = np.std([r_mode, g_mode, b_mode])
        
        # Çok düşük std = unnatural uniformity
        is_uniform = mode_std < 10.0  # Empirical
        
        return {
            'mode_std': float(mode_std),
            'is_unnatural': is_uniform,
            'confidence': 0.4 if is_uniform else 0.0
        }
    
    def analyze_saturation(self, image: np.ndarray) -> Dict:
        """Saturation analizi"""
        # RGB to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        
        # Saturation statistics
        mean_sat = np.mean(saturation)
        std_sat = np.std(saturation)
        
        # AI images: bazen aşırı yüksek veya düşük saturation
        is_extreme = mean_sat > 200 or mean_sat < 30
        
        return {
            'mean_saturation': float(mean_sat),
            'std_saturation': float(std_sat),
            'is_extreme': is_extreme,
            'confidence': 0.3 if is_extreme else 0.0
        }
    
    def analyze(self, image: np.ndarray) -> Dict:
        """Tüm renk analizlerini çalıştır"""
        rgb_result = self.analyze_rgb_correlation(image)
        cast_result = self.analyze_color_cast(image)
        sat_result = self.analyze_saturation(image)
        
        return {
            'rgb_correlation_high': rgb_result['is_high'],
            'details': {
                'rgb_correlation': rgb_result,
                'color_cast': cast_result,
                'saturation': sat_result
            }
        }
