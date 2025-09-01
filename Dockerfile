# Multi-stage Dockerfile for Guardify-AI Production
# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY UI/Guardify-UI/package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY UI/Guardify-UI/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Python Backend with All Services
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    nginx \
    ffmpeg \
    redis-server \
    postgresql-client \
    git \
    build-essential \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./UI/Guardify-UI/dist

# Set Python path
ENV PYTHONPATH=/app

# Create nginx configuration for serving frontend
RUN mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
COPY <<EOF /etc/nginx/sites-available/default
server {
    listen 80;
    server_name localhost;
    
    # Serve React frontend
    location / {
        root /app/UI/Guardify-UI/dist;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Proxy API requests to Flask backend
    location /app/ {
        proxy_pass http://localhost:8574;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Create supervisord configuration
COPY <<EOF /etc/supervisor/conf.d/guardify.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:redis]
command=redis-server
autorestart=true
stdout_logfile=/var/log/supervisor/redis.log
stderr_logfile=/var/log/supervisor/redis.log

[program:nginx]
command=nginx -g "daemon off;"
autorestart=true
stdout_logfile=/var/log/supervisor/nginx.log
stderr_logfile=/var/log/supervisor/nginx.log

[program:flask-backend]
command=python backend/run.py
directory=/app
autorestart=true
stdout_logfile=/var/log/supervisor/flask.log
stderr_logfile=/var/log/supervisor/flask.log
environment=FLASK_ENV=production,PYTHONPATH=/app

[program:celery-worker]
command=celery -A backend.celery_app worker --loglevel=info --pool=solo --queues=analysis
directory=/app
autorestart=true
stdout_logfile=/var/log/supervisor/celery.log
stderr_logfile=/var/log/supervisor/celery.log
environment=PYTHONPATH=/app

[program:celery-flower]
command=celery -A backend.celery_app flower --port=5555
directory=/app
autorestart=true
stdout_logfile=/var/log/supervisor/flower.log
stderr_logfile=/var/log/supervisor/flower.log
environment=PYTHONPATH=/app

[program:video-recorder]
command=python backend/video/main.py
directory=/app
autorestart=true
stdout_logfile=/var/log/supervisor/video.log
stderr_logfile=/var/log/supervisor/video.log
environment=PYTHONPATH=/app
EOF

# Create log directories
RUN mkdir -p /var/log/supervisor

# Set permissions
RUN chmod +x backend/run.py

# Create a non-root user for security
RUN useradd -r -s /bin/bash guardify && \
    chown -R guardify:guardify /app && \
    chown -R guardify:guardify /var/log/supervisor

# Switch to non-root user for Playwright installation
USER guardify

# Install Playwright browsers as non-root user
RUN playwright install chromium

# Create Playwright cache directory with proper permissions
RUN mkdir -p /home/guardify/.cache/ms-playwright

# Switch back to root for service startup
USER root

# Expose ports
EXPOSE 80 8574 5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/app/health || exit 1

# Start supervisord to manage all services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/guardify.conf"]