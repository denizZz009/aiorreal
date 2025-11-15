"""Frekans domain analizi (DCT/FFT)"""

import numpy as np
import cv2
from typing import Dict
from ..utils.image_utils import compute_dct, compute_fft, to_grayscale, compute_autocorrelation_2d
from ..decision.thresholds import ANALYSIS_THRESHOLDS


class FrequencyAnalyzer:
    """DCT/FFT spektrum ve artefact analizi"""
    
    def analyze_dct_ratio(self, image: np.ndarray) -> Dict:
        """DCT frekans oranı analizi"""
        dct = compute_dct(image)
        h, w = dct.shape
        
        # Yüksek frekans (sağ-alt köşe)
        high_freq = dct[h//2:, w//2:]
        high_freq_energy = np.sum(np.abs(high_freq))
        
        # Düşük frekans (sol-üst köşe)
        low_freq = dct[:h//4, :w//4]
        low_freq_energy = np.sum(np.abs(low_freq))
        
        # Oran hesapla
        ratio = high_freq_energy / (low_freq_energy + 1e-10)
        
        # AI images: typically ratio < 0.10 (çok düşük)
        # Real photos: ratio > 0.20
        is_ai = ratio < ANALYSIS_THRESHOLDS['dct_freq_ratio_ai_max']
        
        return {
            'ratio': float(ratio),
            'is_anomaly': is_ai,
            'confidence': 0.8 if is_ai else 0.0
        }
    
    def detect_checkerboard_pattern(self, image: np.ndarray) -> Dict:
        """Diffusion model checkerboard artifact tespiti"""
        # 2D autocorrelation ile periyodik pattern ara
        autocorr = compute_autocorrelation_2d(image)
        
        h, w = autocorr.shape
        center = (h // 2, w // 2)
        
        # 8x8 ve 16x16 grid'de peak ara
        peaks_8 = []
        peaks_16 = []
        
        # 8-pixel offset'lerde peak kontrol
        for offset in [8, 16]:
            positions = [
                (center[0] + offset, center[1]),
                (center[0] - offset, center[1]),
                (center[0], center[1] + offset),
                (center[0], center[1] - offset),
            ]
            
            peak_values = []
            for pos in positions:
                if 0 <= pos[0] < h and 0 <= pos[1] < w:
                    peak_values.append(autocorr[pos[0], pos[1]])
            
            avg_peak = np.mean(peak_values) if peak_values else 0
            
            if offset == 8:
                peaks_8.append(avg_peak)
            else:
                peaks_16.append(avg_peak)
        
        max_peak_8 = max(peaks_8) if peaks_8 else 0
        max_peak_16 = max(peaks_16) if peaks_16 else 0
        max_peak = max(max_peak_8, max_peak_16)
        
        # Threshold - daha yüksek, sadece çok belirgin pattern'ler
        detected = max_peak > ANALYSIS_THRESHOLDS['checkerboard_threshold']
        
        return {
            'detected': detected,
            'peak_strength': float(max_peak),
            'confidence': min(float(max_peak) * 2, 1.0) if detected else 0.0
        }
    
    def detect_gan_grid_artifacts(self, image: np.ndarray) -> Dict:
        """GAN grid artifacts (8x8, 16x16 block boundaries)"""
        gray = to_grayscale(image)
        
        # Horizontal ve vertical gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Her 8 ve 16 pixel'de gradient topla
        h, w = gray.shape
        
        grid_scores = []
        for grid_size in [8, 16]:
            # Horizontal lines
            h_scores = []
            for y in range(grid_size, h, grid_size):
                if y < h:
                    line_strength = np.mean(np.abs(grad_y[y, :]))
                    h_scores.append(line_strength)
            
            # Vertical lines
            v_scores = []
            for x in range(grid_size, w, grid_size):
                if x < w:
                    line_strength = np.mean(np.abs(grad_x[:, x]))
                    v_scores.append(line_strength)
            
            avg_score = np.mean(h_scores + v_scores) if (h_scores or v_scores) else 0
            grid_scores.append(avg_score)
        
        max_grid_score = max(grid_scores) if grid_scores else 0
        
        # Normalize ve threshold
        detected = max_grid_score > 15.0  # Empirical threshold
        
        return {
            'detected': detected,
            'grid_strength': float(max_grid_score),
            'confidence': min(max_grid_score / 30.0, 1.0) if detected else 0.0
        }
    
    def analyze(self, image: np.ndarray) -> Dict:
        """Tüm frekans analizlerini çalıştır"""
        dct_result = self.analyze_dct_ratio(image)
        checkerboard_result = self.detect_checkerboard_pattern(image)
        gan_result = self.detect_gan_grid_artifacts(image)
        
        return {
            'freq_ratio_anomaly': dct_result['is_anomaly'],
            'checkerboard_pattern': checkerboard_result['detected'],
            'gan_grid_artifacts': gan_result['detected'],
            'details': {
                'dct_ratio': dct_result,
                'checkerboard': checkerboard_result,
                'gan_grid': gan_result
            }
        }
