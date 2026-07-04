# Neon.tech Kurulum Rehberi (TASK-102)

Bu doküman, gerçek bir Neon.tech hesabı/projesi oluşturmak için takımın (Product
Owner / DevOps sorumlusu) takip etmesi gereken adımları içerir. Backend ajanı bu
dış servis hesabını kendisi oluşturamaz; local geliştirme `docker-compose.yml`
içindeki `pgvector/pgvector:pg16` imajı ile aynı şemayla çalışır.

## 1. Hesap ve Proje Oluşturma

1. https://neon.tech adresinden ücretsiz hesap oluşturun (GitHub ile giriş önerilir).
2. "New Project" ile yeni bir proje oluşturun:
   - **Postgres version:** 16
   - **Region:** Kullanıcılara en yakın bölge (örn. AWS eu-central-1)
   - **Database name:** `careercopilot`

## 2. pgvector Extension Aktivasyonu

Neon SQL Editor'de (Console → SQL Editor) şu komutu çalıştırın:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Kontrol:

```sql
SELECT extname FROM pg_extension WHERE extname = 'vector';
```

Sonuç boş dönmüyorsa extension aktif demektir (bkz. `backend/scripts/test_neon_connection.py`).

## 3. Connection String'leri Alma

Neon Console → **Connection Details**:

- **Pooled connection** (PgBouncer, uygulama trafiği için — `DATABASE_URL`):
  ```
  postgresql+asyncpg://<user>:<password>@<pooled-host>/<db>?sslmode=require
  ```
- **Direct connection** (Alembic migration için — `DATABASE_URL_SYNC`, PgBouncer'sız):
  ```
  postgresql://<user>:<password>@<direct-host>/<db>?sslmode=require
  ```

Bu iki değişkeni Railway'in Backend servisi environment değişkenlerine ekleyin
(bkz. `.env.example`, `docs/deploy_railway.md`). **Gerçek şifreleri asla repo'ya
veya sohbet loglarına yazmayın.**

## 4. Bağlantı Testi

```bash
docker compose exec backend python scripts/test_neon_connection.py
```

Beklenen çıktı:
```
[test_neon_connection] SELECT 1 başarılı.
[test_neon_connection] pgvector extension AKTİF.
```

## 5. Migration Uygulama

```bash
docker compose exec backend alembic upgrade head
```

`alembic/env.py`, `DATABASE_URL_SYNC` (direct connection) üzerinden çalışır —
PgBouncer pooled connection'da bazı DDL/prepared statement kısıtlamaları
olabileceğinden migration'lar her zaman direct connection ile çalıştırılmalıdır.

## 6. Ücretsiz Tier Limitleri ve İzleme

- **Depolama:** 0,5 GB — `document_embedding` tablosu büyüdükçe doluluk oranını
  Neon Console → **Usage** sekmesinden takip edin.
- **%80 doluluk uyarısı alındığında:**
  1. `backend/scripts/cleanup_embeddings.py` scriptini çalıştırın (30 günden eski
     `user_document` embedding'lerini siler, kullanıcı başına 100 chunk sınırı
     uygular — bkz. TASK-303).
  2. Gerekirse eski `uploaded_document` kayıtlarının `raw_text` alanını
     manuel olarak temizleyin (büyük CV metinleri depolama kullanır).
  3. Kalıcı çözüm için ücretli plana geçiş değerlendirilebilir.
- **Compute auto-suspend:** İlk istekte 1-2 sn cold start gecikmesi normaldir;
  Railway keep-alive cron'u ile `/health` endpoint'i periyodik ping'lenerek
  bu etkiyi azaltabilirsiniz (bkz. TASK-304, `docs/deploy_railway.md`).

## 7. Bağlantı Havuzu Notu

`app/db/session.py` içindeki `create_async_engine`, `pool_size=5,
max_overflow=10, pool_pre_ping=True` ile yapılandırılmıştır. Neon'un kendi
PgBouncer pooled connection'ı ile birlikte kullanıldığında çift havuzlama
(double pooling) oluşur ancak Neon pooled URL'i transaction-mode PgBouncer
kullandığından bu, uygulama tarafındaki SQLAlchemy havuzuyla uyumludur.
