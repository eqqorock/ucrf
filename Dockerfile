# Minimal Dockerfile to pin Python 3.11 for Render
FROM python:3.11.12-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps for common wheels (sqlite, build essentials not needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install --upgrade pip
RUN pip install -r backend/requirements.txt

EXPOSE 8000

# Use Render's $PORT env var; uvicorn expects int but Render will set PORT at runtime.
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
