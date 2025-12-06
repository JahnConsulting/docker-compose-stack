# Base image with Python (updated to latest stable minor for security fixes)
FROM python:3.14-slim

# Working directory inside the container
WORKDIR /app

# System dependencies for psycopg2 and security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
 && apt-get install -y --no-install-recommends --only-upgrade util-linux tar \
 && rm -rf /var/lib/apt/lists/*

# Create an unprivileged user and group to run the app
# Use a fixed UID/GID to avoid permission drift with mounted volumes
RUN groupadd -g 10001 app && \
    useradd -r -u 10001 -g app app

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Upgrade pip to a patched version, then install Python dependencies
RUN python -m pip install --no-cache-dir --upgrade 'pip>=25.0.2' \
 && pip install --no-cache-dir -r requirements.txt

# Copy the remaining code
COPY . .

# Ensure the application directory is owned by the unprivileged user
RUN chown -R app:app /app

# Switch to the non-root user for runtime
USER app:app

# Flask default port
EXPOSE 5000

# Start command: production WSGI server (gunicorn)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]