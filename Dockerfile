FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (Pillow + xhtml2pdf needs fonts)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libjpeg62-turbo-dev \
      zlib1g-dev \
      libfreetype6-dev \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
      libcairo2 \
      libcairo2-dev \
      pkg-config \
      fonts-dejavu \
      curl \
 && rm -rf /var/lib/apt/lists/*

COPY gestor_pro/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
 && pip install --no-cache-dir gunicorn==22.0.0

COPY gestor_pro /app

# Django defaults
ENV DJANGO_SETTINGS_MODULE=gestor_pro.settings \
    PORT=8000

EXPOSE 8000

# Run migrations + collectstatic on start, then serve
CMD ["/bin/sh", "-lc", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn gestor_pro.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120"]
