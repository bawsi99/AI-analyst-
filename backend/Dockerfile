# Multi-stage build for optimization
FROM python:3.9-slim as builder

# Set environment variables for build stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    wget \
    git \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=""
ENV MPLCONFIGDIR=/tmp/matplotlib

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Database connectivity
    libpq5 \
    # Network utilities
    curl \
    wget \
    # File processing
    libgomp1 \
    # Image processing (for matplotlib/seaborn)
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Excel processing
    libxml2 \
    libxslt1.1 \
    # SSL certificates
    ca-certificates \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/models /app/uploads /app/logs \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app
RUN mkdir -p /tmp/matplotlib && chown -R appuser:appuser /tmp/matplotlib

# Create symlinks for common ML libraries to reduce image size
RUN ln -sf /opt/venv/lib/python3.9/site-packages/sklearn /app/sklearn \
    && ln -sf /opt/venv/lib/python3.9/site-packages/pandas /app/pandas \
    && ln -sf /opt/venv/lib/python3.9/site-packages/numpy /app/numpy

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check with better timeout and retry logic
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Development stage (inherits from production)
FROM production as development

# Switch back to root for development
USER root

# Install additional development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    nano \
    htop \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Switch back to appuser
USER appuser

# Development command with reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Celery worker stage
FROM production as celery

# Switch to root for installing packages
USER root

# Install additional dependencies for Celery
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Switch back to appuser
USER appuser

# Copy Celery configuration
COPY --chown=appuser:appuser celery.conf /etc/supervisor/conf.d/celery.conf

# Create Celery log directory
RUN mkdir -p /app/logs/celery && chown -R appuser:appuser /app/logs

# Health check for Celery
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD celery -A celery inspect ping || exit 1

# Celery worker command
CMD ["celery", "-A", "celery", "worker", "--loglevel=info", "--concurrency=2"]

# Celery beat stage
FROM production as celery-beat

# Health check for Celery Beat
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ps aux | grep "celery.*beat" | grep -v grep || exit 1

# Celery beat command
CMD ["celery", "-A", "celery", "beat", "--loglevel=info"]

# Flower monitoring stage
FROM production as flower

# Switch to root for installing packages
USER root

# Install Flower
RUN pip install flower

# Switch back to appuser
USER appuser

# Expose Flower port
EXPOSE 5555

# Health check for Flower
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5555/ || exit 1

# Flower command
CMD ["celery", "-A", "celery", "flower", "--port=5555", "--broker=redis://redis:6379/0"] 