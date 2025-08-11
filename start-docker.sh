#!/bin/bash

# DXP-GEN-STUDIO Docker Startup Script

echo "🚀 Starting DXP-GEN-STUDIO Docker Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.docker template..."
    cp .env.docker .env
    echo "⚠️  Please update .env file with your actual API keys and configuration!"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - AEM configuration (if needed)"
    echo ""
    read -p "Press Enter after updating .env file to continue..."
fi

# Create output directory if it doesn't exist
mkdir -p output

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🔨 Building and starting all services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ DXP-GEN-STUDIO is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   - Frontend:        http://localhost:3000"
echo "   - Backend API:     http://localhost:5000"
echo "   - AEM MCP Server:  http://localhost:8080"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f [service-name]"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart a service:"
echo "   docker-compose restart [service-name]"
