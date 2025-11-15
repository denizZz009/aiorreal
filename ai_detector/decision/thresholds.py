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

# Analiz eşikleri (daha gerçekçi değerler)
ANALYSIS_THRESHOLDS = {
    # DCT frekans oranı
    'dct_freq_ratio_ai_max': 0.10,        # < 0.10 → AI (çok düşük)
    'dct_freq_ratio_real_min': 0.20,      # > 0.20 → Real
    
    # Gürültü varyansı
    'noise_variance_ai_max': 5.0,         # < 5 → AI (çok temiz)
    'noise_variance_real_min': 10.0,      # > 10 → Real
    
    # RGB korelasyon
    'rgb_correlation_ai_min': 0.95,       # > 0.95 → AI (çok yüksek)
    'rgb_correlation_real_max': 0.85,     # < 0.85 → Real
    
    # Temporal gürültü std (video)
    'temporal_noise_real_min': 2.0,       # 2.0-10.0 → Real
    'temporal_noise_real_max': 10.0,
    
    # Checkerboard pattern detection
    'checkerboard_threshold': 0.25,       # Autocorrelation peak (daha yüksek)
    
    # Edge coherence
    'edge_continuity_ai_max': 0.4,        # < 0.4 → AI (çok fragmented)
    'edge_continuity_real_min': 0.70,     # > 0.70 → Real
    
    # Watermark detection thresholds
    'corner_edge_density_threshold': 0.10,  # %10'dan fazla edge = watermark
    'frequency_watermark_peak': 0.4,        # Daha yüksek peak gerekli
    'lsb_chi_square_threshold': 10.0,       # Daha yüksek chi-square
}

def get_verdict(total_score: float) -> str:
    """Determine verdict based on total score"""
    if total_score >= VERDICT_THRESHOLDS['high_confidence']:
        return "AI-Generated (High Confidence)"
    elif total_score >= VERDICT_THRESHOLDS['medium_confidence']:
        return "AI-Generated (Medium Confidence)"
    elif total_score >= VERDICT_THRESHOLDS['suspicious']:
        return "Suspicious"
    else:
        return "Likely Real"

def get_verdict_from_confidence(confidence: float) -> str:
    """Determine verdict based on confidence score (0-1)"""
    if confidence >= 0.70:
        return "AI-Generated"
    elif confidence >= 0.50:
        return "Likely AI-Generated"
    elif confidence >= 0.30:
        return "Suspicious"
    else:
        return "Likely Real"

def get_confidence(total_score: float) -> float:
    """Güven skorunu hesapla (0-1)"""
    max_possible = sum(SCORE_WEIGHTS.values())
    return min(total_score / max_possible, 1.0)
