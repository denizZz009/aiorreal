"""Video temporal analiz modülü"""

import numpy as np
import cv2
from typing import List, Dict
from ..utils.image_utils import to_grayscale, extract_noise_residual
from ..decision.thresholds import ANALYSIS_THRESHOLDS


class VideoTemporalAnalyzer:
    """Frame-to-frame temporal consistency analizi"""
    
    def analyze_temporal_noise(self, frames: List[np.ndarray]) -> Dict:
        """Frame-to-frame gürültü tutarlılığı"""
        if len(frames) < 2:
            return {'temporal_noise_std': 0.0, 'is_anomaly': False, 'confidence': 0.0}
        
        temporal_noise_values = []
        
        for i in range(len(frames) - 1):
            frame1 = to_grayscale(frames[i])
            frame2 = to_grayscale(frames[i + 1])
            
            # Frame difference
            diff = cv2.absdiff(frame1, frame2)
            noise_level = np.std(diff)
            temporal_noise_values.append(noise_level)
        
        # Temporal noise'un std'si
        temporal_std = np.std(temporal_noise_values)
        
        # Real video: smooth (2.5-8.0)
        # AI video: erratic or too smooth
        is_anomaly = (temporal_std < ANALYSIS_THRESHOLDS['temporal_noise_real_min'] or
                     temporal_std > ANALYSIS_THRESHOLDS['temporal_noise_real_max'])
        
        return {
            'temporal_noise_std': float(temporal_std),
            'is_anomaly': is_anomaly,
            'confidence': 0.7 if is_anomaly else 0.0
        }
    
    def analyze_frame_correlation(self, frames: List[np.ndarray]) -> Dict:
        """Consecutive frame noise correlation"""
        if len(frames) < 2:
            return {'avg_correlation': 0.0, 'is_anomaly': False, 'confidence': 0.0}
        
        correlations = []
        
        for i in range(len(frames) - 1):
            noise1 = extract_noise_residual(frames[i])
            noise2 = extract_noise_residual(frames[i + 1])
            
            # Flatten ve correlation
            corr = np.corrcoef(noise1.flatten(), noise2.flatten())[0, 1]
            correlations.append(corr)
        
        avg_corr = np.mean(correlations)
        
        # Real: high correlation (0.8+)
        # AI: low (<0.5) or perfect (1.0)
        is_anomaly = avg_corr < 0.5 or avg_corr > 0.98
        
        return {
            'avg_correlation': float(avg_corr),
            'is_anomaly': is_anomaly,
            'confidence': 0.6 if is_anomaly else 0.0
        }
    
    def detect_diffusion_flicker(self, frames: List[np.ndarray]) -> Dict:
        """Diffusion model karakteristik flicker tespiti"""
        if len(frames) < 10:
            return {'flicker_detected': False, 'peak_frequency': 0.0, 'confidence': 0.0}
        
        # Her frame'in ortalama intensity'si
        intensity_timeline = [np.mean(to_grayscale(frame)) for frame in frames]
        
        # FFT
        fft = np.fft.fft(intensity_timeline)
        freqs = np.fft.fftfreq(len(intensity_timeline), d=1.0/30.0)  # 30 fps varsayımı
        
        # Magnitude
        magnitude = np.abs(fft)
        
        # 2-5 Hz aralığında peak ara
        mask = (freqs >= 2) & (freqs <= 5)
        if not np.any(mask):
            return {'flicker_detected': False, 'peak_frequency': 0.0, 'confidence': 0.0}
        
        peak_idx = np.argmax(magnitude[mask])
        peak_freq = freqs[mask][peak_idx]
        peak_magnitude = magnitude[mask][peak_idx]
        
        # Normalize
        peak_normalized = peak_magnitude / (np.mean(magnitude) + 1e-10)
        
        # Güçlü peak = flicker
        flicker_detected = peak_normalized > 3.0  # Empirical
        
        return {
            'flicker_detected': flicker_detected,
            'peak_frequency': float(peak_freq),
            'peak_strength': float(peak_normalized),
            'confidence': min(peak_normalized / 5.0, 1.0) if flicker_detected else 0.0
        }
    
    def analyze(self, frames: List[np.ndarray]) -> Dict:
        """Tüm temporal analizleri çalıştır"""
        noise_result = self.analyze_temporal_noise(frames)
        corr_result = self.analyze_frame_correlation(frames)
        flicker_result = self.detect_diffusion_flicker(frames)
        
        return {
            'temporal_flicker': flicker_result['flicker_detected'],
            'temporal_noise_anomaly': noise_result['is_anomaly'],
            'details': {
                'temporal_noise': noise_result,
                'frame_correlation': corr_result,
                'flicker': flicker_result
            }
        }
