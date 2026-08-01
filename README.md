# Takım İsmi

**Takım 82**

---

# Ürün ile İlgili Bilgiler

## Takım Elemanları ve Rolleri

| İsim | Rol |
|---|---|
| Ömer Faruk Yelman | Product Owner |
| Hatice Rana Yamaç | Scrum Master |
| Emir Selengil | Team Member / Developer |
| Beyza Nur Çelik | Team Member / Developer |
| Büşra Arslan | Team Member / Developer |

## Ürün İsmi

**CareerAI**

## Ürün Açıklaması

CareerAI, öğrencilerin ve yeni mezunların kariyer hedeflerine ulaşmalarını kolaylaştırmak amacıyla geliştirilen yapay zekâ destekli bir kariyer danışmanlığı platformudur.

Kullanıcılar CV'lerini sisteme yükleyebilir, GitHub ve LinkedIn hesaplarını bağlayabilir. Yapay zekâ bu verileri analiz ederek kullanıcının mevcut yetkinliklerini değerlendirir, eksik becerilerini belirler ve hedeflediği pozisyona ulaşması için kişiselleştirilmiş bir kariyer gelişim planı sunar.

Sistem yalnızca eksik yönleri göstermekle kalmaz; aynı zamanda haftalık çalışma planı oluşturur, teknik mülakat simülasyonları gerçekleştirir ve kullanıcıya hedeflediği kariyer yolunda takip edebileceği bir roadmap önerir. Çoklu AI Agent mimarisi sayesinde CV analizi, skill gap analizi, roadmap oluşturma ve mülakat simülasyonu gibi süreçler ayrı uzman ajanlar tarafından yürütülerek daha kapsamlı ve kişiselleştirilmiş sonuçlar elde edilmesi hedeflenmektedir.

## Ürün Özellikleri

- CV yükleme ve otomatik analiz
- CV bilgilerini düzenleme
- GitHub hesabı entegrasyonu
- LinkedIn profil entegrasyonu
- Yapay zekâ ile beceri eksikliği analizi
- Kişiselleştirilmiş kariyer yol haritası oluşturma
- Haftalık çalışma planı hazırlama
- AI destekli teknik mülakat simülasyonu
- AI sohbet asistanı ile kariyer danışmanlığı
- Dashboard üzerinden kariyer gelişiminin takip edilmesi
- Çoklu AI Agent mimarisi
  - CV Agent
  - Skill Gap Agent
  - Roadmap Agent
  - Interview Agent
- Kullanıcının hedeflediği şirkete veya pozisyona göre öneriler sunma
- İlerleme ve gelişim takibi

## Hedef Kitle

- Üniversite öğrencileri
- Yeni mezun yazılım geliştiriciler
- Staj arayan öğrenciler
- Junior seviyedeki yazılım mühendisleri
- Kariyer değişikliği yapmak isteyen bireyler
- Teknik mülakatlara hazırlanan adaylar
- Yazılım alanında kendini geliştirmek isteyen kişiler

---

# Product Backlog

Product backlog, CareerAI platformunun temel kullanıcı akışını ve yapay zekâ destekli analiz süreçlerini kapsayacak şekilde hazırlanmıştır.

Backlog oluşturulurken önceliklendirme şu kriterlere göre yapılmıştır:

- Kullanıcının ürünü ilk kez deneyimleyebilmesi için gerekli temel ekranlar
- CV yükleme ve analiz akışının oluşturulması
- Kullanıcının mevcut yetkinliklerini ve eksik becerilerini görebilmesi
- Kariyer yol haritası ve mülakat simülasyonu gibi ürünün ana değer önerisini gösteren özellikler
- Backend ve gerçek AI entegrasyonlarına temel oluşturacak frontend yapısının hazırlanması

## Product Backlog URL

[Miro Product Backlog Board](https://miro.com/app/board/uXjVHHXhof0=/)

---

# Sprint 1

## Sprint Notları

Sprint 1 kapsamında CareerAI projesinin temel kullanıcı arayüzünün oluşturulması ve kullanıcının platformdaki ana akışları deneyimleyebilmesi hedeflenmiştir. Bu sprintte öncelik, backend ve gerçek yapay zekâ entegrasyonlarından önce ürünün temel frontend iskeletini ve kullanıcı deneyimini ortaya çıkarmak olmuştur.

## Sprint İçinde Tamamlanması Hedeflenen Puan

**Sprint hedef puanı:** 100 puan

Sprint 1 için seçilen işler, ürünün ilk kullanılabilir prototipini ortaya çıkaracak şekilde belirlenmiştir. Story point dağılımı, işlerin kapsamı ve geliştirme zorluğu dikkate alınarak yapılmıştır.

| Backlog Item | Açıklama | Story Point | Durum |
|---|---|---:|---|
| Kullanıcı kayıt ve giriş ekranları | Kullanıcının sisteme kayıt olup giriş yapabilmesi | 10 | Tamamlandı |
| Dashboard ekranı | Kullanıcının kariyer gelişimini genel olarak takip edebilmesi | 15 | Tamamlandı |
| CV yükleme ekranı | Kullanıcının CV dosyasını sisteme yükleyebilmesi | 10 | Tamamlandı |
| CV düzenleme ekranı | Kullanıcının CV bilgilerinde düzenleme yapabilmesi | 10 | Tamamlandı |
| GitHub entegrasyon ekranı | Kullanıcının GitHub hesabını bağlayabileceği arayüzün hazırlanması | 10 | Tamamlandı |
| Skill Gap Analysis ekranı | Kullanıcının eksik becerilerini görüntüleyebileceği analiz ekranı | 15 | Tamamlandı |
| Career Roadmap ekranı | Kullanıcıya kariyer yol haritası sunan ekranın hazırlanması | 15 | Tamamlandı |
| Interview Simulation ekranı | Teknik mülakat simülasyonu için temel ekranın hazırlanması | 10 | Tamamlandı |
| AI Chat ekranı | Kariyer danışmanlığı için AI sohbet ekranının hazırlanması | 5 | Tamamlandı |

**Tamamlanan puan:** 100 / 100

> Not: Backend servisleri, gerçek AI Agent entegrasyonları, LinkedIn API bağlantısı ve gerçek zamanlı veri işleme süreçleri sonraki sprintlere bırakılmıştır.

## Backlog Düzeni ve Story Seçimleri

Product backlog, ürünün temel değer önerisini en kısa sürede görünür hâle getirecek şekilde düzenlenmiştir. İlk sprintte özellikle kullanıcının sisteme giriş yapması, CV yüklemesi, beceri analizini görüntülemesi, kariyer yol haritasını incelemesi ve mülakat simülasyonu başlatabilmesi gibi temel kullanıcı senaryoları seçilmiştir.

Sprint 1 için seçilen story'ler aşağıdaki gerekçelere göre belirlenmiştir:

- Ürünün temel kullanıcı yolculuğunu gösterecek ekranların öncelikli olması
- Akademi değerlendirmesinde ürün fikrinin somut olarak anlaşılmasını sağlayacak arayüzlerin hazırlanması
- Sonraki sprintlerde backend ve AI servislerinin bağlanabileceği modüler bir frontend yapısının oluşturulması
- Kullanıcı deneyiminin erken aşamada test edilebilir hâle getirilmesi
- CV, skill gap, roadmap ve interview gibi ürünün ana modüllerinin ilk prototiplerinin çıkarılması

Sprint board üzerinde işler genel olarak aşağıdaki akışa göre takip edilmiştir:

- **Backlog:** Henüz sprint içine alınmamış veya detaylandırılması gereken işler
- **To Do:** Sprint 1 kapsamında yapılması planlanan işler
- **In Progress:** Geliştirme süreci devam eden işler
- **Review / Test:** Kontrol ve düzenleme aşamasındaki işler
- **Done:** Tamamlanan işler

## Daily Scrum

Daily Scrum toplantıları takım üyelerinin ilerleme durumunu paylaşması, karşılaşılan problemleri belirtmesi ve bir sonraki adımların belirlenmesi amacıyla gerçekleştirilmiştir.

Toplantılarda genel olarak şu sorular üzerinden ilerlenmiştir:

- Dün ne yaptım?
- Bugün ne yapacağım?
- Önümde bir engel var mı?
- Sprint hedefini etkileyen bir gecikme veya risk var mı?

Daily Scrum toplantı çıktıları PDF olarak README içerisinde paylaşılmıştır:

[Grup82-Sprint1-DailyScrums.pdf](https://github.com/user-attachments/files/29664169/Grup82-Sprint1-DailyScrums.pdf)

## Sprint Board Screenshots

Sprint board ekran görüntüleri aşağıdaki alana eklenmelidir.

> Görselleri repo içinde `docs/sprint1/` klasörüne ekledikten sonra aşağıdaki dosya adlarını aynı şekilde kullanabilirsiniz.

### Sprint Board - Sprint Sonu

![Sprint Board Sprint Sonu](docs/sprint1/sprint1-board-son.png)

## Ürün Durumu: Ekran Görüntüleri

Sprint 1 sonunda CareerAI projesinin temel frontend ekranları hazırlanmıştır. Ürün ekran görüntüleri aşağıdaki bölümlerde paylaşılmalıdır.

> Görselleri repo içinde `docs/sprint1/product-screens/` klasörüne ekledikten sonra aşağıdaki dosya adlarını aynı şekilde kullanabilirsiniz.

### Login / Register Ekranı

![Login Register](docs/sprint1/product-screens/login.png)
![Login Register](docs/sprint1/product-screens/register.png)

### Dashboard Ekranı

![Dashboard](docs/sprint1/product-screens/dashboard.png)

### CV Yükleme Ekranı

![CV Upload](docs/sprint1/product-screens/cv-upload.png)

### CV Düzenleme Ekranı

![CV Edit](docs/sprint1/product-screens/cv-edit.png)

### GitHub Entegrasyon Ekranı

![GitHub Integration](docs/sprint1/product-screens/github-integration.png)

### Skill Gap Analysis Ekranı

![Skill Gap Analysis](docs/sprint1/product-screens/skill-gap-analysis.png)

### Career Roadmap Ekranı

![Career Roadmap](docs/sprint1/product-screens/career-roadmap.png)

### Interview Simulation Ekranı

![Interview Simulation](docs/sprint1/product-screens/interview-simulation.png)

### AI Chat Ekranı

![AI Chat](docs/sprint1/product-screens/ai-chat.png)

## Sprint Review

Sprint 1 sonunda CareerAI projesinin temel kullanıcı arayüzü büyük ölçüde tamamlanmıştır. Kullanıcının kariyer gelişim sürecini tek platform üzerinden yönetebilmesi amacıyla Dashboard, CV yükleme, CV düzenleme, GitHub entegrasyonu, beceri boşluğu analizi, kariyer yol haritası, mülakat simülasyonu ve AI sohbet ekranları tasarlanmıştır.

Sprint sonunda kullanıcı aşağıdaki işlemleri yapabilecek temel arayüzlere sahip olmuştur:

- Sisteme kayıt olabilmekte ve giriş yapabilmektedir.
- CV dosyasını sisteme yükleyebilmektedir.
- CV bilgilerinde düzenleme yapabilmektedir.
- GitHub hesabını sisteme bağlayabileceği arayüzü görüntüleyebilmektedir.
- Beceri boşluğu analizini görüntüleyebilmektedir.
- AI tarafından oluşturulacak kariyer yol haritası için hazırlanan ekranı inceleyebilmektedir.
- AI destekli mülakat simülasyonu için hazırlanan ekranı kullanabilmektedir.
- AI Chat ekranı üzerinden kariyer danışmanlığı alabileceği arayüze erişebilmektedir.

Bu sprintte ürünün frontend tarafındaki temel kullanıcı deneyimi oluşturulmuştur. Backend servisleri, gerçek AI Agent yapısı, LinkedIn entegrasyonu ve gerçek zamanlı analizlerin entegrasyonu sonraki sprintlere bırakılmıştır.

## Sprint Retrospective

### Neler İyi Gitti?

- Uygulamanın temel sayfaları planlanan süre içerisinde tamamlandı.
- Tüm ekranlarda ortak ve tutarlı bir kullanıcı arayüzü oluşturuldu.
- Kullanıcı akışı Login / Register → Dashboard → CV Analysis → Skill Gap → Roadmap → Interview → AI Chat şeklinde başarıyla tasarlandı.
- Modüler sayfa yapısı sayesinde ileride backend entegrasyonunun daha kolay yapılabileceği bir temel oluşturuldu.
- Takım içi görev paylaşımı sprint sürecinin daha düzenli ilerlemesine katkı sağladı.

### Karşılaşılan Zorluklar

- AI servisleri henüz backend ile entegre edilmediği için bazı ekranlarda örnek/mock veriler kullanıldı.
- Sayfalar arası veri aktarımı ve kullanıcı akışının düzenlenmesi planlanandan daha fazla zaman aldı.
- CV ve GitHub entegrasyonlarının gerçek API bağlantıları sonraki sprintlere bırakıldı.
- LinkedIn entegrasyonu için API erişimi ve veri çekme süreci ayrıca araştırılması gereken bir konu olarak belirlendi.

### Gelecek Sprintte Yapılacaklar

- Backend API entegrasyonlarının tamamlanması
- Çoklu AI Agent mimarisinin geliştirilmesi
  - CV Agent
  - Skill Gap Agent
  - Roadmap Agent
  - Interview Agent
- LinkedIn entegrasyonunun eklenmesi
- GitHub üzerinden gerçek veri çekme sürecinin geliştirilmesi
- AI analizlerinin gerçek LLM servisleriyle çalıştırılması
- CV dosyası üzerinden veri çıkarma ve analiz sürecinin geliştirilmesi
- Son kullanıcı testleri ve performans optimizasyonlarının yapılması

## Sprint 1 Genel Değerlendirme

Sprint 1 sonunda CareerAI projesinin kullanıcı arayüzü büyük ölçüde tamamlanmış ve ürünün temel kullanıcı deneyimi ortaya çıkarılmıştır. Bir sonraki sprintte sistemin yapay zekâ destekli karar mekanizmaları, backend bağlantıları ve veri işleme süreçlerinin geliştirilmesine odaklanılacaktır.

---

## Sprint 2

### Backlog Düzeni ve Story Seçimleri
Sprint 2 (6 Temmuz 2026 - 19 Temmuz 2026) geliştirme planlamamız, projenin en kritik anlamsal ve fonksiyonel bileşenlerini ayağa kaldırmak amacıyla **70 Story Point (SP)** olarak hedeflenmiştir. Sprint 2 kapsamında backlog yapımız ve story seçim süreçlerimiz şu şekilde yürütülmüştür:

*   **Çevik Planlama (Agile Selection):** Kullanıcının doğrudan değer alacağı 5 ana modül (CV Analizi, CV Writer, Skill Gap, Roadmap ve Interview) önceliklendirilmiştir. 
*   **Stratejik Pivot ve Limit Yönetimi (Rejected Stories):** İnce ayar (fine-tuning) için planlanan veri setinin sayısal/niteliksel kısıtları nedeniyle, jüriye en kararlı ve bütçe dostu performansı sunabilmek adına fine-tuning süreci (15 SP) iptal edilmiştir. Bunun yerine, açık kaynaklı **Mistral-7B Base modeli** gelişmiş sistem prompt'ları ve **Neon pgvector tabanlı RAG (Retrieval-Augmented Generation) pipeline'ı** ile orkestre edilmiştir. Bu pivot sayesinde 15 SP değerindeki iş paketi **"Rejected" (Reddedilenler)** sütununa aktarılmış ve proje kaynakları RAG veritabanı zenginleştirmesine kaydırılmıştır.
*   **Tamamlanma Oranı (SP Analizi):** Planlanan 55 SP değerindeki ana geliştirme işlerinin **44 SP'si (4 Büyük User Story)** backend-frontend bağlantıları ve veritabanı katmanıyla birlikte %100 "Done" sütununa taşınmıştır. Chat SSE (Server-Sent Events) streaming akışı içeren "Yapay Zeka Sohbet Asistanı" modülü (11 SP) ise arayüz tasarımları ve API'leri hazır olmasına rağmen, gerçek zamanlı token akışının tam entegrasyon cilası için "In Progress" (Devam Edenler) durumuna alınmış ve Sprint 3'e aktarılmıştır.

#### Sprint 2 Puan Durumu Tablosu
| Durum | Story Sayısı | Toplam SP | Açıklama |
| :--- | :---: | :---: | :--- |
| **Tamamlanan (Done)** | 4 | **44 SP** | CV Analizi, CV Writer, Skill Gap, Roadmap, Mülakat ve PDF Export |
| **Devam Eden (In Progress)** | 1 | **11 SP** | Sohbet (Chat) Arayüzü ve Orchestrator SSE Akışı |
| **Reddedilen / Pivot Edilen (Rejected)** | 1 | **15 SP** | Model Fine-Tuning Süreci ve QLoRA Eğitim Altyapısı |
| **SPRINT KAPASİTESİ** | **6** | **70 SP** | **%80 Başarı Oranı (Geliştirme / Core AI)** |

---

### Daily Scrum
Sprint 2 boyunca takım üyelerinin farklı lokasyonlarda bulunması ve bootcamp süresindeki yoğun takvimleri nedeniyle Daily Scrum toplantılarının anlık ve yazılı olarak **WhatsApp üzerinden yürütülmesine** karar verilmiştir.
*   Her gün düzenli olarak "Dün ne yaptım?", "Bugün ne yapacağım?" ve "Önümde bir engel (blocker) var mı?" soruları üzerinden durum güncellemeleri paylaşılmıştır.
*   Yapay Zeka modelinin fine-tune sürecindeki veri kısıtları ve RAG mimarisine geçiş kararı gibi kritik kararlar bu toplantılardaki durum değerlendirmeleri sırasında alınmıştır.

Daily Scrum yazışma geçmişleri ve toplantı çıktıları PDF formatında dokümante edilerek depoda saklanmaktadır:

[Grup82-Sprint2-DailyScrums.pdf](docs/sprint2/Grup82-Sprint2-DailyScrums.pdf)

---

### Sprint Board Screenshotları

Sprint 2 süresince Miro ve GitHub Projects üzerindeki iş takip panolarımızın gelişim süreçlerine ait ekran görüntüleri aşağıda yer almaktadır:

#### Sprint Sonu (Done, In Progress ve Rejected Kart Dağılımı)
![Sprint Board - Sprint Sonu](docs/sprint2/sprint2_completed_1.png)
![Sprint Board - Sprint Sonu (devam)](docs/sprint2/sprint2_completed_2.PNG)

---

### Ürün Durumu: Ekran Görüntüleri
Sprint 2 sonunda mock/fake veri katmanı tamamen kapatılmış, frontend ile backend (FastAPI + Celery + Neon DB) entegrasyonu tamamlanmıştır. Uygulama, modern koyu/açık tema destekli yepyeni bir tasarım sistemine kavuşturulmuştur.

#### 1. Yeni Koyu/Açık Tema Dashboard (Panel) Ekranı
![Dashboard Ekranı](docs/sprint2/product-screens/dashboard.png)

#### 2. Çok Formatlı CV & LinkedIn PDF Birleşik Yükleme Sayfası
![CV Yükleme](docs/sprint2/product-screens/cv-upload.png)

#### 3. 14 Modüler Bölüm Seçimli AI CV Oluşturucu ve Editör
![CV Builder](docs/sprint2/product-screens/cv-builder.png)

#### 4. pgvector RAG Tabanlı Skill Gap (Beceri Boşluğu) Analiz Ekranı
![Skill Gap](docs/sprint2/product-screens/skill-gap.png)

#### 5. İnteraktif Görev İşaretlemeli Haftalık Kariyer Yol Haritası (Roadmap)
![Roadmap](docs/sprint2/product-screens/roadmap.png)

#### 6. Teknik Soru-Cevap ve Süre Sayaçlı Mülakat Simülasyonu
![Mülakat](docs/sprint2/product-screens/interview.png)

#### 7. Sparkle Filigranlı ve Öneri Balonlu AI Chat (Sohbet) Sayfası
![Chat](docs/sprint2/product-screens/chat.png)

#### 8. GitHub Hesap Entegrasyonu ve Proje Çekme Ekranı
![GitHub Connect](docs/sprint2/product-screens/github-connect.png)

---

### Sprint Review
Sprint 2 **"Ürün Odaklı"** bir yaklaşımla, platformun söz verilen tüm ana özelliklerini çalışan ve birbirine bağlı birer ürün haline getirmeyi başarmıştır. Geliştirilen fonksiyonel yetkinlikler şu şekildedir:

*   **Entegrasyon Tamamlandı (No-Mock Auth):** JWT kimlik doğrulama, register, login ve oturum yönetimleri frontend tarafında Zustand persist mağazası ve Axios interceptor'ları ile tamamen backend'e bağlanmıştır.
*   **37/37 Backend Test Başarısı:** Veritabanı sahiplik kontrolleri (IDOR önleme), şifre hash'leme, dosya silme ve async Celery görevleri dâhil olmak üzere yazılan 37 backend birim ve entegrasyon testinin tamamı başarıyla geçmiştir.
*   **Güvenli CV/LinkedIn Analiz Pipeline'ı:** 5 MB limitli, `python-magic` ile gerçek magic-byte ve MIME kontrolü yapan dosya yükleme API'si tamamlanmıştır. PyMuPDF ile parse edilen özgeçmişler Celery kuyruğuna alınmakta ve Türkçe kalite skoru üretilmektedir.
*   **Modüler CV Oluşturma & PDF Çıktısı:** 14 farklı CV bölümü arasından seçim yapmayı sağlayan form yapısı Mistral-7B ile buluşturulmuş, inline editör debounced kayıt sistemine bağlanmış ve WeasyPrint ile standartlara uygun PDF indirme altyapısı kurulmuştur.
*   **pgvector RAG ve Yol Haritası:** Neon PostgreSQL üzerindeki `pgvector` eklentisiyle cosine similarity RAG benzerlik araması başarıyla çalıştırılmıştır. Hedef pozisyon ile kullanıcı becerileri karşılaştırılarak eksikler listelenmekte, kişiye özel interaktif ve saat kısıtlı haftalık yol haritaları üretilebilmektedir.
*   **Mülakat Simülasyonu:** Seçilen kategori ve zorluğa göre anlık Türkçe sorular üreten, kullanıcının cevaplarını 0-10 arası puanlayıp Türkçe geri bildirim veren ve oturum sonunda performans özeti çıkaran mülakat modülü tamamlanmıştır.

---

### Sprint Retrospective
Sprint 2 sonunda takım süreçlerimizin, çalışma dinamiklerimizin ve aldığımız teknik kararların değerlendirilmesi şu şekildedir:

#### 🟢 Neler İyi Gitti?
*   **Kod Kalitesi ve Entegrasyon Hızı:** Backend ve frontend arasındaki veri iletişimi sıfır hata ile tamamlanmış, tüm sayfalar gerçek veriye bağlanmıştır. 37 testin çalışır durumda olması regresyonları önlemiştir.
*   **Modern Tasarım Sistemi:** Uygulamanın jenerik görünümü, koyu/açık tema toggle butonu içeren, amaca uygun pastel renk paletlerine ve Lucide-react SVG ikon setlerine sahip modern bir tasarım diline kavuşturulmuştur.
*   **Güçlü Hata Yönetimi:** JSONB mutasyon takip hataları ve chat IDOR açıkları başarıyla çözüme kavuşturulmuştur.

#### 🟡 Geliştirilmesi Gerekenler / Karşılaşılan Zorluklar
*   **Fine-Tuning Veri Kısıtı ve Stratejik Pivot:** Hedeflediğimiz kalitede Türkçe kariyer diyalogu ve CV veri kümesine ulaşılamamıştır. Ekip, süreci tıkamak yerine Agile felsefesine uygun olarak hızlıca aksiyon almış ve fine-tuning model geliştirmesini iptal etmiştir. Bunun yerine **Base Model + Gelişmiş Prompt Orkestrasyonu + pgvector RAG** mimarisine geçilmiştir. Bu karar, sunucu maliyetlerini düşürmüş ve anlamsal eşleşme kalitesini %90+ seviyesinde tutmuştur.
*   **Gerçek Zamanlı Streaming Gecikmesi:** Orchestrator SSE token-streaming altyapısı yazılmış ve frontend arayüzünde kelime bazlı akış simüle edilmiştir. Ancak gerçek streaming motorunun tam entegrasyonu ve cila testleri zaman kısıtı nedeniyle Sprint 3'e aktarılmıştır.

#### 🔵 Gelecek Sprintte (Sprint 3) Neler Yapılacak?
1.  **PDF Tasarım İyileştirmesi:** Mevcut sade PDF çıktısı kurumsal standartlarda iki sütunlu profesyonel bir tasarıma (`cv_styled.html`) yükseltilecektir.
2.  **SSE Streaming Bağlantısı:** Sohbet odasındaki kelime kelime akış backend token-stream motoruna tam entegre edilecektir.
3.  **Güvenlik ve Performans:** Rate-limiting middleware (slowapi) eklenecek, sunucu cold start sürelerini azaltmak için keep-alive pingleme servisi kurulacaktır.
4.  **Canlıya Dağıtım ve Test:** Backend Railway'e (Docker + Celery), frontend ise Vercel'e deploy edilecek ve jüriye sunulmak üzere uçtan uca E2E testleri ile sunum slaytları tamamlanacaktır.

---

## Sprint 3
### Backlog Düzeni ve Story Seçimleri
Sprint 3 (20 Temmuz 2026 – 2 Ağustos 2026), TASKS.md'de planlandığı üzere **"Cilalama + Canlı Ortam + Demo"** odaklı olarak kurgulanmıştı. Ancak sprint ilerledikçe, önceki sprintlerde base model (Mistral-7B) ile üretilen çıktılarda ciddi bir **sağlamlık (robustness) sorunu** gözlemlendi: Model sık sık JSON çıktısını markdown kod bloğuna sarıyor, bu da ajanların doğrudan heuristik (yedek) moda düşmesine yol açıyordu. Ekip, planlanan "cila" işlerinden önce altyapı sağlamlığını ve canlıya alma (deploy) operasyonunu en yüksek önceliğe aldı. Sprint 3 stratejik kararları şu şekildedir:

*   **Öncelik Değişikliği (Re-plan) ve Sağlamlık:** LLM çıktı ayrıştırma sağlamlığı (`_extract_json_payload`) ve CV Agent kısmi kurtarma mekanizması önceliklendirilerek heuristik moda düşme sorunu büyük ölçüde çözüldü.
*   **Devreden İşin (Spillover) Tamamlanması:** Sprint 2'den sarkan "Doğal Dil İşleme Sohbet Odası ve GitHub Entegrasyonu" (11 SP), gerçek SSE akışı yerine kelime simülasyonuyla stabil hale getirilerek "Done" sütununa çekildi.
*   **Beklenmeyen Altyapı Değişikliği ve Deploy Başarısı:** Backend'i Render'ın ücretsiz katmanında çalıştırırken, FastAPI + Celery + yerel sentence-transformers'ın aynı container'da 512 MB sınırını aşıp OOM'a (Out of Memory) yol açtığı gözlemlendi. Embedding işlemi uzak HF Inference endpoint'ine taşınarak bu kriz aşıldı ve ürün hem Render hem Vercel'de başarıyla canlıya (production) alındı.
*   **Kapsam Daraltma (Scope Cut):** LLM çağrı sayısını ve karmaşıklığı azaltmak adına CV çıktısındaki İngilizce (text_en) desteği tamamen kaldırıldı. Uygulama artık yalnızca %100 Türkçe CV üretiyor.

---

### AI/ML Kapsam Kararı: Fine-Tuning'in Kalıcı Olarak İptali
Proje boyunca fine-tuning'e ayrılan tüm backlog maddeleri bu sprintte resmî olarak kapatılmıştır. Gerekçe tektir: **Projeye özgü, yeterli hacim ve kalitede bir Türkçe kariyer-koçluğu/CV fine-tuning veri seti temin edilememiştir.** 

*   **Kalıcı Mimari Karar:** Proje, LLM katmanında **mistralai/Mistral-7B-Instruct-v0.2** (fine-tune edilmemiş base model) + **gelişmiş Türkçe sistem prompt'ları** + **pgvector tabanlı RAG** üçlüsü üzerine kalıcı olarak sabitlenmiştir. 
*   Buna bağlı olarak TASK-141→145, TASK-241 ve TASK-343 (fine-tune vs. base karşılaştırma) görevleri tamamen iptal edilmiş, model kalitesi prompt mühendisliği ve RAG içerik zenginliğine emanet edilmiştir.

---

#### Sprint 3 Puan Durumu Tablosu
Projemizin genel 100 Puanlık hacmi üzerinden, Sprint 3 iş yükü (Sprint 3'e özgü 30 puan + Sprint 2'den devreden 11 puan) toplam **41 Puan** olarak planlanmıştır.

| Durum | Story Sayısı | Toplam SP | Açıklama |
| ------ | ------ | ------ | ------ |
| **Tamamlanan (Done)** | 3 | **31 SP** | Canlı Platform Dağıtımı ve Sunum (12 SP) + Tasarım Cilası ve Güvenlik (8 SP) + Sprint 2'den Devreden Chat/GitHub Entegrasyonu (11 SP). |
| **Ertelenen (Backlog)** | 3 | **10 SP** | Ürünün ana işleyişini bozmayan "cila" işleri: Recharts dashboard istatistikleri (5 SP), Performans/Cold-start optimizasyonu (3 SP) ve RAG Seed zenginleştirmesi (2 SP). |
| **İptal Edilen (Cancelled)** | 1 | **—** | TASK-343 (fine-tune vs. base karşılaştırma) — Fine-tuning'in tamamı iptal edildiği için kapsamdan kalıcı olarak çıkarılmıştır. |
| **SPRINT KAPASİTESİ** | **7** | **41 SP** | **Projeyi %88'lik devasa bir bitirme oranıyla canlıda tamamlama başarısı.** |

---

### Daily Scrum
Sprint 3 boyunca Daily Scrum güncellemeleri WhatsApp üzerinden yazılı olarak yürütülmeye devam edilmiştir. Bu sprintte gündemin büyük bölümünü şu konular oluşturmuştur:
*  LLM çıktılarının neden sık sık heuristik moda düştüğü ve JSON parse sorunları.
*  Render'daki bellek (OOM) sorununun teşhisi ve embedding mimarisinin HF Inference Providers'a taşınması kararı.
*  İngilizce CV desteğinin kaldırılıp kaldırılmayacağına dair kapsam (scope cut) tartışmaları.

Daily Scrum yazışma geçmişleri PDF formatında dokümante edilerek depoda saklanmaktadır:
[Grup82-Sprint3-DailyScrums.pdf](docs/sprint3/Grup82-Sprint3-DailyScrums.pdf)

---

### Sprint Board Screenshotları
#### Sprint Sonu (Done ve Backlog Kart Dağılımı)
![Sprint 3 Miro Board](docs/sprint3/sprint3.PNG)

---

### Ürün Durumu: Jüri Demo Videosu
MVP kapsamındaki tüm geliştirmeleri, çoklu ajan (Multi-Agent) mimarisini, RAG altyapısını ve ürünün canlı ortamdaki kusursuz kullanım senaryosunu izleyebileceğiniz 3 dakikalık proje tanıtım videomuz aşağıdadır:

[![CareerCopilot AI Demo İzle](https://img.youtube.com/vi/E1ozeTY9wpg/hqdefault.jpg)](https://www.youtube.com/watch?v=E1ozeTY9wpg)
*(Not: Videoyu izlemek için yukarıdaki görsele tıklayınız)*

---

### Sprint Review
Sprint 3, planlanan "cila ve demo" hedefinden çok, ürünün **temel güvenilirliğini (robustness)** artırmaya ve canlıya çıkmaya odaklanan bir sprint olmuştur. Öne çıkan sonuçlar:
*   **LLM Çıktı Sağlamlığı:** `BaseAgent._extract_json_payload()` eklenerek, base modelin markdown/açıklama ile sardığı JSON çıktıları artık ayrıştırılabiliyor. CV Agent artık `cv_score` gibi tek bir alan eksik olduğunda doğrudan tam heuristik moda düşmüyor, `parsed_skills` üzerinden kısmi kurtarma yapabiliyor.
*   **Kapsam Netleştirme:** CV üretim akışı yalnızca Türkçe'ye indirgendi. Bu durum hem LLM çağrı sayısını hem de arayüz karmaşıklığını ciddi şekilde azalttı.
*   **CV Şablonu Genişletmesi:** `cv_styled.html` PDF şablonu görsel ve layout açısından önemli ölçüde genişletildi (+235 satır); "Hakkımda" (About) bölümü uçtan uca sisteme entegre edildi.
*   **Canlı Ortam (Production) Başarısı:** Render'da karşılaşılan OOM sorununun çözülmesiyle backend (FastAPI + Celery + Neon pgvector) tam stabiliteye kavuştu. Frontend arayüzümüz Vercel üzerinden canlıya alındı ve E2E akışları doğrulandı.
*   **Denendi, Geri Alındı (Deneysel Kararlar):** Sınırlı sürede stabilizasyonu bozmamak adına, gerçek SSE token-streaming ve RAG seed zenginleştirmesi (v2 script) denenmiş, ancak sistem bütünlüğünü korumak adına ana koda alınmadan geri alınmıştır.

---

### Sprint Retrospective
#### 🟢 Neler İyi Gitti?
*   **Harika Bitirme Oranı:** 6 haftalık zorlu maratonun sonunda planlanan 100 puanlık ürün hedefini, 88 puanlık devasa bir teslimat hacmi ile **%88'lik başarı oranıyla** kapatmak, takımın Agile disiplinine sadakatinin en büyük kanıtıdır.
*   **Sorun Önceliklendirme Refleksi:** Takım, planlanan "UI cila" işlerine körü körüne devam etmek yerine, üretimi doğrudan etkileyen bir sağlamlık sorununu (LLM JSON ayrıştırma) fark edip önceliklendirdi.
*   **Gerçek Ortam Refleksi:** Deploy denemesi kâğıt üzerinde kalmadı; Render'da gerçek bir OOM sorunu gözlemlenip kök nedeniyle (yerel model yükleme) birlikte çözüldü. Ekibin kriz yönetimi harikaydı.
*   **Belirsizliğin Kalıcı Olarak Kapatılması:** İki sprint boyunca askıda kalan fine-tuning belirsizliği, açık bir kararla resmen kapatıldı ve takım enerjisini tamamen Base Model + RAG stabilizasyonuna aktardı.

#### 🟡 Geliştirilmesi Gerekenler / Karşılaşılan Zorluklar
*   **Base Model Bağımlılığı Riski:** Fine-tuning'in iptal edilmesiyle çıktı kalitesi tamamen prompt mühendisliği ve RAG içerik zenginliğine bağımlı hâle geldi. RAG seed içeriğinin pozisyon başına hâlâ ince (~120-150 kelime) kalması bu riski büyütmektedir.
*   **Son Ana Kalan Cilalar:** Eforun tamamı canlıya dağıtım ve sistem sağlamlığına (robustness) aktarıldığı için; Recharts tabanlı Dashboard istatistikleri, iskelet yükleyiciler (skeleton loaders) ve keep-alive ping servisi gibi "nice-to-have" UI cilaları 10 Puanlık bir Backlog olarak kalmıştır. Bir sonraki projelerde UI cilalarına paralel efor ayrılması hedeflenmelidir.

---

# Kullanılan Teknolojiler
*  **Frontend:** React + Vite + Tailwind CSS, TanStack Query, Zustand (state + persist), React Hook Form + Zod, lucide-react ikon seti [1].
*  **Backend:** FastAPI + SQLAlchemy 2.0 (async) + Alembic, Celery + Redis (async görev kuyruğu), PostgreSQL (Neon) + pgvector, JWT (access + refresh) + bcrypt, WeasyPrint (PDF export), PyMuPDF + python-docx (belge parse), PyGithub (GitHub entegrasyonu), python-magic (dosya güvenliği) [1].
*  **AI Servisleri:** Hugging Face Inference Providers üzerinden `mistralai/Mistral-7B-Instruct-v0.2` (fine-tune edilmemiş base model), gelişmiş Türkçe sistem prompt'ları ile orkestre edilen 5 AI Agent + Orchestrator, pgvector tabanlı RAG (Retrieval-Augmented Generation) pipeline'ı [1].
*  **Altyapı / Deploy:** Backend → Render (Docker + Celery worker aynı container'da), Veritabanı → Neon (PostgreSQL + pgvector), Celery broker → Upstash Redis, Frontend → Vercel (Canlıda).
*  **Tasarım ve Backlog:** Miro.
*  **Versiyon Kontrol:** Git & GitHub.


---


# Kurulum ve Çalıştırma

> Proje dosyaları repoya eklendikten sonra bu bölüm güncellenmelidir.

```bash
git clone https://github.com/Rana-yamach/CareerCopilot-AI.git
cd CareerCopilot-AI
npm install
npm run dev
```

---

# Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
