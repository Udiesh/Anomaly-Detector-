# ── FTRACE Backend ──────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System deps (asyncpg needs libpq, joblib needs gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY main.py consumer.py producer.py websocket_manager.py ./
COPY api/ api/
COPY db/ db/
COPY model/ model/

# No CMD here — overridden per service in docker-compose
