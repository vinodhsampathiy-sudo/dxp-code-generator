#!/bin/bash

# Docker Health Check Script for DXP-GEN-STUDIO

echo "🏥 DXP-GEN-STUDIO Health Check"
echo "=============================="

# Check if docker-compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ No services are running"
    exit 1
fi

# Check each service
services=("backend" "frontend" "aem-mcp-server")

for service in "${services[@]}"; do
    echo "Checking $service..."
    
    health=$(docker-compose ps | grep $service | awk '{print $5}')
    
    if [[ $health == *"healthy"* ]]; then
        echo "✅ $service is healthy"
    elif [[ $health == *"starting"* ]]; then
        echo "🔄 $service is starting..."
    else
        echo "❌ $service is unhealthy"
        echo "Logs for $service:"
        docker-compose logs --tail=10 $service
    fi
done

echo ""
echo "📊 Service URLs:"
echo "   - Frontend:        http://localhost:3000"
echo "   - Backend API:     http://localhost:5000"
echo "   - AEM MCP Server:  http://localhost:8080"
