FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Sistem bağımlılıkları:
# - libpq-dev / gcc: psycopg2 derlemesi için
# - WeasyPrint için: pango, cairo, gdk-pixbuf, libffi, shared-mime-info, fonts
# - libmagic1: python-magic (gerçek dosya içeriği / magic bytes MIME tespiti) için
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    libpq-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    fonts-noto-core \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Bazı geliştirici ağlarında (ör. kurumsal antivirüs TLS taraması) egress HTTPS
# trafiği yerel bir CA ile MITM edilebilir. Böyle bir sertifika varsa
# (docker/extra-ca-certificates/*.crt, git'e commit edilmez) sisteme eklenir;
# yoksa bu adım no-op'tur ve normal ortamları etkilemez.
COPY docker/extra-ca-certificates/ /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
