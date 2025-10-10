### Multi-stage Dockerfile: build frontend with Node, copy into Python image

# Stage 1: build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --silent || npm install --silent
COPY frontend/ .
RUN npm run build

# Stage 2: runtime image
FROM python:3.11.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code and frontend build
COPY backend/ ./backend
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

RUN python -m pip install --upgrade pip
RUN pip install -r backend/requirements.txt

EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
