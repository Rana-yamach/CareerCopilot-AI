"""Basit rate limiting (TASK-302): login endpoint dakikada 10 istek ile sınırlı.

slowapi (Flask-Limiter'ın FastAPI portu) kullanılır; limiter Redis olmadan
in-memory sayaç ile de çalışır (tek instance geliştirme/demo ortamı için yeterli).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
