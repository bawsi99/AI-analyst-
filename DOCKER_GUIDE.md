# Docker Configuration Guide

This guide explains the Docker setup for the Mini AI Analyst platform and how to use it effectively.

## 🐳 Overview

The application uses Docker Compose to orchestrate multiple services:

### Core Services
- **backend**: FastAPI application with ML capabilities
- **frontend**: React application with TypeScript
- **postgres**: PostgreSQL database for data persistence
- **redis**: Redis for caching and message queuing
- **celery**: Background task worker for ML operations

### Optional Services
- **celery-beat**: Scheduled task scheduler
- **flower**: Celery monitoring dashboard
- **nginx**: Reverse proxy for production deployment

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version
```

### 2. Environment Setup
```bash
# Copy the startup script and make it executable
chmod +x start.sh

# Run the startup script to create .env template
./start.sh help
```

### 3. Configure Environment
Edit the `.env` file with your actual values:
```env
# Required for AI Analysis
GEMINI_LLM_API_KEY=your_actual_gemini_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Optional: Customize database settings
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secure_secret_key
```

### 4. Start the Application
```bash
# Development mode (recommended for first run)
./start.sh dev

# Or with monitoring
./start.sh monitor

# Production mode
./start.sh prod
```

## 📊 Service Details

### Backend Service
- **Port**: 8000
- **Health Check**: `GET /health`
- **API Docs**: `http://localhost:8000/docs`
- **Resources**: 2GB RAM, 1 CPU (limits)

**Key Features:**
- FastAPI with automatic API documentation
- ML pipeline with scikit-learn and XGBoost
- AI analysis with Google Gemini LLM
- Background task integration
- Redis caching
- PostgreSQL database integration

### Frontend Service
- **Port**: 3000
- **Health Check**: Web server availability
- **Resources**: 1GB RAM, 0.5 CPU (limits)

**Key Features:**
- React with TypeScript
- Tailwind CSS for styling
- Real-time task monitoring
- File upload with drag-and-drop
- Interactive data visualization

### PostgreSQL Database
- **Port**: 5432
- **Health Check**: Database connectivity
- **Resources**: 1GB RAM, 0.5 CPU (limits)
- **Persistence**: `postgres_data` volume

**Key Features:**
- Persistent data storage
- User sessions and metadata
- Model information and metrics
- Analysis results and summaries

### Redis Service
- **Port**: 6379
- **Health Check**: Redis ping
- **Resources**: 512MB RAM, 0.25 CPU (limits)
- **Persistence**: `redis_data` volume

**Key Features:**
- Celery message broker
- Application caching
- Rate limiting
- Session storage

### Celery Worker
- **Health Check**: Celery inspect ping
- **Resources**: 2GB RAM, 1 CPU (limits)
- **Concurrency**: 2 workers by default

**Key Features:**
- Background ML model training
- AI analysis generation
- Data profiling tasks
- Batch prediction processing

### Celery Beat (Optional)
- **Purpose**: Scheduled task execution
- **Resources**: 512MB RAM, 0.25 CPU (limits)

**Use Cases:**
- Periodic data cleanup
- Model retraining schedules
- System maintenance tasks

### Flower Monitoring (Optional)
- **Port**: 5555
- **Purpose**: Celery task monitoring
- **Resources**: 256MB RAM, 0.25 CPU (limits)

**Features:**
- Real-time task monitoring
- Worker status tracking
- Task history and statistics
- Web-based dashboard

### Nginx Reverse Proxy (Production)
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Profile**: production
- **Resources**: 256MB RAM, 0.25 CPU (limits)

**Features:**
- Load balancing
- SSL termination
- Rate limiting
- Security headers
- Gzip compression

## 🔧 Configuration Options

### Resource Management
Each service has defined resource limits to prevent resource exhaustion:

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

### Health Checks
All services include health checks for monitoring:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Environment Variables
Key environment variables and their purposes:

| Variable | Purpose | Default |
|----------|---------|---------|
| `GEMINI_LLM_API_KEY` | AI analysis functionality | Required |
| `SUPABASE_URL` | Authentication and database | Required |
| `DATABASE_URL` | Database connection | Auto-generated |
| `REDIS_URL` | Cache and message broker | Auto-generated |
| `SECRET_KEY` | JWT token signing | Generated |
| `MAX_FILE_SIZE` | Upload file size limit | 50MB |

## 🚀 Deployment Scenarios

### Development Mode
```bash
# Start core services only
docker-compose up backend frontend postgres redis celery

# Or use the startup script
./start.sh dev
```

### Testing Mode
```bash
# Start with monitoring for debugging
docker-compose up -d

# Access monitoring dashboard
open http://localhost:5555
```

### Production Mode
```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d

# Scale services for high load
docker-compose up --scale backend=3 --scale celery=5 -d
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale backend API instances
docker-compose up --scale backend=3

# Scale Celery workers
docker-compose up --scale celery=5

# Scale both
docker-compose up --scale backend=2 --scale celery=3
```

### Resource Scaling
Modify resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase for large datasets
      cpus: '2.0' # Increase for ML operations
```

## 🔍 Monitoring and Debugging

### Service Status
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps backend

# Use startup script
./start.sh status
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# With timestamps
docker-compose logs -f --timestamps

# Use startup script
./start.sh logs
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Database health
docker-compose exec postgres pg_isready -U user -d ai_analyst

# Redis health
docker-compose exec redis redis-cli ping
```

### Performance Monitoring
```bash
# Resource usage
docker stats

# Container details
docker-compose exec backend top

# Memory usage
docker-compose exec backend free -h
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using a port
lsof -i :8000

# Stop conflicting services
sudo systemctl stop conflicting-service
```

#### 2. Memory Issues
```bash
# Check available memory
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. Disk Space
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a
docker volume prune
```

#### 4. Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Rebuild without cache
docker-compose build --no-cache

# Remove and recreate
docker-compose down -v
docker-compose up --build
```

### Debugging Commands

#### Database Issues
```bash
# Connect to database
docker-compose exec postgres psql -U user -d ai_analyst

# Check database logs
docker-compose logs postgres
```

#### Redis Issues
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check Redis logs
docker-compose logs redis
```

#### Celery Issues
```bash
# Check Celery status
docker-compose exec celery celery -A app.celery inspect active

# Check Celery logs
docker-compose logs celery
```

## 🔒 Security Considerations

### Production Security
1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY**
3. **Enable SSL** in nginx configuration
4. **Restrict network access** to services
5. **Regular security updates**

### Network Security
```yaml
# Restrict external access
networks:
  ai-analyst-network:
    driver: bridge
    internal: true  # No external access
```

### Volume Security
```yaml
# Use named volumes for persistence
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /secure/path/to/data
```

## 📚 Best Practices

### 1. Environment Management
- Use `.env` files for configuration
- Never commit secrets to version control
- Use different configurations for dev/staging/prod

### 2. Resource Management
- Set appropriate resource limits
- Monitor resource usage
- Scale based on actual needs

### 3. Data Persistence
- Use named volumes for important data
- Regular backups of PostgreSQL data
- Monitor volume usage

### 4. Monitoring
- Enable health checks for all services
- Use Flower for Celery monitoring
- Set up log aggregation

### 5. Updates
- Regular Docker image updates
- Security patches
- Dependency updates

## 🎯 Performance Optimization

### For Large Datasets
```yaml
# Increase memory limits
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
```

### For High Traffic
```yaml
# Scale services
docker-compose up --scale backend=3 --scale celery=5

# Use nginx for load balancing
docker-compose --profile production up
```

### For ML Operations
```yaml
# Increase Celery concurrency
command: celery -A app.celery worker --loglevel=info --concurrency=4

# Add GPU support (if available)
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
```

## 📞 Support

For issues and questions:
1. Check the logs: `./start.sh logs`
2. Verify health checks: `./start.sh status`
3. Review this guide for common solutions
4. Check the main README.md for additional information
5. Monitor the Flower dashboard for task issues 