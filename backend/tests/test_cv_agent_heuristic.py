"""CV Agent heuristik mod testleri (LLM/HF Inference API erişilemediğinde
kullanılan sezgisel çıkarım). Bu testler saf Python fonksiyonlarını çağırır,
veritabanı/Redis gerektirmez.
"""
from __future__ import annotations

from app.agents.cv_agent import _heuristic_cv_score, _heuristic_parsed_skills

FORMATTED_CV = """
Ahmet Yılmaz
Backend Developer
ahmet@example.com | +90 555 000 0000 | Istanbul

Özet
Python ve FastAPI konusunda deneyimli bir backend developer.

İş Deneyimi
Backend Developer
XYZ Teknoloji A.Ş.
Ocak 2022 - Günümüz
FastAPI ile mikroservis mimarisi geliştirdim, PostgreSQL ve Redis kullandım.

Yazılım Mühendisi
ABC Yazılım Ltd.
2019 - 2021
Django tabanlı e-ticaret sistemleri geliştirdim, Docker ile konteynerize ettim.

Eğitim
İstanbul Teknik Üniversitesi
Bilgisayar Mühendisliği, Lisans
2015 - 2019

Yetenekler
Python, JavaScript, Django, FastAPI, Docker, Git, PostgreSQL, Redis, AWS
"""

# LinkedIn PDF export tarzı, satır kırılımları korunmuş ama kısaltılmış ay
# isimleri kullanan (Mar, Jun gibi) yoğun metin.
LINKEDIN_DENSE = """Ahmet Yılmaz
Senior Software Engineer at Google
Istanbul, Turkey
Summary
Experienced software engineer with expertise in distributed systems.
Experience
Senior Software Engineer
Google
Mar 2021 - Present
Working on large scale distributed systems using Go and Kubernetes.
Software Engineer
Amazon
Jun 2018 - Feb 2021
Built backend services with Java and AWS.
Education
Bogazici University
Master's Degree, Computer Science
2016 - 2018
Middle East Technical University
Bachelor's Degree, Computer Engineering
2012 - 2016
Skills
Java, Go, Kubernetes, AWS, Docker, Git, Linux
"""

# Deneyimi olmayan öğrenci CV'si.
STUDENT_CV = """
Ayşe Demir
Bilgisayar Mühendisliği Öğrencisi
ayse@example.com

Eğitim
Ege Üniversitesi
Bilgisayar Mühendisliği, Lisans (devam ediyor)
2022 - 2026

Yetenekler
Python, Java, HTML, CSS, Git

Projeler
Kişisel blog uygulaması - Flask ile geliştirildi.
"""


def test_formatted_cv_extracts_skills_experience_and_education():
    result = _heuristic_parsed_skills(FORMATTED_CV)

    assert "Python" in result["languages"]
    assert "JavaScript" in result["languages"]
    assert "FastAPI" in result["frameworks"]
    assert "Django" in result["frameworks"]
    assert "Docker" in result["tools"]
    assert "PostgreSQL" in result["tools"]

    assert len(result["experience"]) == 2
    assert result["experience"][0]["title"] == "Backend Developer"
    assert result["experience"][0]["company"] == "XYZ Teknoloji A.Ş."
    assert "2022" in result["experience"][0]["period"]

    assert len(result["education"]) == 1
    assert "Üniversite" in result["education"][0]["school"]
    assert "Lisans" in result["education"][0]["degree"]


def test_linkedin_dense_export_with_abbreviated_months():
    result = _heuristic_parsed_skills(LINKEDIN_DENSE)

    assert "Java" in result["languages"]
    assert "Go" in result["languages"]
    assert "Kubernetes" in result["tools"]

    assert len(result["experience"]) == 2
    assert result["experience"][0]["title"] == "Senior Software Engineer"
    assert result["experience"][0]["company"] == "Google"
    assert result["experience"][1]["company"] == "Amazon"

    assert len(result["education"]) == 2
    schools = {entry["school"] for entry in result["education"]}
    assert "Bogazici University" in schools
    assert "Middle East Technical University" in schools


def test_student_cv_without_experience_section_returns_empty_experience():
    result = _heuristic_parsed_skills(STUDENT_CV)

    assert result["experience"] == []
    assert len(result["education"]) == 1
    assert "Ege" in result["education"][0]["school"]
    assert "Python" in result["languages"]
    assert "Flask" in result["frameworks"]


def test_heuristic_cv_score_rewards_experience_and_education():
    empty_skills = {"languages": [], "frameworks": [], "tools": [], "experience": [], "education": []}
    rich_skills = {
        "languages": ["Python", "JavaScript"],
        "frameworks": ["Django", "FastAPI"],
        "tools": ["Docker", "Git"],
        "experience": [{"title": "Backend Developer", "company": "XYZ", "period": "2022 - Present"}],
        "education": [{"school": "İTÜ", "degree": "Lisans", "period": "2015 - 2019"}],
    }

    empty_score, _ = _heuristic_cv_score(empty_skills, "")
    rich_score, explanation = _heuristic_cv_score(rich_skills, "x" * 2000)

    assert rich_score > empty_score
    assert "1 deneyim" in explanation
    assert "1 eğitim" in explanation


def test_ascii_stripped_turkish_headers_still_detected():
    """Bazı PDF metin çıkarma araçları Türkçe aksanlı karakterleri (ş, ğ, ü,
    ö, ç, ı, İ) tamamen kaybedebiliyor. "İş Deneyimi" -> "Is Deneyimi",
    "Eğitim" -> "Egitim" haline geldiğinde bile bölüm başlıkları ve tarih
    aralıkları (ör. "Gunumuz") tespit edilebilmeli.
    """
    ascii_stripped_cv = (
        "Ahmet Yilmaz\n"
        "Backend Developer\n\n"
        "Is Deneyimi\n"
        "Backend Developer\n"
        "XYZ Teknoloji A.S.\n"
        "Ocak 2022 - Gunumuz\n"
        "FastAPI ile mikroservis mimarisi gelistirdim.\n\n"
        "Egitim\n"
        "Istanbul Teknik Universitesi\n"
        "Bilgisayar Muhendisligi, Lisans\n"
        "2015 - 2019\n"
    )

    result = _heuristic_parsed_skills(ascii_stripped_cv)

    assert len(result["experience"]) == 1
    assert result["experience"][0]["title"] == "Backend Developer"
    assert result["experience"][0]["company"] == "XYZ Teknoloji A.S."
    assert "Gunumuz" in result["experience"][0]["period"]

    assert len(result["education"]) == 1
    assert "Universitesi" in result["education"][0]["school"]


def test_heuristic_parsed_skills_handles_empty_text():
    result = _heuristic_parsed_skills("")
    assert result == {
        "languages": [],
        "frameworks": [],
        "tools": [],
        "experience": [],
        "education": [],
    }
