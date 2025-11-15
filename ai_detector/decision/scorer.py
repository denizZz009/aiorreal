"""Decision engine - Scoring and verdict determination"""

from typing import Dict, List, Tuple
from .thresholds import SCORE_WEIGHTS, get_verdict, get_confidence


class DecisionEngine:
    """Engine that scores analysis results and determines verdict"""
    
    def __init__(self):
        self.scores = {}
        self.evidence = []
        
    def add_detection(self, detection_type: str, detected: bool, 
                     evidence_text: str = None):
        """Add detection result"""
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
        """Calculate final verdict"""
        total_score = sum(self.scores.values())
        confidence = get_confidence(total_score)
        
        # Use confidence-based verdict (more intuitive)
        from .thresholds import get_verdict_from_confidence
        verdict = get_verdict_from_confidence(confidence)
        
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
