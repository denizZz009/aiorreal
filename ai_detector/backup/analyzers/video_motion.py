"""Video motion vector analizi"""

import numpy as np
from typing import List, Dict
from ..utils.image_utils import compute_optical_flow


class VideoMotionAnalyzer:
    """Optical flow ve motion consistency analizi"""
    
    def analyze_motion_vectors(self, frames: List[np.ndarray]) -> Dict:
        """Motion vector consistency"""
        if len(frames) < 2:
            return {'is_irregular': False, 'confidence': 0.0}
        
        motion_magnitudes = []
        
        for i in range(len(frames) - 1):
            magnitude, angle = compute_optical_flow(frames[i], frames[i + 1])
            avg_magnitude = np.mean(magnitude)
            motion_magnitudes.append(avg_magnitude)
        
        # Motion magnitude variance
        motion_variance = np.var(motion_magnitudes)
        
        # AI videos: erratic (high variance) or overly smooth (low variance)
        is_irregular = motion_variance < 0.5 or motion_variance > 50.0  # Empirical
        
        return {
            'motion_variance': float(motion_variance),
            'is_irregular': is_irregular,
            'confidence': 0.6 if is_irregular else 0.0
        }
    
    def analyze_motion_smoothness(self, frames: List[np.ndarray]) -> Dict:
        """Motion smoothness analizi"""
        if len(frames) < 3:
            return {'is_unnatural': False, 'confidence': 0.0}
        
        # Consecutive motion differences
        motion_diffs = []
        
        for i in range(len(frames) - 2):
            mag1, _ = compute_optical_flow(frames[i], frames[i + 1])
            mag2, _ = compute_optical_flow(frames[i + 1], frames[i + 2])
            
            diff = np.mean(np.abs(mag1 - mag2))
            motion_diffs.append(diff)
        
        avg_diff = np.mean(motion_diffs)
        
        # Çok düşük = overly smooth (AI)
        is_unnatural = avg_diff < 0.1  # Empirical
        
        return {
            'avg_motion_diff': float(avg_diff),
            'is_unnatural': is_unnatural,
            'confidence': 0.5 if is_unnatural else 0.0
        }
    
    def analyze(self, frames: List[np.ndarray]) -> Dict:
        """Tüm motion analizlerini çalıştır"""
        vector_result = self.analyze_motion_vectors(frames)
        smoothness_result = self.analyze_motion_smoothness(frames)
        
        return {
            'motion_vector_irregular': vector_result['is_irregular'],
            'details': {
                'motion_vectors': vector_result,
                'motion_smoothness': smoothness_result
            }
        }
