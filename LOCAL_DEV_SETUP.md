# Local Development Environment Setup

## Hızlı Başlangıç

```bash
# 1. .env dosyasını oluştur (isteğe bağlı)
cat > .env << EOF
DB_PASSWORD=onlyoffice_dev
RABBITMQ_PASSWORD=onlyoffice_dev
CORE_SECRET=dev_secret_key
EOF

# 2. Docker containers'ı başlat
docker-compose -f docker-compose.local.yml up -d

# 3. Servislerin hazır olmasını bekle (~2 dakika)
docker-compose -f docker-compose.local.yml logs -f

# 4. Browser'da aç
# DocSpace: http://localhost:8080
# DocumentServer: http://localhost:8000
# Nginx: http://localhost
```

## Sistem Bileşenleri

| Servis | Port | URL | Amaç |
|--------|------|-----|------|
| DocSpace | 8080 | http://localhost:8080 | Dosya yönetimi + Editör UI |
| DocumentServer | 8000 | http://localhost:8000 | Editör backend |
| DrawIO EMF API | 9000 | http://localhost:9000 | Diyagram konvertisyonu |
| Nginx | 80 | http://localhost | Reverse proxy |
| PostgreSQL | 5432 | localhost:5432 | Veritabanı |
| Redis | 6379 | localhost:6379 | Cache |
| RabbitMQ | 5672 | localhost:5672 | Message queue |

## Temel İşlemler

### DocSpace'e Giriş
1. http://localhost:8080 aç
2. İlk kez açıyorsa:
   - Admin hesabı oluştur (email: admin@example.com, şifre: belirle)
   - Ekip üyesi ekle
3. Dosya yükle ve editör aç

### Plugin Test
1. DocSpace'te Word dosyası aç
2. Plugin sekmesine git
3. "Draw.io EMF" plugin'ini seç
4. .drawio dosyası yükle ve EMF'ye dönüştür

### Logs İnceleme

```bash
# Tüm servislerin loglarını gör
docker-compose -f docker-compose.local.yml logs -f

# Spesifik servis logu
docker-compose -f docker-compose.local.yml logs -f documentserver
docker-compose -f docker-compose.local.yml logs -f drawio-emf-api

# Docker daemon logları
docker events
```

### Veritabanı Erişimi

```bash
# PostgreSQL console
docker exec -it drawoffice-postgres psql -U onlyoffice -d onlyoffice

# Redis CLI
docker exec -it drawoffice-redis redis-cli
```

## Sorun Giderme

### "Connection refused" hatası
```bash
# Servislerin çalışıp çalışmadığını kontrol et
docker-compose -f docker-compose.local.yml ps

# Hata varsa logları kontrol et
docker-compose -f docker-compose.local.yml logs documentserver
```

### EMF Konvertisyonu başarısız
```bash
# Backend API loglarını kontrol et
docker-compose -f docker-compose.local.yml logs drawio-emf-api

# LibreOffice/ImageMagick kontrol
docker exec drawoffice-drawio-emf-api which libreoffice
docker exec drawoffice-drawio-emf-api which convert
```

### Dosya yüklemesi başarısız
- Maksimum dosya boyutu: 100MB
- Desteklenen formatlar: .drawio
- DocSpace'te klasör izinlerini kontrol et

## Durdurma ve Temizleme

```bash
# Servisleri durdur
docker-compose -f docker-compose.local.yml down

# Tüm verileri sil (veritabanı, cache, vb.)
docker-compose -f docker-compose.local.yml down -v
```

## İleri Konfigürasyon

### Konvertisyon ayarlarını değiştir
`diagram-vector-pipeline/src/convert_svg_to_emf.py`:
- `-density` değerini artır (kalite ↑, boyut ↑)
- `-quality` değerini değiştir

### Nginx konfigürasyonu
`nginx-local.conf` dosyasını düzenle:
- Cache politikaları
- Rate limiting
- SSL (production'da)

### Yeni bir plugin ekle
1. `sdkjs-plugins/content/<plugin-name>/` klasörü oluştur
2. `config.json`, `index.html`, `code.js` ekle
3. Docker-compose'u restart et
4. DocSpace'te kullan

---

**Sorular?** Logları kontrol et veya README'de ayrıntılı bilgi var.
