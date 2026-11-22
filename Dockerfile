# ==========================================
# Stage 1: Build React + Vite Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Backend & Unified App
# ==========================================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

# Install system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
COPY bot/requirements.txt ./bot/requirements.txt
RUN pip install --no-cache-dir \
    -r ./backend/requirements.txt \
    -r ./bot/requirements.txt

# Copy application files
COPY backend ./backend
COPY bot ./bot
COPY scripts ./scripts

# Copy built frontend assets from Stage 1 into backend static
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000

# Run the website and, when configured, the Telegram bot.
CMD ["python", "scripts/run_deployment.py"]
