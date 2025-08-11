# DXP-GEN-STUDIO Docker Setup Guide

This guide provides step-by-step instructions for setting up and managing the DXP Component Generator Studio using Docker containers.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Git** installed
- **Windows PowerShell** or **Command Prompt** (Windows)
- **Terminal** (Linux/Mac)

## 🏗️ Architecture Overview

The application consists of two main containers:

- **Backend Container** (`backend-app`): FastAPI + MongoDB on port `8000`
- **Frontend Container** (`dxp-frontend`): React + nginx on port `3000`

## 🚀 First-Time Setup

### 1. Clone and Navigate to Project
```bash
git clone https://github.com/Vinodh-Projects/DXP-GEN-STUDIO.git
cd DXP-GEN-STUDIO
```

### 2. Backend Setup (FastAPI + MongoDB)

#### Option A: Using Control Scripts (Recommended)
```bash
# Windows
cd backend
.\backend-control.bat

# Linux/Mac
cd backend
./backend-control.sh
```

#### Option B: Using Docker Compose Directly
```bash
cd backend
docker-compose up -d --build
```

**Backend Services:**
- 🗄️ **MongoDB**: `localhost:27017`
- 🔧 **FastAPI Backend**: `localhost:8000`
- 📚 **API Documentation**: `http://localhost:8000/docs`

### 3. Frontend Setup (React + nginx)

#### Option A: Using Control Scripts (Recommended)
```bash
# Windows
cd frontend
.\frontend-control.bat

# Linux/Mac
cd frontend
./frontend-control.sh
```

#### Option B: Using Docker Compose Directly
```bash
cd frontend
docker-compose up -d --build
```

**Frontend Service:**
- 🌐 **React Application**: `http://localhost:3000`

### 4. Verify Installation

Check that all containers are running:
```bash
# Check backend containers
cd backend
docker-compose ps

# Check frontend container
cd frontend
docker-compose ps
```

**Expected Output:**
```
Backend:
- backend-mongodb: Up (healthy)
- backend-app: Up (healthy)

Frontend:
- dxp-frontend: Up (healthy)
```

## 🔄 Daily Operations

### Starting Services

#### Start Backend Services
```bash
cd backend
docker-compose up -d
```

#### Start Frontend Service
```bash
cd frontend
docker-compose up -d
```

#### Start All Services (Alternative)
```bash
# Using control scripts for interactive management
# Windows
cd backend && .\backend-control.bat
cd frontend && .\frontend-control.bat

# Linux/Mac
cd backend && ./backend-control.sh
cd frontend && ./frontend-control.sh
```

### Stopping Services

#### Stop Backend Services
```bash
cd backend
docker-compose down
```

#### Stop Frontend Service
```bash
cd frontend
docker-compose down
```

#### Stop All Services
```bash
# Stop all Docker containers
docker stop $(docker ps -q)
```

### Restarting Services

#### Restart Backend
```bash
cd backend
docker-compose restart
```

#### Restart Frontend
```bash
cd frontend
docker-compose restart
```

#### Full Restart (Backend + Frontend)
```bash
cd backend
docker-compose down
docker-compose up -d

cd frontend
docker-compose down
docker-compose up -d
```

## 🛠️ Troubleshooting

### Check Container Status
```bash
# View all running containers
docker ps

# View container logs
docker-compose logs <service-name>

# Examples:
cd backend && docker-compose logs backend
cd backend && docker-compose logs mongodb
cd frontend && docker-compose logs frontend
```

### Rebuild Containers (When Code Changes)
```bash
# Rebuild backend
cd backend
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Rebuild frontend
cd frontend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Reset Everything (Nuclear Option)
```bash
# Stop all containers
docker-compose down

# Remove all containers, networks, and images
docker system prune -f

# Rebuild from scratch
cd backend && docker-compose up -d --build
cd frontend && docker-compose up -d --build
```

### Common Issues & Solutions

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :27017

# Kill the process or change ports in docker-compose.yml
```

#### 2. Container Won't Start
```bash
# Check detailed logs
docker-compose logs --tail 50 <service-name>

# Rebuild container
docker-compose build --no-cache <service-name>
```

#### 3. Database Connection Issues
```bash
# Reset MongoDB data
cd backend
docker-compose down
docker volume rm backend_mongodb_data
docker-compose up -d
```

## 📊 Service Status Check

### Quick Health Check
```bash
# Backend API
curl http://localhost:8000/docs

# Frontend
curl http://localhost:3000

# MongoDB (requires mongosh)
mongosh "mongodb://admin:password123@localhost:27017/dxp_gen_studio?authSource=admin"
```

### Container Resource Usage
```bash
# View resource usage
docker stats

# View container details
docker inspect backend-app
docker inspect dxp-frontend
docker inspect backend-mongodb
```

## 🔧 Configuration

### Environment Variables

#### Backend Configuration
Located in `backend/.env`:
```bash
MONGODB_URI=mongodb://admin:password123@mongodb:27017/dxp_gen_studio?authSource=admin
PYTHONUNBUFFERED=1
```

#### Frontend Configuration
Located in `frontend/.env.production`:
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_AEM_BUILDER_URL=http://localhost:8080
```

### Volume Mappings

#### Backend Volumes
- `./backend:/app` - Live code updates
- `../output:/app/output` - Generated output files
- `../project_code:/app/project_code` - AEM project files
- `mongodb_data:/data/db` - Database persistence

#### Frontend Volumes
- Built files served via nginx (no live updates in container)

## 📱 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main React Application |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Interactive API Documentation |
| MongoDB | localhost:27017 | Database (admin/password123) |

## 🎯 Quick Commands Reference

```bash
# First time setup
cd backend && docker-compose up -d --build
cd frontend && docker-compose up -d --build

# Daily start
cd backend && docker-compose up -d
cd frontend && docker-compose up -d

# Daily stop
cd backend && docker-compose down
cd frontend && docker-compose down

# View logs
cd backend && docker-compose logs --tail 20
cd frontend && docker-compose logs --tail 20

# Rebuild after changes
cd backend && docker-compose build --no-cache && docker-compose up -d
cd frontend && docker-compose build --no-cache && docker-compose up -d
```

## 🆘 Support

For issues or questions:
1. Check the logs: `docker-compose logs <service>`
2. Verify containers are running: `docker-compose ps`
3. Check the troubleshooting section above
4. Rebuild containers if needed: `docker-compose build --no-cache`

---

**Happy Coding! 🚀**
