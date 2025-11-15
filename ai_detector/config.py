"""Sistem konfigürasyonu ve sabitler"""

# Desteklenen formatlar
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi']

# Maksimum dosya boyutları (bytes)
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

# Video analiz ayarları
VIDEO_FRAME_SAMPLE_RATE = 10  # Her 10 frame'den 1'ini analiz et
MAX_FRAMES_TO_ANALYZE = 100

# Watermark template dizini
WATERMARK_TEMPLATES_DIR = "templates/watermarks"

# AI platform watermark stringleri
AI_WATERMARK_STRINGS = [
    "midjourney",
    "dall-e",
    "dall·e",
    "openai",
    "runway",
    "stable diffusion",
    "adobe firefly",
    "pika",
    "sora",
    "kling",
    "synthetic",
    "ai generated",
    "content credentials",
    "c2pa"
]

# Metadata AI software tags
AI_SOFTWARE_TAGS = [
    "midjourney",
    "dall-e",
    "stable diffusion",
    "adobe firefly",
    "runway",
    "pika labs",
    "synthesia",
    "d-id"
]
