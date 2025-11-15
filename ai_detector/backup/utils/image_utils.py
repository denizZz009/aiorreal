"""Görüntü işleme yardımcı fonksiyonları"""

import numpy as np
import cv2
from typing import Tuple


def load_image(file_path: str) -> np.ndarray:
    """Görüntüyü yükle (RGB format)"""
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Görüntü yüklenemedi: {file_path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """RGB'yi grayscale'e çevir"""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image


def apply_gaussian_filter(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Gaussian blur uygula"""
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def extract_noise_residual(image: np.ndarray) -> np.ndarray:
    """Gürültü residual'ını çıkar"""
    denoised = apply_gaussian_filter(image, kernel_size=5)
    noise = image.astype(np.float32) - denoised.astype(np.float32)
    return noise


def compute_dct(image: np.ndarray) -> np.ndarray:
    """2D DCT hesapla"""
    gray = to_grayscale(image)
    # Float32'ye çevir ve normalize et
    gray_float = np.float32(gray) / 255.0
    dct = cv2.dct(gray_float)
    return dct


def compute_fft(image: np.ndarray) -> np.ndarray:
    """2D FFT hesapla"""
    gray = to_grayscale(image)
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)
    magnitude = np.abs(fft_shift)
    return magnitude


def detect_edges(image: np.ndarray, low_threshold: int = 50, 
                 high_threshold: int = 150) -> np.ndarray:
    """Canny edge detection"""
    gray = to_grayscale(image)
    edges = cv2.Canny(gray, low_threshold, high_threshold)
    return edges


def compute_optical_flow(frame1: np.ndarray, frame2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """İki frame arasında optical flow hesapla"""
    gray1 = to_grayscale(frame1)
    gray2 = to_grayscale(frame2)
    
    flow = cv2.calcOpticalFlowFarneback(
        gray1, gray2, None,
        pyr_scale=0.5, levels=3, winsize=15,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0
    )
    
    # Flow magnitude ve angle
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    return magnitude, angle


def compute_autocorrelation_2d(image: np.ndarray) -> np.ndarray:
    """2D autocorrelation hesapla"""
    gray = to_grayscale(image)
    
    # FFT ile autocorrelation
    fft = np.fft.fft2(gray)
    power_spectrum = np.abs(fft) ** 2
    autocorr = np.fft.ifft2(power_spectrum)
    autocorr = np.fft.fftshift(np.real(autocorr))
    
    # Normalize
    autocorr = autocorr / autocorr.max()
    
    return autocorr
