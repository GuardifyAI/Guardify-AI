# Docker Deployment Guide for Guardify-AI

## Overview

This guide provides instructions for deploying Guardify-AI in production using Docker. Two deployment options are available:

1. **Single Container** (Dockerfile) - All services in one container using supervisord
2. **Multi-Container** (Docker Compose) - 4 containers: Redis, Backend, Celery, Frontend [RECOMMENDED]

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+ (for multi-container setup)
- Google Cloud Service Account JSON key
- PostgreSQL database (external)

## Environment Setup

Create a `.env` file in the project root:

```env
# Database Configuration (External PostgreSQL required)
DB_USER=guardify
DB_PASSWORD=your_secure_password
DB_NAME=guardify
DATABASE_URL=postgresql://guardify:your_secure_password@your_postgres_host:5432/guardify

# Redis Configuration (Internal - automatically configured)
REDIS_URL=redis://redis:6379/0

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json

# Provision ISR Configuration (for video recording)
PROVISION_ISR_USERNAME=your_provision_username
PROVISION_ISR_PASSWORD=your_provision_password

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_secret_key_here

# Security
JWT_SECRET_KEY=your_jwt_secret_here
```

## Deployment Option 1: Single Container (All-in-One)

### Build and Run

```bash
# Build the image
docker build -t guardify-ai:latest .

# Run the container
docker run -d \
  --name guardify-ai \
  -p 80:80 \
  -p 8574:8574 \
  -p 5555:5555 \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  guardify-ai:latest
```

### Services Included
- Nginx (port 80) - Frontend
- Flask API (port 8574) - Backend
- Celery Worker - Video analysis
- Celery Flower (port 5555) - Task monitoring
- Video Recorder - Automated recording
- Redis - Message broker

## Deployment Option 2: Multi-Container (Docker Compose) [RECOMMENDED]

### Prerequisites Setup

1. **Setup external PostgreSQL database** (required)

2. **Place Google Cloud credentials:**
   ```bash
   mkdir -p credentials
   cp your-service-account.json credentials/service-account.json
   ```

3. **Create data directories:**
   ```bash
   mkdir -p data logs
   ```

### Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Services Architecture

```
                    ┌─────────────┐
                    │  Database   │
                    │(PostgreSQL) │
                    │ External    │
                    └─────────────┘
                           │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Frontend   │────│   Backend   │────│    Redis    │
│  (Nginx)    │    │   (Flask)   │    │  (Message   │
│   Port 80   │    │  Port 8574  │    │   Broker)   │
└─────────────┘    └─────────────┘    │  Port 6379  │
                           │          └─────────────┘
                           │                   │
                   ┌─────────────┐             │
                   │   Celery    │─────────────┘
                   │   Worker    │
                   │  (Analysis) │
                   └─────────────┘
```

## Service URLs

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8574/app/
- **Redis**: localhost:6379 (internal access only)
- **Health Check**: http://localhost:8574/app/health

## Production Considerations

### Security

1. **Change default passwords** in `.env` file
2. **Use HTTPS** with SSL certificates:
   ```yaml
   # Add to docker-compose.yml frontend service
   ports:
     - "443:443"
   volumes:
     - ./ssl:/etc/nginx/ssl
   ```

3. **Restrict network access** using Docker networks
4. **Run as non-root user** (already configured)

### Scaling

Scale individual services:
```bash
# Scale Celery workers
docker-compose up -d --scale celery-worker=3

# Scale backend instances (with load balancer)
docker-compose up -d --scale backend=2
```

### Monitoring

1. **Service Health Checks**: Built into each container
2. **Flower Dashboard**: Monitor Celery tasks at http://localhost:5555
3. **Container Logs**: `docker-compose logs -f [service_name]`
4. **Resource Usage**: `docker stats`

### Backup Strategy

1. **Database Backup**:
   ```bash
   docker-compose exec db pg_dump -U guardify guardify > backup.sql
   ```

2. **Volume Backup**:
   ```bash
   docker run --rm -v guardify-ai_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
   ```

### Performance Tuning

1. **Database**: Increase PostgreSQL shared_buffers, work_mem
2. **Redis**: Configure maxmemory and maxmemory-policy
3. **Celery**: Adjust worker concurrency and prefetch settings
4. **Nginx**: Enable gzip, set proper cache headers

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Permission issues**: Check file ownership and Docker daemon permissions
3. **Out of memory**: Increase Docker memory limits
4. **Database connection**: Verify DATABASE_URL and container networking

### Debug Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Execute commands in containers
docker-compose exec backend python -c "import sys; print(sys.path)"
docker-compose exec db psql -U guardify -d guardify

# Check network connectivity
docker-compose exec backend ping redis
docker-compose exec backend ping db
```

### Health Checks

```bash
# Backend health
curl http://localhost:8574/app/health

# Frontend health
curl http://localhost/health

# Database health
docker-compose exec db pg_isready -U guardify

# Redis health
docker-compose exec redis redis-cli ping

# Celery worker status
docker-compose exec celery-worker celery -A backend.celery_app status
```

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
docker-compose build --no-cache

# Rolling update (no downtime)
docker-compose up -d --force-recreate --no-deps backend
```

### Log Rotation

Configure log rotation in production:
```bash
# Add to crontab
0 0 * * * docker-compose exec backend find /app/logs -name "*.log" -mtime +7 -delete
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          docker-compose pull
          docker-compose up -d --force-recreate
          docker system prune -f
```

## Support

For issues and support:
1. Check container logs: `docker-compose logs -f`
2. Verify environment variables: `docker-compose config`
3. Test individual services: Use health check endpoints
4. Review resource usage: `docker stats`