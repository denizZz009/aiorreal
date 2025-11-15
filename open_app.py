"""Uygulamayı tarayıcıda aç"""

import webbrowser
import time
import requests

print("AI Detection System başlatılıyor...")
print("Sunucu kontrolü yapılıyor...")

# API'nin hazır olmasını bekle
max_retries = 10
for i in range(max_retries):
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
        if response.status_code == 200:
            print("✅ API sunucusu hazır!")
            break
    except:
        if i < max_retries - 1:
            print(f"Bekleniyor... ({i+1}/{max_retries})")
            time.sleep(1)
        else:
            print("⚠️ API sunucusuna bağlanılamadı!")
            print("Lütfen 'python run_server.py' komutunu çalıştırın")
            input("Devam etmek için Enter'a basın...")
            exit(1)

# Tarayıcıda aç
print("\n🚀 Tarayıcıda açılıyor...")
print("URL: http://localhost:8000")
webbrowser.open("http://localhost:8000")

print("\n✅ Uygulama başlatıldı!")
print("API Docs: http://localhost:8000/docs")
print("Frontend: http://localhost:8000")
