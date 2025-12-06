# Base image with Python
FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# System dependencies for psycopg2 and security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
 && apt-get install -y --no-install-recommends --only-upgrade util-linux tar \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Upgrade pip to a patched version, then install Python dependencies
RUN python -m pip install --no-cache-dir --upgrade 'pip>=25.0.2' \
 && pip install --no-cache-dir -r requirements.txt

# Copy the remaining code
COPY . .

# Flask default port
EXPOSE 5000

# Start command: production WSGI server (gunicorn)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]