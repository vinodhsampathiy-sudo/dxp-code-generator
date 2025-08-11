# Backend and MongoDB Docker Setup

This directory contains a self-contained Docker Compose setup for running just the Backend application and MongoDB database.

## Files Created

### 1. docker-compose.yml
- Defines MongoDB and Backend services
- Includes health checks and proper networking
- Configured with volume mounts for data persistence

### 2. backend-control.bat (Windows)
Interactive control script with menu options:
- Start Backend and MongoDB
- Stop Backend and MongoDB
- Restart Backend and MongoDB
- View Container Status
- View Backend Logs
- View MongoDB Logs

### 3. backend-control.sh (Linux/macOS)
Same functionality as the batch file but for Unix-based systems.

## Quick Start

### Windows:
```powershell
cd backend
.\backend-control.bat
```

### Linux/macOS:
```bash
cd backend
chmod +x backend-control.sh
./backend-control.sh
```

### Manual Commands:
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f mongodb
```

## Access Points

- **Backend API**: http://localhost:8000
- **MongoDB**: localhost:27017
  - Username: admin
  - Password: password123
  - Database: dxp_gen_studio

## Features

- **Health Checks**: MongoDB has built-in health monitoring
- **Auto-restart**: Containers restart automatically unless stopped
- **Data Persistence**: MongoDB data is stored in a named volume
- **Dependency Management**: Backend waits for MongoDB to be healthy before starting
- **Volume Mounts**: Backend code is mounted for development

## Container Names

- MongoDB: `backend-mongodb`
- Backend: `backend-app`
- Network: `backend_backend-network`
- Volume: `backend_mongodb_data`

## Troubleshooting

If containers fail to start:
1. Check if ports 8000 and 27017 are available
2. Ensure Docker is running
3. Check logs using the control script option 5 or 6
4. Try restarting with option 3 in the control script
