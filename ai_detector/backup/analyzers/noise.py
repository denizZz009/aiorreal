"""Gürültü ve sensor izi analizi"""

import numpy as np
from scipy import stats
from typing import Dict
from ..utils.image_utils import extract_noise_residual, to_grayscale
from ..decision.thresholds import ANALYSIS_THRESHOLDS


class NoiseAnalyzer:
    """Sensor noise ve PRNU-like analiz"""
    
    def analyze_noise_variance(self, image: np.ndarray) -> Dict:
        """Gürültü varyansı analizi"""
        noise = extract_noise_residual(image)
        
        # Global variance
        noise_variance = np.var(noise)
        
        # AI images: often < 12
        # Real photos: typically > 15
        is_low = noise_variance < ANALYSIS_THRESHOLDS['noise_variance_ai_max']
        
        return {
            'variance': float(noise_variance),
            'is_low': is_low,
            'confidence': 0.7 if is_low else 0.0
        }
    
    def analyze_noise_entropy(self, image: np.ndarray) -> Dict:
        """Gürültü entropy analizi"""
        noise = extract_noise_residual(image)
        
        # Flatten ve histogram
        noise_flat = noise.flatten()
        hist, _ = np.histogram(noise_flat, bins=256, range=(-128, 128))
        hist = hist / hist.sum()  # Normalize
        
        # Entropy hesapla
        entropy = stats.entropy(hist + 1e-10)
        
        # Düşük entropy = yapay gürültü
        is_low = entropy < 4.0  # Empirical threshold
        
        return {
            'entropy': float(entropy),
            'is_low': is_low,
            'confidence': 0.5 if is_low else 0.0
        }
    
    def analyze_local_variance_map(self, image: np.ndarray) -> Dict:
        """Lokal varyans haritası - homojenlik testi"""
        gray = to_grayscale(image)
        h, w = gray.shape
        
        # 32x32 bloklar halinde varyans hesapla
        block_size = 32
        variances = []
        
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = gray[y:y+block_size, x:x+block_size]
                block_var = np.var(block)
                variances.append(block_var)
        
        if not variances:
            return {'homogeneity': 0.0, 'is_unnatural': False, 'confidence': 0.0}
        
        # Varyansların varyansı (meta-variance)
        variance_of_variances = np.var(variances)
        
        # AI images: çok homojen (düşük meta-variance)
        is_unnatural = variance_of_variances < 50.0  # Empirical
        
        return {
            'variance_of_variances': float(variance_of_variances),
            'is_unnatural': is_unnatural,
            'confidence': 0.4 if is_unnatural else 0.0
        }
    
    def chi_square_test(self, image: np.ndarray) -> Dict:
        """Pixel değer dağılımı chi-square testi"""
        gray = to_grayscale(image)
        
        # Histogram
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        
        # Beklenen: uniform distribution
        expected = len(gray.flatten()) / 256
        
        # Chi-square
        chi2 = np.sum((hist - expected) ** 2 / (expected + 1e-10))
        
        # Normalize
        chi2_normalized = chi2 / len(gray.flatten())
        
        # Çok düşük chi2 = yapay uniform dağılım
        is_anomaly = chi2_normalized < 0.5  # Empirical
        
        return {
            'chi_square': float(chi2_normalized),
            'is_anomaly': is_anomaly,
            'confidence': 0.3 if is_anomaly else 0.0
        }
    
    def analyze(self, image: np.ndarray) -> Dict:
        """Tüm gürültü analizlerini çalıştır"""
        variance_result = self.analyze_noise_variance(image)
        entropy_result = self.analyze_noise_entropy(image)
        local_var_result = self.analyze_local_variance_map(image)
        chi2_result = self.chi_square_test(image)
        
        # Genel karar
        noise_variance_low = variance_result['is_low']
        
        return {
            'noise_variance_low': noise_variance_low,
            'details': {
                'variance': variance_result,
                'entropy': entropy_result,
                'local_variance': local_var_result,
                'chi_square': chi2_result
            }
        }
