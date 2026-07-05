# PDF Render Kütüphane Kararı (TASK-208)

## Karşılaştırılan Seçenekler

| Kriter | WeasyPrint | pdfkit (wkhtmltopdf) |
|---|---|---|
| Kurulum | Sistem paketleri (pango, cairo) gerektirir ama saf Python + apt ile Docker'da sorunsuz | Ayrı bir binary (`wkhtmltopdf`) indirilmesi/derlemesi gerekir, Docker imajı büyür ve bakımı zor |
| Türkçe karakter desteği | CSS3 + UTF-8 font desteği native, `ğ ü ş ı ö ç` sorunsuz render edilir (DejaVu Sans / Noto Sans ile test edildi) | Genelde çalışır ama font embedding sorunları bilinen bir problem alanı |
| CSS3 desteği | Modern CSS3 (flexbox kısmi, grid yok ama sayfa/print CSS güçlü) | Chromium tabanlı olmadığından CSS3 desteği sınırlı |
| Aktif geliştirme | Aktif (Kozea tarafından sürdürülüyor) | Üst kaynak proje (wkhtmltopdf) resmi olarak arşivlendi, güvenlik yamaları yavaş |
| Python entegrasyonu | Native Python kütüphanesi (`weasyprint.HTML(string=...).write_pdf()`) | Sistem binary'sine subprocess çağrısı yapar |

## Karar

**WeasyPrint** seçildi. Gerekçe: Aktif geliştirme, Türkçe karakter güvenliği,
saf Python entegrasyonu (subprocess yönetimi gerekmiyor) ve CSS3 ile sade/şık
şablon üretebilme esnekliği.

## Uygulama

- `backend/app/services/pdf_render_service.py` — Jinja2 ile HTML render edip
  `WeasyPrint HTML(string=...).write_pdf()` ile PDF üretir.
- Sprint 2 şablonu: `backend/app/templates/cv_simple.html` (tek sütun, sade).
- Sprint 3 şablonu: `backend/app/templates/cv_styled.html` (başlık vurgusu,
  renkli bölüm ayraçları, footer notu) — TASK-301.
- Docker imajı, WeasyPrint'in ihtiyaç duyduğu sistem paketlerini
  (`libpango-1.0-0`, `libpangocairo-1.0-0`, `libcairo2`, `libgdk-pixbuf2.0-0`,
  `fonts-dejavu-core`, `fonts-noto-core`) `backend/Dockerfile` içinde kurar.

## Test Notu

3 farklı `form_data` senaryosu (kısa CV, çok bölümlü CV, yalnızca Türkçe
karakter ağırlıklı içerik) ile PDF üretimi manuel olarak doğrulanmalıdır
(bkz. TASK-301 kabul kriteri). Bu doğrulama, gerçek bir HF token ile CV Writer
Agent'ın ürettiği metinler üzerinde de tekrarlanmalıdır.
