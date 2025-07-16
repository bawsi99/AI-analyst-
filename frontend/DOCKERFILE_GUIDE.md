# Frontend Dockerfile Guide

This guide explains the multi-stage Dockerfile for the React frontend application, including security features, optimization strategies, and usage instructions.

## Overview

The frontend Dockerfile uses a multi-stage build approach to create optimized, secure containers for different environments:

- **Production**: Nginx-based serving with security headers and compression
- **Development**: Hot-reload development server
- **Testing**: Isolated testing environment
- **Build-only**: CI/CD optimized build stage

## Build Stages

### Stage 1: Dependencies (`deps`)
```dockerfile
FROM node:18-alpine AS deps
```
- Installs production dependencies only
- Optimizes for smaller image size
- Cleans npm cache for security

### Stage 2: Builder (`builder`)
```dockerfile
FROM node:18-alpine AS builder
```
- Installs all dependencies (including dev dependencies)
- Builds the React application
- Creates optimized production build

### Stage 3: Production (`production`)
```dockerfile
FROM nginx:alpine AS production
```
- Uses Nginx for serving static files
- Includes security headers and compression
- Runs as non-root user for security
- Includes health checks

### Stage 4: Development (`development`)
```dockerfile
FROM node:18-alpine AS development
```
- Full development environment
- Hot-reload capabilities
- Source code mounted as volumes
- Runs as non-root user

### Stage 5: Testing (`testing`)
```dockerfile
FROM node:18-alpine AS testing
```
- Isolated testing environment
- Runs test suites
- No production dependencies

### Stage 6: Build-only (`build-only`)
```dockerfile
FROM node:18-alpine AS build-only
```
- CI/CD optimized
- Builds application without serving
- Outputs build artifacts

## Security Features

### Non-root User
```dockerfile
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001
USER nextjs
```
- Creates dedicated user and group
- Runs application as non-root
- Reduces security attack surface

### Security Headers
The nginx configuration includes comprehensive security headers:
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME type sniffing
- `X-XSS-Protection`: Enables XSS protection
- `Content-Security-Policy`: Restricts resource loading
- `Referrer-Policy`: Controls referrer information

### File Permissions
```dockerfile
COPY --from=builder --chown=nextjs:nodejs /app/build /usr/share/nginx/html
```
- Proper file ownership
- Secure directory permissions
- Prevents unauthorized access

## Performance Optimizations

### Multi-stage Build
- Reduces final image size
- Separates build and runtime dependencies
- Optimizes layer caching

### Nginx Configuration
- Gzip compression for all text-based files
- Static asset caching (1 year for assets)
- No caching for HTML files
- Optimized connection handling

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

## Usage Instructions

### Production Build
```bash
# Build production image
docker build -t ai-analyst-frontend:prod --target production .

# Run production container
docker run -p 3000:3000 ai-analyst-frontend:prod
```

### Development Build
```bash
# Build development image
docker build -t ai-analyst-frontend:dev --target development .

# Run with volume mounting for hot-reload
docker run -p 3000:3000 \
  -v $(pwd):/app \
  -v /app/node_modules \
  ai-analyst-frontend:dev
```

### Testing
```bash
# Build and run tests
docker build -t ai-analyst-frontend:test --target testing .
docker run ai-analyst-frontend:test
```

### Docker Compose
```bash
# Production
FRONTEND_TARGET=production docker-compose up frontend

# Development
FRONTEND_TARGET=development FRONTEND_VOLUMES="./frontend:/app,/app/node_modules" docker-compose up frontend

# Testing
FRONTEND_TARGET=testing docker-compose up frontend
```

## Environment Variables

### Required
- `REACT_APP_API_URL`: Backend API URL
- `NODE_ENV`: Environment (production/development)

### Optional
- `FRONTEND_TARGET`: Docker build target (production/development/testing)
- `FRONTEND_VOLUMES`: Volume mounts for development

## Health Checks

### Production
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1
```

### Development
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1
```

## Nginx Configuration Features

### Static File Serving
- Optimized caching for static assets
- Gzip compression
- Proper MIME type handling

### SPA Routing
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```
- Handles React Router routes
- Falls back to index.html for client-side routing

### API Proxy (Optional)
```nginx
location /api/ {
    proxy_pass http://backend:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## Troubleshooting

### Build Issues
1. **Node modules not found**: Ensure package.json is copied before npm install
2. **Permission errors**: Check file ownership and user creation
3. **Build failures**: Verify all dependencies are in package.json

### Runtime Issues
1. **Port conflicts**: Ensure port 3000 is available
2. **Health check failures**: Check if nginx is running properly
3. **Static file 404s**: Verify build output is copied correctly

### Development Issues
1. **Hot-reload not working**: Check volume mounts
2. **Node modules in container**: Use volume mount for node_modules
3. **Permission issues**: Ensure proper file ownership

## Best Practices

### Security
- Always run as non-root user
- Use security headers
- Keep base images updated
- Scan for vulnerabilities

### Performance
- Use multi-stage builds
- Optimize layer caching
- Compress static assets
- Use appropriate resource limits

### Development
- Use volume mounts for source code
- Separate dev and prod dependencies
- Include health checks
- Provide clear error messages

## Monitoring

### Logs
- Nginx access and error logs
- Application logs
- Health check results

### Metrics
- Response times
- Error rates
- Resource usage
- Build times

## CI/CD Integration

### Build Pipeline
```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker build --target build-only -t frontend-build .
    - docker build --target testing -t frontend-test .
    - docker build --target production -t frontend-prod .
```

### Testing
```yaml
test:
  stage: test
  script:
    - docker run frontend-test npm test
```

### Deployment
```yaml
deploy:
  stage: deploy
  script:
    - docker push frontend-prod
    - kubectl set image deployment/frontend frontend=frontend-prod
```

## Conclusion

This multi-stage Dockerfile provides a robust, secure, and performant solution for deploying React applications. The separation of concerns between build, development, and production stages ensures optimal resource usage and security while maintaining developer productivity. 