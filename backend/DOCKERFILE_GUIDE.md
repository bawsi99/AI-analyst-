# Backend Dockerfile Guide

This guide explains the updated multi-stage Dockerfile for the Mini AI Analyst backend and how to use it effectively.

## 🏗️ Multi-Stage Build Architecture

The Dockerfile uses a multi-stage build approach to optimize image size and security:

### Build Stage (`builder`)
- **Purpose**: Compile and install Python dependencies
- **Base Image**: `python:3.9-slim`
- **Dependencies**: Build tools, development libraries
- **Output**: Virtual environment with all Python packages

### Production Stage (`production`)
- **Purpose**: Runtime environment for the FastAPI application
- **Base Image**: `python:3.9-slim`
- **Security**: Non-root user, minimal system packages
- **Optimizations**: Symlinks for common ML libraries

### Development Stage (`development`)
- **Purpose**: Development environment with debugging tools
- **Inherits**: From production stage
- **Additions**: Development tools (vim, nano, htop)
- **Command**: Uvicorn with auto-reload

### Celery Stages
- **`celery`**: Worker processes for background tasks
- **`celery-beat`**: Scheduled task scheduler
- **`flower`**: Monitoring dashboard for Celery

## 🚀 Build Targets

### Production Target
```bash
# Build production image
docker build -t ai-analyst-backend:prod --target production .

# Run production container
docker run -p 8000:8000 ai-analyst-backend:prod
```

### Development Target
```bash
# Build development image
docker build -t ai-analyst-backend:dev --target development .

# Run development container with auto-reload
docker run -p 8000:8000 -v $(pwd):/app ai-analyst-backend:dev
```

### Celery Worker Target
```bash
# Build Celery worker image
docker build -t ai-analyst-celery --target celery .

# Run Celery worker
docker run ai-analyst-celery
```

### Celery Beat Target
```bash
# Build Celery beat image
docker build -t ai-analyst-celery-beat --target celery-beat .

# Run Celery beat
docker run ai-analyst-celery-beat
```

### Flower Monitoring Target
```bash
# Build Flower image
docker build -t ai-analyst-flower --target flower .

# Run Flower monitoring
docker run -p 5555:5555 ai-analyst-flower
```

## 🔧 Key Features

### Security Enhancements
1. **Non-root User**: Application runs as `appuser` instead of root
2. **Minimal Base Image**: Uses `python:3.9-slim` for smaller attack surface
3. **Proper Permissions**: Files and directories have appropriate ownership
4. **Cleanup**: Removes unnecessary files and packages

### Performance Optimizations
1. **Multi-stage Build**: Reduces final image size by excluding build tools
2. **Virtual Environment**: Isolated Python environment
3. **Symlinks**: Reduces image size for common ML libraries
4. **Layer Caching**: Optimized layer ordering for faster rebuilds

### System Dependencies
The Dockerfile includes all necessary system dependencies:

#### Build Dependencies
- `build-essential`: C compiler and build tools
- `libpq-dev`: PostgreSQL development libraries
- `curl`, `wget`: Network utilities
- `git`, `pkg-config`: Development tools

#### Runtime Dependencies
- `libpq5`: PostgreSQL runtime libraries
- `libgomp1`: OpenMP runtime for parallel processing
- `libgl1-mesa-glx`, `libglib2.0-0`, `libsm6`, `libxext6`: Graphics libraries for matplotlib/seaborn
- `libxml2`, `libxslt1.1`: XML processing for Excel files
- `ca-certificates`: SSL certificates for HTTPS requests

### Health Checks
Each target includes appropriate health checks:

```dockerfile
# FastAPI health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Celery health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD celery -A app.celery inspect ping || exit 1

# Flower health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5555/ || exit 1
```

## 📦 Image Optimization

### Size Reduction Techniques
1. **Multi-stage Build**: Excludes build tools from final image
2. **Virtual Environment**: Only necessary Python packages
3. **Symlinks**: Reduces duplication of large ML libraries
4. **Cleanup**: Removes package lists and temporary files
5. **Minimal Base**: Uses slim Python image

### Layer Optimization
```dockerfile
# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements before application code
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code last (changes most frequently)
COPY . .
```

## 🔍 Debugging and Development

### Development Mode
```bash
# Build development image
docker build --target development -t ai-analyst-dev .

# Run with volume mount for live code changes
docker run -p 8000:8000 \
  -v $(pwd):/app \
  -v $(pwd)/logs:/app/logs \
  ai-analyst-dev
```

### Debugging Commands
```bash
# Access container shell
docker exec -it <container_id> /bin/bash

# View logs
docker logs <container_id>

# Check health status
docker inspect <container_id> | grep Health -A 10

# Monitor resource usage
docker stats <container_id>
```

### Common Issues and Solutions

#### 1. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run container with proper user mapping
docker run -u $(id -u):$(id -g) -v $(pwd):/app ai-analyst-dev
```

#### 2. Memory Issues
```bash
# Increase memory limit
docker run --memory=4g ai-analyst-backend:prod

# Monitor memory usage
docker stats
```

#### 3. Port Conflicts
```bash
# Use different port
docker run -p 8001:8000 ai-analyst-backend:prod

# Check what's using the port
lsof -i :8000
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Set required environment variables
docker run -e GEMINI_LLM_API_KEY=your_key \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_ANON_KEY=your_key \
  -e SUPABASE_SERVICE_ROLE_KEY=your_key \
  ai-analyst-backend:prod
```

### Volume Mounts
```bash
# Persistent storage for models and uploads
docker run -v /path/to/models:/app/models \
  -v /path/to/uploads:/app/uploads \
  -v /path/to/logs:/app/logs \
  ai-analyst-backend:prod
```

### Resource Limits
```bash
# Set resource limits
docker run --memory=2g --cpus=1.0 \
  --memory-swap=4g \
  ai-analyst-backend:prod
```

## 🔧 Customization

### Adding New Dependencies
1. **Python Packages**: Add to `requirements.txt`
2. **System Packages**: Add to appropriate `RUN` command
3. **Rebuild**: `docker build --target production .`

### Custom Commands
```dockerfile
# Override default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Or use shell form for complex commands
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level debug
```

### Environment-Specific Builds
```bash
# Development build
docker build --target development --build-arg ENV=dev .

# Production build
docker build --target production --build-arg ENV=prod .
```

## 📊 Performance Monitoring

### Health Check Endpoints
- **FastAPI**: `GET /health`
- **Celery**: `celery -A app.celery inspect ping`
- **Flower**: `GET /` (Flower dashboard)

### Logging
```bash
# View application logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>

# View logs with timestamps
docker logs -t <container_id>
```

### Resource Monitoring
```bash
# Container stats
docker stats

# Detailed resource usage
docker exec <container_id> top

# Memory usage
docker exec <container_id> free -h
```

## 🔒 Security Best Practices

### Image Security
1. **Non-root User**: Application runs as `appuser`
2. **Minimal Base**: Uses slim image with fewer vulnerabilities
3. **Regular Updates**: Keep base images updated
4. **Security Scanning**: Use tools like Trivy or Snyk

### Runtime Security
1. **Environment Variables**: Use secrets management
2. **Network Security**: Restrict container networking
3. **Resource Limits**: Prevent resource exhaustion attacks
4. **Health Checks**: Monitor application health

### Secrets Management
```bash
# Use Docker secrets
echo "your_secret" | docker secret create my_secret -

# Or use environment files
docker run --env-file .env ai-analyst-backend:prod
```

## 📚 Best Practices

### 1. Build Optimization
- Use multi-stage builds
- Optimize layer ordering
- Minimize image size
- Use appropriate base images

### 2. Security
- Run as non-root user
- Use minimal base images
- Regular security updates
- Proper file permissions

### 3. Monitoring
- Implement health checks
- Use proper logging
- Monitor resource usage
- Set up alerts

### 4. Development
- Use development target for local development
- Mount volumes for live code changes
- Use appropriate debugging tools
- Test in production-like environment

## 🆘 Troubleshooting

### Build Issues
```bash
# Clean build without cache
docker build --no-cache --target production .

# Build with verbose output
docker build --progress=plain --target production .

# Check build context
docker build --target production . 2>&1 | grep "sending build context"
```

### Runtime Issues
```bash
# Check container logs
docker logs <container_id>

# Access container shell
docker exec -it <container_id> /bin/bash

# Check health status
docker inspect <container_id> | grep Health -A 10

# Restart container
docker restart <container_id>
```

### Performance Issues
```bash
# Monitor resource usage
docker stats <container_id>

# Check memory usage
docker exec <container_id> free -h

# Check disk usage
docker exec <container_id> df -h
```

For additional support, refer to the main README.md and DOCKER_GUIDE.md files. 