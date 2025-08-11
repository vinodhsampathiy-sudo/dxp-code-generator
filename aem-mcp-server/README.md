# AEM MCP Server

A Model Context Protocol (MCP) server for Adobe Experience Manager (AEM) that provides REST API endpoints to build and deploy AEM projects using Maven.

## Features

- **Build Automation**: Trigger Maven builds for AEM projects via REST API
- **Package Deployment**: Deploy AEM packages to author instances
- **Authentication**: Basic authentication for API security
- **Package Management**: List and manage installed packages
- **Docker Support**: Containerized deployment option
- **Extensible**: Easy to add new endpoints and functionality

## Prerequisites

- Node.js 18 or higher
- Java JDK 11 or higher
- Apache Maven 3.6+
- Running AEM Author instance
- Git

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Update environment file with your settings:
# AEM Connection Details
AEM_HOST=http://localhost:4502
AEM_SERVICE_USER=admin
AEM_SERVICE_PASSWORD=admin

# MCP Server Configuration
MCP_USERNAME=mcp-admin
MCP_PASSWORD="Your_password"
PORT=8080

# AEM Project Configuration
AEM_PROJECT_PATH=D:\\AI\\Hackathon\\AEM CODE\\aem-guides-wknd

# Optional: Build Configuration
MAVEN_OPTS=-Xmx2048m
JAVA_HOME=/usr/lib/jvm/java-11-openjdk

### 3. Start the Server

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm run build
npm start
```

## Docker Deployment

```bash
docker-compose up -d
```

## API Details


```bash
curl --location 'http://localhost:8080/api/build-aem-project' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic bWNwLWFkbWluOkFJSGFja2F0aG9uMTIz' \
--data '{
    "projectPath": "D:\\AI\\Hackathon\\AEM CODE\\aem-guides-wknd",
    "mavenProfile": "autoInstallPackage",
    "packagePath": "D:\\AI\\Hackathon\\AEM CODE\\aem-guides-wknd\\all\\target\\your-package.zip",
    "autoInstall": true
  }'
  ```