"""Geometri ve yapı analizi"""

import numpy as np
import cv2
from typing import Dict
from ..utils.image_utils import detect_edges, to_grayscale
from ..decision.thresholds import ANALYSIS_THRESHOLDS


class GeometryAnalyzer:
    """Edge coherence, symmetry, perspective analizi"""
    
    def analyze_edge_coherence(self, image: np.ndarray) -> Dict:
        """Edge continuity ve coherence analizi"""
        edges = detect_edges(image)
        
        # Hough line transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                               minLineLength=30, maxLineGap=10)
        
        if lines is None:
            return {
                'continuity_score': 0.0,
                'is_fragmented': True,
                'confidence': 0.5
            }
        
        # Line sayısı ve uzunlukları
        num_lines = len(lines)
        line_lengths = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            line_lengths.append(length)
        
        avg_length = np.mean(line_lengths) if line_lengths else 0
        
        # Continuity score: uzun çizgiler = iyi coherence
        continuity_score = min(avg_length / 100.0, 1.0)
        
        # AI images: fragmented edges (low continuity)
        is_fragmented = continuity_score < ANALYSIS_THRESHOLDS['edge_continuity_ai_max']
        
        return {
            'continuity_score': float(continuity_score),
            'num_lines': num_lines,
            'avg_line_length': float(avg_length),
            'is_fragmented': is_fragmented,
            'confidence': 0.5 if is_fragmented else 0.0
        }
    
    def analyze_symmetry(self, image: np.ndarray) -> Dict:
        """Simetri ve pattern repetition analizi"""
        gray = to_grayscale(image)
        h, w = gray.shape
        
        # Horizontal symmetry
        left_half = gray[:, :w//2]
        right_half = gray[:, w//2:]
        right_half_flipped = np.fliplr(right_half)
        
        # Boyutları eşitle
        min_w = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_w]
        right_half_flipped = right_half_flipped[:, :min_w]
        
        # Correlation
        h_symmetry = np.corrcoef(left_half.flatten(), right_half_flipped.flatten())[0, 1]
        
        # Vertical symmetry
        top_half = gray[:h//2, :]
        bottom_half = gray[h//2:, :]
        bottom_half_flipped = np.flipud(bottom_half)
        
        min_h = min(top_half.shape[0], bottom_half_flipped.shape[0])
        top_half = top_half[:min_h, :]
        bottom_half_flipped = bottom_half_flipped[:min_h, :]
        
        v_symmetry = np.corrcoef(top_half.flatten(), bottom_half_flipped.flatten())[0, 1]
        
        # Aşırı simetri = yapay
        max_symmetry = max(h_symmetry, v_symmetry)
        is_unnatural = max_symmetry > 0.85
        
        return {
            'horizontal_symmetry': float(h_symmetry),
            'vertical_symmetry': float(v_symmetry),
            'is_unnatural': is_unnatural,
            'confidence': 0.4 if is_unnatural else 0.0
        }
    
    def analyze_perspective(self, image: np.ndarray) -> Dict:
        """Perspektif tutarlılığı (basitleştirilmiş)"""
        edges = detect_edges(image)
        
        # Hough lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is None or len(lines) < 4:
            return {
                'has_vanishing_point': False,
                'is_inconsistent': False,
                'confidence': 0.0
            }
        
        # Line açılarını topla
        angles = []
        for line in lines[:20]:  # İlk 20 line
            rho, theta = line[0]
            angles.append(theta)
        
        # Açı dağılımı
        angle_std = np.std(angles)
        
        # Çok düzensiz açılar = perspektif problemi
        is_inconsistent = angle_std > 1.0  # Empirical
        
        return {
            'angle_std': float(angle_std),
            'is_inconsistent': is_inconsistent,
            'confidence': 0.3 if is_inconsistent else 0.0
        }
    
    def analyze(self, image: np.ndarray) -> Dict:
        """Tüm geometri analizlerini çalıştır"""
        edge_result = self.analyze_edge_coherence(image)
        symmetry_result = self.analyze_symmetry(image)
        perspective_result = self.analyze_perspective(image)
        
        return {
            'edge_fragmented': edge_result['is_fragmented'],
            'details': {
                'edge_coherence': edge_result,
                'symmetry': symmetry_result,
                'perspective': perspective_result
            }
        }
