# Railway Backend Deploy Rehberi (TASK-161, iskelet)

> Not: Bu doküman bir iskelet/rehberdir. Gerçek Railway hesabı ve deploy
> işlemi dış servis erişimi gerektirdiğinden Backend ajanı tarafından
> gerçekleştirilmemiştir; DevOps/Product Owner tarafından uygulanmalıdır.

## 1. Ön Koşullar

- GitHub reposu Railway hesabına bağlı olmalı.
- Neon connection string'leri hazır olmalı (bkz. `docs/neon_setup.md`).

## 2. Servis Oluşturma

1. Railway → New Project → Deploy from GitHub repo.
2. Root directory: `backend/` (Dockerfile build).
3. İkinci bir servis oluşturun: **Celery worker** — aynı repo/Dockerfile,
   farklı start command:
   ```
   celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
   ```
4. Railway Redis eklentisini ekleyin (Add Plugin → Redis) veya Upstash Redis
   kullanın; `REDIS_URL`'i her iki servise de env olarak verin.

## 3. Environment Variables

`.env.example` (kök dizin) listesindeki tüm değişkenleri Railway panelinden
her iki servise de girin. Özellikle:

- `DATABASE_URL` (Neon pooled)
- `DATABASE_URL_SYNC` (Neon direct — yalnızca release command için gerekli)
- `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY` (openssl rand -hex 32 ile üretin)
- `HF_API_TOKEN`, `HF_MODEL_ID`
- `GITHUB_API_TOKEN`
- `CORS_ORIGINS` (prod Vercel URL'i dahil)

## 4. Release Command

FastAPI servisinin **Release Command**'ı:

```
alembic upgrade head
```

Bu, her deploy öncesi migration'ların otomatik uygulanmasını sağlar.

## 5. Health Check

Railway "Healthcheck Path" ayarını `/api/v1/health` olarak yapılandırın
(kök `/health` de mevcuttur, TASK-101 uyumluluğu için).

## 6. Keep-Alive (TASK-304)

Neon compute auto-suspend nedeniyle ilk istekte cold start yaşanabilir.
Railway Cron Job (veya harici bir uptime monitor, örn. UptimeRobot) ile
`https://<railway-url>/health` adresine 5 dakikada bir istek atılması önerilir.

## 7. Doğrulama

```bash
curl https://<railway-url>/api/v1/health
# {"status":"ok"}
```
