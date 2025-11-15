"""API test script"""

import requests
import sys
from pathlib import Path


def test_health():
    """Health check testi"""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_detect_image(image_path: str):
    """Görüntü analiz testi"""
    print(f"Testing image detection: {image_path}")
    
    if not Path(image_path).exists():
        print(f"File not found: {image_path}\n")
        return
    
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f, 'image/jpeg')}
        response = requests.post("http://localhost:8000/api/v1/detect", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Verdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Total Score: {result['total_score']}")
        print(f"Evidence: {result['evidence']}")
        print(f"Processing Time: {result['processing_time_ms']} ms\n")
    else:
        print(f"Error: {response.text}\n")


def test_detect_video(video_path: str):
    """Video analiz testi"""
    print(f"Testing video detection: {video_path}")
    
    if not Path(video_path).exists():
        print(f"File not found: {video_path}\n")
        return
    
    with open(video_path, 'rb') as f:
        files = {'file': (Path(video_path).name, f, 'video/mp4')}
        response = requests.post("http://localhost:8000/api/v1/detect", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Verdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Frames Analyzed: {result.get('frames_analyzed', 'N/A')}")
        print(f"Evidence: {result['evidence']}")
        print(f"Processing Time: {result['processing_time_ms']} ms\n")
    else:
        print(f"Error: {response.text}\n")


if __name__ == "__main__":
    print("=== AI Detection API Test ===\n")
    
    # Health check
    try:
        test_health()
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Make sure the API server is running: python -m uvicorn ai_detector.api.main:app --reload\n")
        sys.exit(1)
    
    # Test with sample files if provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        ext = Path(file_path).suffix.lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.webp']:
            test_detect_image(file_path)
        elif ext in ['.mp4', '.mov', '.avi']:
            test_detect_video(file_path)
        else:
            print(f"Unsupported file format: {ext}")
    else:
        print("Usage: python test_api.py <image_or_video_path>")
        print("Example: python test_api.py sample.jpg")
