# Frontend Docker Deployment Guide

## Overview

This guide covers deploying the React frontend as a standalone Docker container. The container serves the built React application using nginx.

## Files Created

### Docker Configuration
- **`Dockerfile`** - Multi-stage build for optimized production container
- **`docker-compose.yml`** - Container orchestration for frontend deployment
- **`nginx.conf`** - nginx configuration with SPA routing support
- **`nginx-frontend-only.conf`** - Simplified nginx config without API proxy

### Control Scripts
- **`frontend-control.bat`** - Windows batch script for container management
- **`frontend-control.sh`** - Linux/Mac shell script for container management

### Environment Files
- **`.env.docker`** - Docker-specific environment variables
- **`.env.production`** - Production environment template

## Quick Start

### Using Control Scripts (Recommended)

**Windows:**
```cmd
cd frontend
.\frontend-control.bat
```

**Linux/Mac:**
```bash
cd frontend
chmod +x frontend-control.sh
./frontend-control.sh
```

### Direct Docker Commands

**Build the container:**
```bash
cd frontend
docker-compose build
```

**Start the container:**
```bash
docker-compose up -d
```

**Stop the container:**
```bash
docker-compose down
```

## Container Details

### Build Process
1. **Stage 1 (Builder)**: 
   - Uses Node.js 18 Alpine
   - Installs dependencies with `npm ci`
   - Builds the React application for production
   
2. **Stage 2 (Runtime)**:
   - Uses nginx Alpine for serving static files
   - Copies built application from builder stage
   - Runs as non-root user for security
   - Includes health checks

### Security Features
- ✅ Runs as non-root user (`appuser`)
- ✅ Minimal Alpine Linux base image
- ✅ Security headers (XSS, CSRF, etc.)
- ✅ Denies access to sensitive files
- ✅ Health checks for container monitoring

### Performance Optimizations
- ✅ Multi-stage build reduces final image size
- ✅ Gzip compression enabled
- ✅ Static asset caching (1 year)
- ✅ HTML caching (1 hour)
- ✅ Docker layer caching optimization

## Port Configuration

- **Container Port**: 80
- **Host Port**: 3000 (configurable in docker-compose.yml)
- **Access URL**: http://localhost:3000

## API Configuration

The frontend container is configured to work with external API services:

### Environment Variables
Set these in `.env.docker` or override in docker-compose.yml:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_AEM_BUILDER_URL=http://localhost:8080
```

### Runtime Configuration
- Use the config panel in the frontend (Ctrl+Shift+C)
- Update API URLs to point to your backend services
- Settings are persisted in browser localStorage

## Deployment Scenarios

### 1. Standalone Frontend (Recommended)
Deploy frontend container independently and configure it to connect to external backend services.

```bash
# Start frontend container
docker-compose up -d

# Configure API URLs via:
# - Environment variables
# - Config panel (Ctrl+Shift+C)
# - localStorage override
```

### 2. With Existing Backend
Deploy frontend alongside your existing backend services.

```yaml
# Example docker-compose.yml integration
version: '3.8'
services:
  backend:
    # Your existing backend service
    image: your-backend:latest
    ports:
      - "8000:5000"
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000
```

### 3. Production Deployment
For production deployment with custom domains:

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_BASE_URL=https://api.yourdomain.com
      - REACT_APP_AEM_BUILDER_URL=https://builder.yourdomain.com
```

## Control Script Features

Both Windows (.bat) and Linux/Mac (.sh) scripts provide:

1. **Build Frontend Container** - Build the Docker image
2. **Start Frontend Container** - Run the container in detached mode
3. **Stop Frontend Container** - Stop and remove the container
4. **Restart Frontend Container** - Restart the running container
5. **View Container Status** - Show container health and status
6. **View Container Logs** - Follow container logs in real-time
7. **Clean Build (No Cache)** - Build without using Docker cache
8. **Remove Container and Images** - Complete cleanup

## nginx Configuration

### Default Configuration (nginx.conf)
- Includes API proxy configuration (for integrated deployments)
- CORS headers for external API calls
- Security headers and optimizations

### Frontend-Only Configuration (nginx-frontend-only.conf)
- Simplified configuration without API proxy
- Optimized for standalone frontend deployment
- Enhanced security and caching

To use the simplified configuration:
```dockerfile
# In Dockerfile, replace:
COPY nginx.conf /etc/nginx/conf.d/default.conf
# With:
COPY nginx-frontend-only.conf /etc/nginx/conf.d/default.conf
```

## Health Checks

The container includes health checks:
- **Check**: HTTP GET to `http://localhost:80/`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 5 seconds

## Troubleshooting

### Build Issues
```bash
# Clean build without cache
docker-compose build --no-cache

# Check Docker daemon
docker info

# View build logs
docker-compose build --progress=plain
```

### Runtime Issues
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs -f frontend

# Check health status
docker inspect --format='{{.State.Health.Status}}' dxp-frontend
```

### Common Problems

**1. Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "3001:80"  # Use different host port
```

**2. API connection issues:**
- Check API URLs in config panel (Ctrl+Shift+C)
- Verify backend services are accessible
- Check browser developer console for CORS errors

**3. Container fails to start:**
```bash
# Check container logs
docker-compose logs frontend

# Verify Docker resources
docker system df
```

## Image Size Optimization

The multi-stage build results in a small, optimized image:
- **Builder stage**: ~1.2GB (discarded)
- **Final image**: ~50-80MB
- **Compressed**: ~25-40MB

## Best Practices

✅ **Use specific tags** for base images  
✅ **Run as non-root** user for security  
✅ **Include health checks** for monitoring  
✅ **Use .dockerignore** to exclude unnecessary files  
✅ **Leverage build cache** for faster builds  
✅ **Set resource limits** in production  
✅ **Monitor container metrics** and logs  

## Next Steps

1. **Build and test** the frontend container locally
2. **Configure API URLs** for your environment
3. **Deploy to staging** for integration testing
4. **Set up monitoring** and logging
5. **Deploy to production** with proper CI/CD pipeline
