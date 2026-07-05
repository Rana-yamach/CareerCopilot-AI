"""Merkezi uygulama exception sınıfları (ARCHITECTURE.md §9.2).

Tüm hata yanıtları `main.py` içindeki global handler tarafından
`{"error": {"code", "message"}}` şemasına dönüştürülür.
"""
from __future__ import annotations


class AppException(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message_tr: str, code: str | None = None, status_code: int | None = None):
        self.message_tr = message_tr
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message_tr)


class BadRequestError(AppException):
    status_code = 400
    code = "BAD_REQUEST"


class UnauthorizedError(AppException):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppException):
    status_code = 403
    code = "FORBIDDEN"


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppException):
    status_code = 409
    code = "CONFLICT"


class PayloadTooLargeError(AppException):
    status_code = 413
    code = "PAYLOAD_TOO_LARGE"


class UnsupportedMediaTypeError(AppException):
    status_code = 415
    code = "UNSUPPORTED_MEDIA_TYPE"


class ValidationError(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"


class RateLimitError(AppException):
    status_code = 429
    code = "RATE_LIMITED"


class LLMError(AppException):
    status_code = 502
    code = "LLM_ERROR"


class ExternalServiceError(AppException):
    """3. parti servis (ör. GitHub API) çağrısı başarısız olduğunda (502).

    `API_CONTRACT.md` her endpoint için 502'yi kendi bağlamında tanımlar
    (ör. `/github/sync` -> "GitHub API hatası"). Ortak hata kodları
    tablosunda yalnızca LLM_ERROR örneklenmiştir; bu sınıf `code`
    parametresiyle servise özgü bir kod taşımak için kullanılır.
    """

    status_code = 502
    code = "EXTERNAL_SERVICE_ERROR"
