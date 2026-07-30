import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(_file_))))

from app.db.session import get_db
from app.services.embedding_service import EmbeddingService
from app.models.document import DocumentEmbedding

async def run_seed_v2():
    # Zenginleştirilmiş geniş içerikli RAG verileri
    enriched_data = [
        {
            "position": "Google SWE",
            "content": "Google Yazılım Mühendisi (SWE) pozisyonu için veri yapıları (Data Structures) ve algoritmalar kritik öneme sahiptir. Adayların Python, Java, C++ veya Go dillerinden en az birine çok iyi hakim olması beklenir. Sistem tasarımı (System Design) mülakatlarında ölçeklenebilir mikroservis mimarileri, load balancing, caching (Redis/Memcached) ve dağıtık sistemler (distributed systems) konuları sorulur. Ayrıca CI/CD süreçleri, Docker, Kubernetes ve bulut altyapısı (GCP/AWS) tecrübesi büyük avantaj sağlar. Liderlik prensipleri ve takım çalışmasına uyum aranır."
        },
        {
            "position": "Frontend Developer",
            "content": "Kıdemli Frontend Geliştirici pozisyonu için modern JavaScript (ES6+), TypeScript ve React.js / Next.js konularında derinlemesine bilgi şarttır. Adayların durum yönetimi (State Management) konusunda Redux veya Zustand kullanabilmesi, RESTful API'ler ve GraphQL ile entegrasyon yapabilmesi beklenir. CSS frameworkleri (Tailwind CSS, SASS) ve responsive web tasarımı olmazsa olmazdır. Ayrıca Webpack/Vite bundler optimizasyonları, Web Vitals performans metrikleri ve Jest/Cypress ile uçtan uca (E2E) test yazma yeteneği zorunluluktur."
        }
        # Buraya diğer pozisyonlarınızı da uzun açıklamalarla ekleyebilirsiniz.
    ]
    
    # Embedding (Vektörleştirme) servisi
    emb_service = EmbeddingService()
    
    async for db in get_db():
        for item in enriched_data:
            # Metni 384 boyutlu vektöre çevir
            vector = emb_service.encode(item["content"])
            
            # Veritabanına yeni chunk olarak ekle (Eski kodlara dokunmadan yeni metadata)
            new_chunk = DocumentEmbedding(
                content=item["content"],
                embedding=vector,  # İlk liste elemanı
                metadata={"source_label": "skill_requirement", "position_key": item["position"], "version": "v2"}
            )
            db.add(new_chunk)
        
        await db.commit()
        print("V2 Zenginleştirilmiş tohum (seed) verileri başarıyla pgvector'a eklendi!")
        break

if _name_ == "_main_":
    asyncio.run(run_seed_v2())
