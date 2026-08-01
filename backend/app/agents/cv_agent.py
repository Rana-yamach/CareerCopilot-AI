"""CV Agent (TASK-203): raw_text + github_languages -> parsed_skills + cv_score.

HF Inference API üzerinden LLM çağrısı dener; token tanımlı değilse veya
LLM hata verirse (fine-tune model henüz hazır değilse), sistemi bloke
etmemek için basit sezgisel (heuristic) bir çıkarım yapar (bkz. TASKS.md
Genel Kurallar madde 3 ruhu: "bloke olma, base/placeholder ile devam et").

Heuristik mod, gerçek bir LLM'in yerini tutmaz; amaç HF Inference API
kredisi/erişimi geçici olarak kesildiğinde (ör. 402 Payment Required)
kullanıcıya "hiçbir şey"den çok daha faydalı, kaba ama makul bir ön analiz
sunmaktır.
"""
from __future__ import annotations

import re

from app.agents.base import BaseAgent
from app.models.enums import DocumentType

# ---------------------------------------------------------------------------
# Kelime dağarcığı (heuristik beceri tespiti)
# ---------------------------------------------------------------------------

COMMON_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Golang", "Go",
    "Rust", "PHP", "Ruby", "Kotlin", "Swift", "Scala", "Perl", "Dart",
    "Objective-C", "SQL", "PL/SQL", "Bash", "Shell", "PowerShell", "HTML",
    "HTML5", "CSS", "CSS3", "Sass", "SCSS", "Less", "R", "MATLAB", "Julia",
    "Groovy", "Lua", "Haskell", "Elixir", "Clojure",
]

COMMON_FRAMEWORKS = [
    "React", "React Native", "Redux", "Zustand", "Vue", "Vue.js", "Angular",
    "Svelte", "jQuery", "Next.js", "Nuxt.js", "Gatsby", "FastAPI", "Django",
    "Flask", "Spring", "Spring Boot", "Express", "Express.js", "Node.js",
    "NestJS", ".NET", "ASP.NET", "Laravel", "Symfony", "Ruby on Rails",
    "Flutter", "Xamarin", "SwiftUI", "Bootstrap", "Tailwind CSS",
    "Tailwind", "Material UI", "Ant Design", "GraphQL", "gRPC", "REST",
    "RESTful", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
    "Scikit-Learn", "Pandas", "NumPy", "OpenCV", "Hugging Face",
    "LangChain", "Matplotlib", "Seaborn", "XGBoost",
]

COMMON_TOOLS = [
    # Sürüm kontrolü / işbirliği
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello",
    "Asana", "Slack", "Notion", "Monday.com",
    # Konteyner / bulut / devops
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Google Cloud", "Linux",
    "Unix", "Windows Server", "CI/CD", "Jenkins", "GitHub Actions",
    "GitLab CI", "CircleCI", "Travis CI", "Terraform", "Ansible", "Chef",
    "Puppet", "Nginx", "Apache", "Vault", "Prometheus", "Grafana", "ELK",
    "Elasticsearch", "Logstash", "Kibana", "Datadog",
    # Veri / mesajlaşma
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle",
    "Cassandra", "DynamoDB", "Firebase", "Supabase", "Kafka", "RabbitMQ",
    "Celery", "Spark", "Hadoop", "Airflow", "BigQuery", "Snowflake",
    # Tasarım / ürün
    "Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "Canva",
    "InVision", "Miro",
    # Ofis / proje yönetimi
    "Excel", "PowerPoint", "Word", "Google Sheets", "Google Analytics",
    "Tableau", "Power BI", "Looker", "Scrum", "Kanban", "Agile",
    # Test araçları
    "Postman", "Selenium", "Jest", "Cypress", "JUnit", "Pytest", "Mocha",
    "Cucumber", "TestRail", "SoapUI",
    # IDE / editör
    "VS Code", "IntelliJ", "PyCharm", "Eclipse", "Android Studio", "Xcode",
]


def _term_pattern(term: str) -> re.Pattern[str]:
    """Terimin başında/sonunda kelime sınırı arayan, özel karakterli terimlerde
    (`C++`, `.NET`, `CI/CD` vb.) `\\b` yerine daha güvenilir çalışan bir kalıp.
    """
    escaped = re.escape(term)
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


_LANGUAGE_PATTERNS = [(term, _term_pattern(term)) for term in COMMON_LANGUAGES]
_FRAMEWORK_PATTERNS = [(term, _term_pattern(term)) for term in COMMON_FRAMEWORKS]
_TOOL_PATTERNS = [(term, _term_pattern(term)) for term in COMMON_TOOLS]


def _find_matches(text: str, patterns: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    return [term for term, pattern in patterns if pattern.search(text)]


# ---------------------------------------------------------------------------
# Bölüm başlığı tespiti (deneyim / eğitim / diğer)
# ---------------------------------------------------------------------------

EXPERIENCE_HEADER_WORDS = [
    "iş deneyimi", "iş deneyimleri", "çalışma deneyimi", "profesyonel deneyim",
    "deneyimler", "deneyim", "work experience", "professional experience",
    "employment history", "experience",
]

EDUCATION_HEADER_WORDS = [
    "eğitim bilgileri", "akademik geçmiş", "öğrenim bilgileri", "öğrenim",
    "eğitim", "academic background", "education",
]

OTHER_HEADER_WORDS = [
    "sertifikalar", "sertifika", "certifications", "certificates",
    "teknik beceriler", "yetenekler", "beceriler", "skills",
    "diller", "languages", "projeler", "projects", "referanslar",
    "references", "özet", "summary", "hakkımda", "hakkında", "about",
    "profil", "profile", "iletişim", "contact", "gönüllülük",
    "volunteering", "yayınlar", "publications", "ödüller", "awards",
    "ilgi alanları", "interests", "kurslar", "courses",
]

_TR_FOLD_MAP = str.maketrans({
    "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g", "ü": "u", "Ü": "u",
    "ö": "o", "Ö": "o", "ç": "c", "Ç": "c", "ı": "i", "İ": "i", "I": "i",
})


def _norm(text: str) -> str:
    """ASCII'ye yakın, Türkçe aksansız + küçük harfli normalize edilmiş kopya
    üretir. Karakter sayısı orijinal metinle BİREBİR aynı kalır (1:1 eşleme)
    ki bu kopya üzerinde bulunan regex eşleşme pozisyonları orijinal metinde
    de doğrudan geçerli olsun (dilim/slice almak için).

    Neden gerekli: bazı PDF metin çıkarma araçları (özellikle LinkedIn PDF
    export'ları) Türkçe aksanlı karakterleri (ş, ğ, ü, ö, ç, ı, İ) tamamen
    kaybedebiliyor — "İş Deneyimi" -> "Is Deneyimi" oluyor. Ayrıca Python'un
    yerleşik `str.lower()` fonksiyonu Türkçe büyük "İ" (U+0130) harfini
    "i" + birleşen nokta (U+0307) olmak üzere İKİ karaktere açar (Unicode tam
    case-folding), bu da tek başına `.lower()` ile başlık tespitini
    bozabiliyor. Bu fonksiyon her iki sorunu da tek seferde çözer.
    """
    return text.translate(_TR_FOLD_MAP).lower()


_ALL_HEADER_WORDS = sorted(
    {_norm(w) for w in EXPERIENCE_HEADER_WORDS + EDUCATION_HEADER_WORDS + OTHER_HEADER_WORDS},
    key=len,
    reverse=True,
)
_EXPERIENCE_HEADER_SET = {_norm(w) for w in EXPERIENCE_HEADER_WORDS}
_EDUCATION_HEADER_SET = {_norm(w) for w in EDUCATION_HEADER_WORDS}


def _build_header_regex(loose: bool) -> re.Pattern[str]:
    alternation = "|".join(re.escape(w) for w in _ALL_HEADER_WORDS)
    if loose:
        return re.compile(rf"\b(?:{alternation})\b")
    return re.compile(rf"^[ \t]*(?:{alternation})[ \t]*:?[ \t]*$", re.MULTILINE)


_HEADER_REGEX_STRICT = _build_header_regex(loose=False)
_HEADER_REGEX_LOOSE = _build_header_regex(loose=True)


def _header_positions(text: str, loose: bool) -> list[tuple[int, int, str]]:
    """Başlık kalıplarını normalize edilmiş bir kopya üzerinde arar (bkz.
    `_norm`), ama döndürülen `(start, end)` pozisyonları orijinal `text`
    üzerinde doğrudan dilimleme için kullanılabilir (1:1 karakter eşlemesi
    sayesinde).
    """
    regex = _HEADER_REGEX_LOOSE if loose else _HEADER_REGEX_STRICT
    normalized = _norm(text)
    return sorted(
        ((m.start(), m.end(), m.group(0).strip()) for m in regex.finditer(normalized)),
        key=lambda p: p[0],
    )


def _locate_section(text: str, category_headers: set[str]) -> str:
    """`category_headers`'a ait ilk başlığı bulur ve bir sonraki bilinen bölüm
    başlığına kadar olan metni döner. Önce satır başı ("strict") arar, hiçbir
    şey bulamazsa daha gevşek (metin içinde herhangi bir yerde) arar.
    """
    for loose in (False, True):
        positions = _header_positions(text, loose)
        for idx, (_, end, header) in enumerate(positions):
            if header in category_headers:
                next_start = positions[idx + 1][0] if idx + 1 < len(positions) else min(len(text), end + 4000)
                return text[end:next_start]
    return ""


# ---------------------------------------------------------------------------
# Tarih aralığı tespiti
# ---------------------------------------------------------------------------

# NOT: bu kalıplar normalize edilmiş (bkz. `_norm`: aksansız + küçük harf)
# metin üzerinde aranır, bu yüzden Türkçe aksanlı harfler yerine ASCII
# karşılıkları kullanılır (ör. "Şubat" -> "subat", "Ağustos" -> "agustos").
_MONTHS_TR = (
    "ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik"
    # Kısaltmalar (bazı CV/LinkedIn export'larında görülür)
    "|oca|sub|nis|haz|tem|agu|eyl|eki|kas|ara"
)
_MONTHS_EN = (
    "january|february|march|april|may|june|july|august|september|october|november|december"
    # Kısaltmalar (LinkedIn PDF export'larında çok yaygın: "Mar 2021", "Jun 2018")
    "|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
)
_PRESENT_WORDS = "present|current|ongoing|gunumuz|halen|devam ediyor|su an"

DATE_RANGE_PATTERN = re.compile(
    rf"""
    (?:(?:{_MONTHS_TR}|{_MONTHS_EN})\s+\d{{4}}|\b(?:19|20)\d{{2}}\b)
    \s*(?:-|–|—|to|ile)\s*
    (?:(?:{_MONTHS_TR}|{_MONTHS_EN})\s+\d{{4}}|\b(?:19|20)\d{{2}}\b|(?:{_PRESENT_WORDS}))
    """,
    re.VERBOSE,
)

SCHOOL_KEYWORDS = re.compile(
    r"(universite|institute|enstitu|akademi|academy|college|okulu|okul|politeknik)"
)
DEGREE_KEYWORDS = re.compile(
    r"(onlisans|yuksek lisans|lisans|doktora|bachelor|master|mba|phd|b\.sc|m\.sc|associate)"
)


def _split_two(text: str, separators: list[str]) -> tuple[str, str]:
    # `_norm` uzunluk-koruyan (1:1) bir dönüşüm olduğu için `idx` orijinal
    # `text` üzerinde de doğrudan güvenle kullanılabilir; `.lower()` yerine
    # bunun kullanılması Türkçe "İ" gibi harflerde offset kaymasını önler.
    normalized = _norm(text)
    for sep in separators:
        idx = normalized.find(_norm(sep))
        if idx != -1:
            return (
                text[:idx].strip(" ,|-–—.:"),
                text[idx + len(sep) :].strip(" ,|-–—.:"),
            )
    return text.strip(" ,|-–—.:"), ""


_PART_SEPARATOR_PATTERN = re.compile(r"[,;|•]|\bat\b")


def _split_parts(text: str) -> list[str]:
    if not text:
        return []
    normalized = _norm(text)
    parts: list[str] = []
    prev_end = 0
    for match in _PART_SEPARATOR_PATTERN.finditer(normalized):
        parts.append(text[prev_end : match.start()])
        prev_end = match.end()
    parts.append(text[prev_end:])
    return [p.strip(" \t-–—.:") for p in parts if p.strip(" \t-–—.:")]


def _assign_school_degree(candidates: list[str]) -> tuple[str, str]:
    school = ""
    degree = ""
    remaining = list(candidates)
    for line in list(remaining):
        if not school and SCHOOL_KEYWORDS.search(_norm(line)):
            school = line
            remaining.remove(line)
    for line in list(remaining):
        if not degree and DEGREE_KEYWORDS.search(_norm(line)):
            degree = line
            remaining.remove(line)
    if remaining:
        if not school:
            school = remaining.pop(0)
        elif not degree:
            degree = remaining.pop(0)
    return school, degree


def _extract_entries_from_lines(lines: list[str], kind: str) -> list[dict]:
    entries: list[dict] = []
    consumed: set[int] = set()
    for i, line in enumerate(lines):
        if not line:
            continue
        match = DATE_RANGE_PATTERN.search(_norm(line))
        if not match:
            continue
        period = line[match.start() : match.end()].strip()
        remainder = (line[: match.start()] + line[match.end() :]).strip(" \t-–—|,:()")

        if remainder:
            if kind == "experience":
                title, company = _split_two(remainder, [" at ", " - ", " – ", " — ", "|", ","])
                entries.append({"title": title, "company": company, "period": period})
            else:
                school, degree = _assign_school_degree(_split_parts(remainder) or [remainder])
                entries.append({"school": school, "degree": degree, "period": period})
            consumed.add(i)
            continue

        lookback: list[tuple[int, str]] = []
        j = i - 1
        while j >= 0 and len(lookback) < 2:
            if j in consumed:
                j -= 1
                continue
            prev = lines[j]
            if not prev:
                j -= 1
                continue
            if DATE_RANGE_PATTERN.search(_norm(prev)):
                break
            lookback.append((j, prev))
            j -= 1
        lookback.reverse()
        for idx, _ in lookback:
            consumed.add(idx)
        consumed.add(i)
        context = [text for _, text in lookback]

        if kind == "experience":
            title = context[0] if len(context) >= 1 else ""
            company = context[1] if len(context) >= 2 else ""
            entries.append({"title": title, "company": company, "period": period})
        else:
            school, degree = _assign_school_degree(context)
            entries.append({"school": school, "degree": degree, "period": period})
    return entries


def _extract_entries_from_blob(text: str, kind: str) -> list[dict]:
    entries: list[dict] = []
    prev_end = 0
    normalized_text = _norm(text)
    for match in DATE_RANGE_PATTERN.finditer(normalized_text):
        context = text[prev_end : match.start()].strip(" \t\n-–—|,:()")
        if len(context) > 160:
            context = context[-160:]
        period = text[match.start() : match.end()].strip()
        prev_end = match.end()
        parts = _split_parts(context)
        if kind == "experience":
            title = parts[0] if len(parts) >= 1 else ""
            company = parts[1] if len(parts) >= 2 else ""
            entries.append({"title": title, "company": company, "period": period})
        else:
            school, degree = _assign_school_degree(parts) if parts else ("", "")
            entries.append({"school": school, "degree": degree, "period": period})
    return entries


def _extract_section_entries(section_text: str, kind: str) -> list[dict]:
    if not section_text or not section_text.strip():
        return []
    lines = [ln.strip(" \t•*-–—") for ln in section_text.split("\n")]
    non_empty = [ln for ln in lines if ln]
    if len(non_empty) >= 2:
        entries = _extract_entries_from_lines(lines, kind=kind)
        if entries:
            return entries
    return _extract_entries_from_blob(section_text, kind=kind)


def _heuristic_experience(raw_text: str) -> list[dict]:
    section = _locate_section(raw_text, _EXPERIENCE_HEADER_SET)
    return _extract_section_entries(section, kind="experience")


def _heuristic_education(raw_text: str) -> list[dict]:
    section = _locate_section(raw_text, _EDUCATION_HEADER_SET)
    return _extract_section_entries(section, kind="education")


def _heuristic_parsed_skills(raw_text: str) -> dict:
    text = raw_text or ""

    return {
        "languages": _find_matches(text, _LANGUAGE_PATTERNS),
        "frameworks": _find_matches(text, _FRAMEWORK_PATTERNS),
        "tools": _find_matches(text, _TOOL_PATTERNS),
        "experience": _heuristic_experience(text),
        "education": _heuristic_education(text),
    }


def _heuristic_cv_score(parsed_skills: dict, raw_text: str) -> tuple[int, str]:
    skill_count = sum(len(parsed_skills.get(key, [])) for key in ("languages", "frameworks", "tools"))
    experience_count = len(parsed_skills.get("experience", []) or [])
    education_count = len(parsed_skills.get("education", []) or [])
    length_score = min(len(raw_text or "") // 200, 40)
    score = min(100, 25 + skill_count * 4 + experience_count * 6 + education_count * 4 + length_score)
    explanation = (
        f"Tespit edilen {skill_count} teknik beceri, {experience_count} deneyim kaydı ve "
        f"{education_count} eğitim kaydına göre otomatik ön skor hesaplandı. Bu skor, "
        "fine-tune LLM entegrasyonu tamamlandığında daha isabetli hale gelecektir."
    )
    return score, explanation


class CVAgent(BaseAgent):
    name = "cv_agent"
    system_prompt_path = "cv_agent_tr.txt"

    async def analyze(
        self,
        raw_text: str,
        document_type: DocumentType | str,
        github_languages: dict | None = None,
    ) -> dict:
        doc_type_value = document_type.value if hasattr(document_type, "value") else document_type

        prompt = self.load_prompt(raw_text=raw_text[:6000], github_languages=github_languages or {})

        def _fallback() -> dict:
            return {"parsed_skills": _heuristic_parsed_skills(raw_text)}

        parsed, used_fallback = await self.generate_json_with_fallback(
            prompt, fallback_fn=_fallback, max_tokens=1200, temperature=0.3
        )

        if used_fallback:
            parsed_skills = parsed["parsed_skills"]
            if github_languages:
                parsed_skills["languages"] = list(
                    {*parsed_skills["languages"], *github_languages.keys()}
                )
            cv_score = None
            cv_score_explanation = None
            if doc_type_value == DocumentType.CV.value:
                cv_score, cv_score_explanation = _heuristic_cv_score(parsed_skills, raw_text)
        else:
            parsed_skills = parsed.get("parsed_skills", _heuristic_parsed_skills(raw_text))
            cv_score = parsed.get("cv_score")
            cv_score_explanation = parsed.get("cv_score_explanation")
            if doc_type_value != DocumentType.CV.value:
                cv_score = None
                cv_score_explanation = None
            elif not isinstance(cv_score, (int, float)):
                # Model JSON'da parsed_skills'i doğru üretti ama cv_score alanını
                # atladı — LLM'in zaten iyi çıkardığı becerileri heba etmemek için
                # tam heuristik moda düşmek yerine yalnızca eksik skoru,
                # LLM'in ürettiği gerçek parsed_skills üzerinden hesaplıyoruz.
                cv_score, cv_score_explanation = _heuristic_cv_score(parsed_skills, raw_text)

        return {
            "parsed_skills": parsed_skills,
            "cv_score": cv_score,
            "cv_score_explanation": cv_score_explanation,
        }
