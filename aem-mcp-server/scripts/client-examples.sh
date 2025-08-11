#!/bin/bash

# AEM MCP Server - Client Examples

# Configuration
MCP_HOST="http://localhost:8080"
MCP_USER="mcp-admin"
MCP_PASS="your-secure-password-here"

# Health Check
echo "Health Check:"
curl -s "$MCP_HOST/api/health" | jq .

# Build AEM Project
echo -e "\nBuild AEM Project:"
curl -s -u "$MCP_USER:$MCP_PASS" \
  -X POST "$MCP_HOST/api/build-aem-project" \
  -H "Content-Type: application/json" \
  -d '{
    "projectPath": "/path/to/aem/project",
    "mavenProfile": "autoInstallPackage"
  }' | jq .

# Deploy Package
echo -e "\nDeploy Package:"
curl -s -u "$MCP_USER:$MCP_PASS" \
  -X POST "$MCP_HOST/api/deploy-package" \
  -H "Content-Type: application/json" \
  -d '{
    "packagePath": "/path/to/package.zip",
    "packageName": "my-package.zip",
    "force": true
  }' | jq .
