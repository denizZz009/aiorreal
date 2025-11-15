"""Karar motoru - Skorlama ve karar verme"""

from typing import Dict, List, Tuple
from .thresholds import SCORE_WEIGHTS, get_verdict, get_confidence


class DecisionEngine:
    """Analiz sonuçlarını skorlayıp karar veren motor"""
    
    def __init__(self):
        self.scores = {}
        self.evidence = []
        
    def add_detection(self, detection_type: str, detected: bool, 
                     evidence_text: str = None):
        """Tespit sonucu ekle"""
        if detected and detection_type in SCORE_WEIGHTS:
            self.scores[detection_type] = SCORE_WEIGHTS[detection_type]
            if evidence_text:
                self.evidence.append(evidence_text)
    
    def add_metric_score(self, metric_name: str, value: float, 
                        threshold: float, comparison: str,
                        evidence_text: str = None):
        """
        Metrik bazlı skor ekle
        comparison: 'less', 'greater', 'between'
        """
        detected = False
        
        if comparison == 'less' and value < threshold:
            detected = True
        elif comparison == 'greater' and value > threshold:
            detected = True
        elif comparison == 'between':
            # threshold tuple olmalı (min, max)
            if isinstance(threshold, tuple):
                detected = threshold[0] <= value <= threshold[1]
        
        if detected and metric_name in SCORE_WEIGHTS:
            self.scores[metric_name] = SCORE_WEIGHTS[metric_name]
            if evidence_text:
                self.evidence.append(evidence_text)
    
    def calculate_verdict(self) -> Dict:
        """Final kararı hesapla"""
        total_score = sum(self.scores.values())
        verdict = get_verdict(total_score)
        confidence = get_confidence(total_score)
        
        return {
            'verdict': verdict,
            'confidence': round(confidence, 3),
            'total_score': total_score,
            'scores': self.scores,
            'evidence': self.evidence
        }
    
    def reset(self):
        """Skorları sıfırla"""
        self.scores = {}
        self.evidence = []
