# Basis-Image mit Python
FROM python:3.12-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Abhängigkeiten für psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Requirements zuerst kopieren (bessere Layer-Caches)
COPY requirements.txt .

# Python-Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Restlichen Code kopieren
COPY . .

# Flask-Standardport
EXPOSE 5000

# Startbefehl: Production WSGI Server (gunicorn)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]