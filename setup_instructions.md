# DXP-GEN-STUDIO Setup Instructions

## 📋 Prerequisites

Before setting up DXP-GEN-STUDIO, ensure you have the following installed:

- **Node.js** (v18+ recommended) - [Download](https://nodejs.org/)
- **Python** (v3.9+ recommended) - [Download](https://python.org/)
- **Docker & Docker Compose** - [Download](https://docker.com/)
- **Java JDK** (v11+ for AEM) - [Download](https://adoptopenjdk.net/)
- **Apache Maven** (v3.6+) - [Download](https://maven.apache.org/)
- **Git** - [Download](https://git-scm.com/)

## 🚀 Quick Start (Docker Compose)

### 1. Clone and Initialize
```bash
# Clone the repository
git clone <your-repo-url> DXP-GEN-STUDIO
cd DXP-GEN-STUDIO

# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.development.example frontend/.env.development
cp aem-mcp-server/.env.example aem-mcp-server/.env
```

### 2. Configure Environment Variables
Edit the `.env` files with your specific configurations:

**Root `.env`:**
```env
# AEM Instance Configuration
AEM_INSTANCE_URL=http://localhost:4502
AEM_USER=admin
AEM_PASSWORD=admin

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dxp_studio
DB_USER=postgres
DB_PASSWORD=postgres

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Backend `.env`:**
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Frontend `.env.development`:**
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Feature Flags
REACT_APP_ENABLE_DEBUG=true
REACT_APP_ENABLE_PREVIEW=true
```

**AEM MCP Server `.env`:**
```env
# AEM Configuration
AEM_INSTANCE_URL=http://localhost:4502
AEM_USER=admin
AEM_PASSWORD=admin
AEM_PROJECT_ROOT=./aem-project

# MCP Configuration
MCP_PORT=3001
LOG_LEVEL=info
```

### 3. Start All Services
```bash
# Build and start all services
docker-compose up --build

# Or start in detached mode
docker-compose up -d --build
```

### 4. Verify Installation
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **AEM MCP Server**: http://localhost:3001/health
- **AEM Instance**: http://localhost:4502 (if running locally)

---

## 🔧 Manual Setup (Development)

## Backend Service Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Set Up Environment Variables
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configurations
nano .env  # or use your preferred editor
```

### 5. Initialize Database (if using)
```bash
# Run database migrations
alembic upgrade head

# Create initial data (optional)
python scripts/init_db.py
```

### 6. Start Backend Server
```bash
# Development server with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the provided script
python -m app.main
```

### 7. Verify Backend Setup
```bash
# Test API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

---

## ⚛️ Frontend Service Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Node.js Dependencies
```bash
# Install dependencies
npm install

# Or using yarn
yarn install
```

### 3. Set Up Environment Variables
```bash
# Copy environment file
cp .env.development.example .env.development

# Edit environment variables
nano .env.development
```

### 4. Start Development Server
```bash
# Start React development server
npm start

# Or using yarn
yarn start
```

### 5. Build for Production (Optional)
```bash
# Create production build
npm run build

# Serve production build locally
npm install -g serve
serve -s build -l 3000
```

### 6. Verify Frontend Setup
- Open http://localhost:3000 in your browser
- Verify connection to backend API
- Test component generation interface

---

## 🔧 AEM MCP Server Setup

### 1. Navigate to AEM MCP Server Directory
```bash
cd aem-mcp-server
```

### 2. Install Node.js Dependencies
```bash
# Install dependencies
npm install

# Install TypeScript globally (if not already installed)
npm install -g typescript ts-node
```

### 3. Set Up Environment Variables
```bash
# Copy environment file
cp .env.example .env

# Configure AEM connection details
nano .env
```

### 4. Compile TypeScript
```bash
# Compile TypeScript to JavaScript
npm run build

# Or run in development mode with watch
npm run dev
```

### 5. Start MCP Server
```bash
# Start the MCP server
npm start

# Or in development mode
npm run dev
```

### 6. Test MCP Server Connection
```bash
# Test server health
curl http://localhost:3001/health

# Test AEM connectivity
curl http://localhost:3001/aem/status
```

---

## 📁 AEM Project Setup

### 1. Generate AEM Project (If Not Exists)
```bash
# Navigate to project root
cd DXP-GEN-STUDIO

# Generate AEM project using Maven archetype
mvn archetype:generate \
  -DarchetypeGroupId=com.adobe.aem \
  -DarchetypeArtifactId=aem-project-archetype \
  -DarchetypeVersion=35 \
  -DgroupId=com.mycompany.myproject \
  -DartifactId=myproject \
  -Dversion=1.0.0-SNAPSHOT \
  -DpackageName=com.mycompany.myproject \
  -DappTitle="My Project" \
  -DcomponentGroupName="My Project" \
  -DconfFolderName="myproject" \
  -DcontentFolderName="myproject" \
  -DcssId="myproject" \
  -DpackageGroup="my-packages" \
  -DsiteName="myproject" \
  -DoptionAemVersion=6.5.0 \
  -DoptionIncludeExamples=n \
  -DoptionIncludeErrorHandler=n \
  -DoptionFrontendModule=general \
  -DoptionIncludeDispatcherConfig=n

# Rename generated project
mv myproject aem-project
```

### 2. Build AEM Project
```bash
cd aem-project

# Clean and install all modules
mvn clean install

# Deploy to local AEM instance (if running)
mvn clean install -PautoInstallPackage
```

### 3. Verify AEM Project Setup
- Check AEM Package Manager: http://localhost:4502/crx/packmgr
- Verify components in CRXDE: http://localhost:4502/crx/de
- Test component creation through MCP server


## 🐳 Docker Development Setup

### 1. Development with Docker Compose Override
```bash
# Create docker-compose.override.yml for development
cp docker-compose.dev.yml docker-compose.override.yml

# Start development environment
docker-compose up
```

### 2. Individual Service Development
```bash
# Start only backend and database
docker-compose up backend

# Start only frontend
docker-compose up frontend

# Start only MCP server
docker-compose up aem-mcp-server
```

### 3. Debug Mode
```bash
# Enable debug mode for all services
COMPOSE_FILE=docker-compose.yml:docker-compose.debug.yml docker-compose up
```
---

## 🔍 Troubleshooting

### Common Issues

**Backend Won't Start:**
```bash
# Check Python version
python --version

# Verify virtual environment
which python

# Check dependencies
pip list
```

**Frontend Build Fails:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**AEM MCP Server Connection Issues:**
```bash
# Test AEM connectivity
curl -u admin:admin http://localhost:4502/system/console/bundles.json

# Check server logs
tail -f aem-mcp-server/logs/server.log
```

**Docker Issues:**
```bash
# Clean Docker system
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check container logs
docker-compose logs [service-name]
```


