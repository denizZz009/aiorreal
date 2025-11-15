"""Basit test - Dummy image ile API test"""

import requests
import numpy as np
from PIL import Image
import io

# Basit bir test görüntüsü oluştur
print("Test görüntüsü oluşturuluyor...")
img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
img = Image.fromarray(img_array)

# BytesIO'ya kaydet
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# API'ye gönder
print("API'ye gönderiliyor...")
files = {'file': ('test.png', img_bytes, 'image/png')}
response = requests.post('http://localhost:8000/api/v1/detect', files=files)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Başarılı!")
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Total Score: {result['total_score']}")
    print(f"Processing Time: {result['processing_time_ms']} ms")
    
    if result['evidence']:
        print(f"\nKanıtlar:")
        for evidence in result['evidence']:
            print(f"  - {evidence}")
else:
    print(f"\n❌ Hata: {response.text}")
