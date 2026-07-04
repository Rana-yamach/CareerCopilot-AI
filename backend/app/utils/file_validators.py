"""Belge yükleme validasyonu (TASK-106).

İki bağımsız kontrol katmanı uygulanır (biri diğerinin yerine geçmez):
1. `validate_file_extension` — dosya adı uzantısı (kullanıcı deneyimi / hızlı ret).
2. `validate_file_content_type` — gerçek dosya içeriği (magic bytes, `python-magic`
   ile) tespit edilip `ALLOWED_CONTENT_TYPES` ile karşılaştırılır. Yalnızca
   uzantıya bakmak, `.pdf` uzantılı ama içeriği farklı (ör. düz metin, script,
   binary) bir dosyanın kabul edilmesine izin verir; bu kontrol o açığı kapatır.
"""
import magic

from app.config import settings
from app.core.constants import (
    MSG_FILE_CONTENT_MISMATCH,
    MSG_FILE_TOO_LARGE,
    MSG_INVALID_DOCUMENT_TYPE,
    MSG_UNSUPPORTED_FILE_TYPE,
)
from app.core.exceptions import PayloadTooLargeError, UnsupportedMediaTypeError, ValidationError

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_DOCUMENT_TYPES = {"cv", "linkedin_pdf"}

# `.docx` dosyaları teknik olarak bir ZIP arşividir. Bazı `libmagic` veritabanı
# sürümleri iç içeriği (ör. `[Content_Types].xml`) tanımayıp yalnızca
# "application/zip" döndürebilir; bu, geçerli bir .docx'i yanlışlıkla
# reddetmemek için uzantıya özel kabul edilebilir MIME kümesine eklenir.
_EXTENSION_ALLOWED_MIME_TYPES: dict[str, set[str]] = {
    ".pdf": {"application/pdf"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    },
    ".doc": {"application/msword", "application/CDFV2", "application/x-ole-storage"},
}


def validate_document_type(document_type: str) -> None:
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise ValidationError(MSG_INVALID_DOCUMENT_TYPE)


def validate_file_extension(filename: str) -> str:
    lowered = filename.lower()
    ext = next((e for e in ALLOWED_EXTENSIONS if lowered.endswith(e)), None)
    if ext is None:
        raise UnsupportedMediaTypeError(MSG_UNSUPPORTED_FILE_TYPE)
    return ext


def validate_file_size(size_bytes: int) -> None:
    if size_bytes > settings.max_upload_size_bytes:
        raise PayloadTooLargeError(MSG_FILE_TOO_LARGE)


def detect_mime_type(content: bytes) -> str:
    """Dosyanın ilk baytlarından (magic bytes) gerçek MIME tipini tespit eder."""
    return magic.from_buffer(content, mime=True)


def validate_file_content_type(content: bytes, extension: str) -> str:
    """Yüklenen dosyanın gerçek içeriğinin, beyan edilen uzantıyla uyumlu bir
    MIME tipine sahip olduğunu doğrular. Uzantı kontrolüyle birlikte çalışır,
    onun yerine geçmez.
    """
    mime_type = detect_mime_type(content)
    allowed = _EXTENSION_ALLOWED_MIME_TYPES.get(extension, ALLOWED_CONTENT_TYPES)
    if mime_type not in allowed:
        raise UnsupportedMediaTypeError(MSG_FILE_CONTENT_MISMATCH)
    return mime_type
