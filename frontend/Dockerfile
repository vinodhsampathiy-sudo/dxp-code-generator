# Multi-stage build for React frontend
# Stage 1: Build the React application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package*.json ./

    # Install dependencies
    RUN npm install --only=production --silent

    # Copy source code
COPY . .

# Build the application for production
RUN npm run build

# Stage 1b: Development server for live reload (hot reload)
FROM node:18-alpine AS development
WORKDIR /app
COPY package*.json ./
# Install all dependencies (including dev) for React dev server
RUN npm install --silent
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

# Stage 2: Serve the application with nginx
FROM nginx:alpine

# Install wget for health checks
RUN apk add --no-cache wget

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from build stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create directories for nginx runtime files
RUN mkdir -p /var/cache/nginx/client_temp && \
    mkdir -p /var/cache/nginx/proxy_temp && \
    mkdir -p /var/cache/nginx/fastcgi_temp && \
    mkdir -p /var/cache/nginx/uwsgi_temp && \
    mkdir -p /var/cache/nginx/scgi_temp && \
    mkdir -p /var/log/nginx && \
    mkdir -p /var/run && \
    touch /var/run/nginx.pid

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Change ownership of necessary directories including /var/run for nginx.pid
RUN chown -R appuser:appgroup /var/cache/nginx && \
    chown -R appuser:appgroup /var/log/nginx && \
    chown -R appuser:appgroup /usr/share/nginx/html && \
    chown -R appuser:appgroup /etc/nginx/conf.d && \
    chown appuser:appgroup /var/run/nginx.pid

# Make nginx run as non-root user
RUN sed -i 's/user nginx;/user appuser;/' /etc/nginx/nginx.conf

# Switch to non-root user
USER appuser

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Labels for better container management
LABEL maintainer="DXP-GEN-STUDIO"
LABEL description="React Frontend for DXP Component Generator"
LABEL version="1.0"

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
