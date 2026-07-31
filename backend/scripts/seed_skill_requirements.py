"""Pozisyon-beceri seed script (TASK-206).

8-12 pozisyon için Türkçe gereksinim dokümanlarını chunk'layıp embed eder ve
`document_embedding` tablosuna `document_id=NULL,
metadata={source_label: "skill_requirement", position_key: "..."}` olarak yazar.

Idempotent: aynı `position_key` için önce mevcut kayıtları siler, sonra yeniden ekler.

Kullanım (konteyner içinde):
    python scripts/seed_skill_requirements.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.db.session import async_session_maker  # noqa: E402
from app.models.document_embedding import DocumentEmbedding  # noqa: E402
from app.services.embedding_service import encode  # noqa: E402
from app.utils.text_chunker import chunk_text  # noqa: E402

POSITIONS: dict[str, str] = {
    "google_swe_l3": """
Google SWE L3 (Junior/Mid Software Engineer) pozisyonu için temel gereksinimler:
Veri yapıları ve algoritmalar konusunda derinlemesine bilgi (diziler, ağaçlar, graf'lar,
hash tabloları, sıralama ve arama algoritmaları). Big-O notasyonu ile zaman/alan
karmaşıklığı analizi yapabilme. Sistem tasarımı temelleri: ölçeklenebilirlik, veritabanı
seçimi, cache stratejileri, yük dengeleme. En az bir üretim dilinde (Python, Java, C++,
Go) ileri seviye programlama becerisi. Dağıtık sistemler kavramlarına aşinalık:
consistency, availability, partition tolerance (CAP teoremi). Kod okunabilirliği ve
test yazma alışkanlığı (unit test, entegrasyon testi). Git ve code review süreçlerine
hakimiyet. Google'ın mülakat sürecinde algoritmik problemler LeetCode medium/hard
seviyesinde sorulur; davranışsal mülakatlarda Googleyness & Leadership değerlendirilir.
İşbirlikçi çalışma, büyük ölçekli kod tabanlarında gezinme ve teknik tasarım dokümanı
yazma becerisi beklenir.
""",
    "ml_engineer": """
Machine Learning Engineer pozisyonu için temel gereksinimler: Python ve NumPy, Pandas,
Scikit-learn gibi kütüphanelerde yetkinlik. PyTorch veya TensorFlow ile derin öğrenme
model eğitimi ve deployment deneyimi. İstatistik, olasılık ve doğrusal cebir temelleri.
Veri ön işleme, feature engineering ve model değerlendirme metrikleri (precision,
recall, F1, ROC-AUC) konusunda bilgi. MLOps araçlarına aşinalık: model versiyonlama,
CI/CD for ML, model monitoring. Büyük veri işleme araçları (Spark, Hadoop) hakkında
temel bilgi. Fine-tuning, transfer learning ve QLoRA gibi verimli eğitim tekniklerine
hakimiyet. Bulut platformlarında (AWS SageMaker, GCP Vertex AI) model deploy etme
deneyimi. Araştırma makalelerini okuyup uygulamaya dökebilme yeteneği.
""",
    "frontend_developer": """
Frontend Developer pozisyonu için temel gereksinimler: HTML5, CSS3 ve modern
JavaScript (ES6+) konusunda ileri seviye bilgi. React, Vue veya Angular gibi en az bir
modern framework'te üretim deneyimi. State management (Redux, Zustand, Pinia) ve
component mimarisi tasarımı. Responsive tasarım, erişilebilirlik (a11y) standartları
(WCAG) ve cross-browser uyumluluk. Performans optimizasyonu: lazy loading, code
splitting, bundle boyutu azaltma. TypeScript kullanımı ve tip güvenliği. REST/GraphQL
API entegrasyonu. Test kütüphaneleri (Jest, React Testing Library, Cypress) ile birim
ve uçtan uca test yazma. Build araçları (Vite, Webpack) hakkında bilgi. UI/UX
prensiplerine duyarlılık ve tasarımcılarla işbirliği yapabilme.
""",
    "backend_developer": """
Backend Developer pozisyonu için temel gereksinimler: En az bir backend dilinde
(Python, Java, Node.js, Go) ileri seviye deneyim. RESTful API tasarımı ve
dokümantasyonu (OpenAPI/Swagger). İlişkisel (PostgreSQL, MySQL) ve NoSQL (MongoDB,
Redis) veritabanı tasarımı ve optimizasyonu. Kimlik doğrulama/yetkilendirme (JWT,
OAuth2) implementasyonu. Mesaj kuyrukları (RabbitMQ, Kafka) ve asenkron görev işleme
(Celery) deneyimi. Mikroservis mimarisi ve container teknolojileri (Docker,
Kubernetes). Güvenlik en iyi pratikleri: SQL injection, XSS, CSRF koruması. CI/CD
pipeline kurulumu ve otomatik test entegrasyonu. Sistem tasarımı ve ölçeklenebilirlik
prensipleri (caching, load balancing, database sharding).
""",
    "data_scientist": """
Data Scientist pozisyonu için temel gereksinimler: İstatistiksel analiz ve hipotez
testi konusunda güçlü temel. Python (Pandas, NumPy, Matplotlib) veya R ile veri
analizi. SQL ile ileri seviye sorgu yazma ve veri modelleme. Makine öğrenmesi
algoritmaları (regresyon, sınıflandırma, kümeleme) konusunda pratik deneyim. Veri
görselleştirme araçları (Tableau, PowerBI veya Python kütüphaneleri) kullanımı. A/B
test tasarımı ve sonuç yorumlama. Büyük veri setleriyle çalışma deneyimi. İş
paydaşlarına teknik bulguları anlaşılır şekilde sunma (storytelling with data)
becerisi. Jupyter notebook ile araştırma ve prototipleme.
""",
    "devops_engineer": """
DevOps Engineer pozisyonu için temel gereksinimler: Linux sistem yönetimi ve shell
scripting. Docker ve Kubernetes ile konteyner orkestrasyon deneyimi. CI/CD pipeline
kurulumu (GitHub Actions, Jenkins, GitLab CI). Infrastructure as Code araçları
(Terraform, Ansible) kullanımı. Bulut platformları (AWS, GCP, Azure) üzerinde
altyapı yönetimi. Monitoring ve logging araçları (Prometheus, Grafana, ELK stack).
Ağ temelleri: DNS, load balancing, reverse proxy (Nginx). Güvenlik ve secret
management (Vault, KMS). Yüksek erişilebilirlik ve felaket kurtarma planlaması
konusunda bilgi.
""",
    "mobile_developer": """
Mobile Developer pozisyonu için temel gereksinimler: iOS (Swift) veya Android
(Kotlin) native geliştirme ya da React Native/Flutter ile cross-platform geliştirme
deneyimi. Mobil UI/UX prensipleri ve platform tasarım rehberlerine (Material Design,
Human Interface Guidelines) hakimiyet. REST API entegrasyonu ve yerel veri
depolama (SQLite, Realm). Performans optimizasyonu ve bellek yönetimi. Push
notification, deep linking ve uygulama içi satın alma entegrasyonları. App
Store/Play Store yayınlama süreçleri. Test araçları (XCTest, Espresso) ile
otomatik test yazma.
""",
    "product_manager": """
Product Manager pozisyonu için temel gereksinimler: Ürün stratejisi oluşturma ve
yol haritası (roadmap) yönetimi. Kullanıcı araştırması ve veri odaklı karar verme
(analytics, A/B testing). Paydaş yönetimi ve çapraz fonksiyonlu takımlarla
(mühendislik, tasarım, pazarlama) etkili iletişim. Agile/Scrum metodolojilerine
hakimiyet, backlog önceliklendirme. Ürün metriklerini (retention, engagement,
conversion) analiz edebilme. Teknik kavramları anlama ve mühendislik ekibiyle
teknik fizibilite tartışabilme yeteneği. Pazar araştırması ve rakip analizi yapma.
""",
}


async def seed() -> None:
    async with async_session_maker() as db:
        for position_key, doc_text in POSITIONS.items():
            await db.execute(
                text("DELETE FROM document_embedding WHERE metadata->>'position_key' = :pk"),
                {"pk": position_key},
            )
            await db.commit()

            chunks = chunk_text(doc_text.strip())
            if not chunks:
                continue
            vectors = await encode([c["content"] for c in chunks])

            for chunk, vector in zip(chunks, vectors, strict=False):
                db.add(
                    DocumentEmbedding(
                        document_id=None,
                        content=chunk["content"],
                        embedding=vector,
                        doc_metadata={
                            "chunk_index": chunk["chunk_index"],
                            "source_label": "skill_requirement",
                            "position_key": position_key,
                        },
                    )
                )
            await db.commit()
            print(f"[seed] {position_key}: {len(chunks)} chunk eklendi.")

    print(f"[seed] Toplam {len(POSITIONS)} pozisyon seed edildi.")


if __name__ == "__main__":
    asyncio.run(seed())
