"""Tespit eşik değerleri ve skorlama ağırlıkları"""

# Skorlama ağırlıkları (0-100)
SCORE_WEIGHTS = {
    'watermark_detected': 100,      # Kesin AI tespiti
    'c2pa_synthetic': 90,            # C2PA metadata
    'metadata_suspicious': 40,       # Şüpheli metadata
    'checkboard_pattern': 40,        # Diffusion artifact
    'freq_ratio_anomaly': 30,        # DCT/FFT anomali
    'temporal_flicker': 35,          # Video flicker
    'noise_variance_low': 25,        # Düşük gürültü
    'motion_vector_irregular': 25,   # Düzensiz hareket
    'rgb_correlation_high': 20,      # Yüksek RGB korelasyon
    'shadow_inconsistent': 15,       # Tutarsız gölge
    'edge_fragmented': 15,           # Parçalı kenarlar
}

# Karar eşikleri
VERDICT_THRESHOLDS = {
    'high_confidence': 100,   # >= 100: AI-generated (HIGH)
    'medium_confidence': 60,  # >= 60: AI-generated (MEDIUM)
    'suspicious': 30,         # >= 30: SUSPICIOUS
    # < 30: Likely REAL
}

# Analiz eşikleri
ANALYSIS_THRESHOLDS = {
    # DCT frekans oranı
    'dct_freq_ratio_ai_max': 0.22,        # < 0.22 → AI
    'dct_freq_ratio_real_min': 0.25,      # > 0.25 → Real
    
    # Gürültü varyansı
    'noise_variance_ai_max': 12.0,        # < 12 → AI
    'noise_variance_real_min': 15.0,      # > 15 → Real
    
    # RGB korelasyon
    'rgb_correlation_ai_min': 0.90,       # > 0.90 → AI
    'rgb_correlation_real_max': 0.88,     # < 0.88 → Real
    
    # Temporal gürültü std (video)
    'temporal_noise_real_min': 2.5,       # 2.5-8.0 → Real
    'temporal_noise_real_max': 8.0,
    
    # Checkerboard pattern detection
    'checkerboard_threshold': 0.15,       # Autocorrelation peak
    
    # Edge coherence
    'edge_continuity_ai_max': 0.6,        # < 0.6 → AI (fragmented)
    'edge_continuity_real_min': 0.75,     # > 0.75 → Real
}

def get_verdict(total_score: float) -> str:
    """Toplam skora göre karar ver"""
    if total_score >= VERDICT_THRESHOLDS['high_confidence']:
        return "AI-generated (HIGH CONFIDENCE)"
    elif total_score >= VERDICT_THRESHOLDS['medium_confidence']:
        return "AI-generated (MEDIUM CONFIDENCE)"
    elif total_score >= VERDICT_THRESHOLDS['suspicious']:
        return "SUSPICIOUS"
    else:
        return "Likely REAL"

def get_confidence(total_score: float) -> float:
    """Güven skorunu hesapla (0-1)"""
    max_possible = sum(SCORE_WEIGHTS.values())
    return min(total_score / max_possible, 1.0)
