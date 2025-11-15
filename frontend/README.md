# Frontend Kullanım Kılavuzu

## Hızlı Başlangıç

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Manuel Başlatma

1. Backend'i başlat:
```bash
python run_server.py
```

2. Frontend'i aç:
- `frontend/index.html` dosyasını tarayıcıda açın
- Veya: `http://localhost:8000` üzerinden serve edin

## Özellikler

### 📁 Dosya Yükleme
- **Drag & Drop**: Dosyaları sürükleyip bırakın
- **Dosya Seçici**: "Dosya Seç" butonuna tıklayın
- **Çoklu Dosya**: Aynı anda 10 dosyaya kadar yükleyin

### 🎯 Desteklenen Formatlar
- **Görüntü**: JPG, PNG, WEBP
- **Video**: MP4, MOV, AVI

### ⚡ Hızlı Mod
- Pahalı testleri atlar
- Daha hızlı sonuç
- Batch işlemler için ideal

### 📊 Sonuç Gösterimi
- **Verdict Badge**: AI/Real kararı
- **Güven Skoru**: 0-100% confidence bar
- **Detaylı Skorlar**: Her testin puanı
- **Kanıt Listesi**: Tespit edilen anomaliler
- **İşlem Süresi**: Milisaniye cinsinden

## Arayüz Bileşenleri

### Upload Area
- Dosya sürükle-bırak desteği
- Görsel feedback (hover, drag-over)
- Format kontrolü

### Selected Files
- Yüklenen dosya listesi
- Dosya boyutu gösterimi
- Tek tek kaldırma özelliği

### Results Section
- Her dosya için ayrı kart
- Renkli verdict badge'ler
- Animasyonlu confidence bar
- Detaylı analiz bilgileri

### Info Cards
- Sistem nasıl çalışır?
- Karar seviyeleri
- Görsel rehber

## API Bağlantısı

Frontend otomatik olarak `http://localhost:8000` adresine bağlanır.

Farklı bir port kullanıyorsanız, `script.js` dosyasında değiştirin:

```javascript
const API_BASE_URL = 'http://localhost:XXXX';
```

## Hata Durumları

### API Offline
- Kırmızı status göstergesi
- Backend'in çalıştığından emin olun
- `python run_server.py` ile başlatın

### Dosya Format Hatası
- Sadece desteklenen formatları yükleyin
- Alert mesajı gösterilir

### Analiz Hatası
- Hata kartı gösterilir
- Console'da detaylı log
- API sunucusunu kontrol edin

## Responsive Tasarım

- **Desktop**: Full layout
- **Tablet**: 2-column grid
- **Mobile**: Single column, optimized touch

## Tarayıcı Desteği

- Chrome/Edge: ✅ Tam destek
- Firefox: ✅ Tam destek
- Safari: ✅ Tam destek
- IE11: ❌ Desteklenmiyor

## Geliştirme

### Stil Değişiklikleri
`style.css` dosyasını düzenleyin. CSS değişkenleri:

```css
:root {
    --primary: #6366f1;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    /* ... */
}
```

### Fonksiyon Ekleme
`script.js` dosyasına yeni fonksiyonlar ekleyin.

### API Endpoint Değişikliği
`script.js` içinde endpoint URL'lerini güncelleyin.
