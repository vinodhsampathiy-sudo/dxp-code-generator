# Frontend API Configuration Guide

## Overview

The frontend has been updated to use configurable API URLs instead of hardcoded localhost:5000. This allows you to easily switch between different backend configurations.

## API Port Configuration

### Docker Backend (Recommended)
- **Port**: 8000
- **URL**: http://localhost:8000
- **Usage**: When using the Docker setup in the `backend/` folder

### Direct Python Backend  
- **Port**: 5000
- **URL**: http://localhost:5000
- **Usage**: When running the Python backend directly (without Docker)

## Configuration Methods

### 1. Environment Variables (Recommended)

Create or modify these files in the `frontend/` directory:

**`.env.development`** (Default for npm start):
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_AEM_BUILDER_URL=http://localhost:8080
```

**`.env.local`** (For local Python backend):
```env
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_AEM_BUILDER_URL=http://localhost:8080
```

**`.env.production`** (For production deployment):
```env
REACT_APP_API_BASE_URL=https://your-production-domain.com
REACT_APP_AEM_BUILDER_URL=https://your-aem-builder-domain.com
```

### 2. Runtime Configuration Panel

Press `Ctrl+Shift+C` in the frontend application to open the configuration panel:

- **View current configuration**: See active API URLs
- **Change API base URL**: Enter new URL and click "Update URL"  
- **Reset to default**: Restore environment variable settings
- **Persistent**: Settings saved in localStorage

### 3. Browser localStorage Override

You can also set the API URL programmatically:

```javascript
// Override API base URL
localStorage.setItem('API_BASE_URL', 'http://localhost:5000');

// Remove override (use environment variables)
localStorage.removeItem('API_BASE_URL');

// Reload to apply changes
window.location.reload();
```

## Usage Examples

### Starting with Docker Backend (Port 8000)

1. Start Docker backend:
   ```bash
   cd backend
   ./backend-control.bat  # Windows
   # OR
   ./backend-control.sh   # Linux/Mac
   ```

2. Start frontend (will use port 8000 by default):
   ```bash
   cd frontend
   npm start
   ```

### Starting with Direct Python Backend (Port 5000)

1. Start Python backend directly:
   ```bash
   cd backend
   python run.py
   ```

2. Use local environment:
   ```bash
   cd frontend
   cp .env.local .env
   npm start
   ```

   OR use the config panel (`Ctrl+Shift+C`) and set URL to `http://localhost:5000`

## Files Updated

### Components Updated:
- `DXPComponentGenerator.js` - Main component generator
- `PromptInputPanel.js` - Quick component generation
- `ProjectGeneratorPage.js` - AEM project generator  
- `EDSBlockGeneratorPage.js` - EDS block generator
- `App.js` - Added ConfigPanel component

### New Files:
- `config/apiConfig.js` - Central API configuration
- `components/ConfigPanel.js` - Runtime configuration UI
- `.env` files - Environment-specific settings

## API Endpoints Configured

All endpoints now use the configurable base URL:

- **Component Generation**: `{baseUrl}/api/component/generate`
- **AEM Component**: `{baseUrl}/api/component`  
- **EDS Block Generation**: `{baseUrl}/api/component/generate-eds-block`
- **Project Generation**: `{baseUrl}/api/projects/generate`
- **AEM Project Build**: `{aemBuilderUrl}/api/build-aem-project`

## Priority Order

The configuration is loaded in this priority order:

1. **localStorage override** (set via config panel)
2. **Environment variables** (from .env files)
3. **Default values** (port 8000 for Docker setup)

## Troubleshooting

### Frontend can't connect to backend:
1. Check if backend is running on the expected port
2. Verify API URL in config panel (`Ctrl+Shift+C`)
3. Check browser developer console for network errors
4. Ensure no CORS issues (backend should handle CORS)

### Wrong port being used:
1. Check which `.env` file is active
2. Use config panel to override URL temporarily
3. Clear localStorage: `localStorage.removeItem('API_BASE_URL')`

### Environment variables not working:
1. Restart the frontend (`npm start`)
2. Ensure `.env` files are in the `frontend/` directory
3. Environment variables must start with `REACT_APP_`

## Benefits

✅ **Flexible Development**: Easy switching between Docker and direct Python backend  
✅ **Environment-Specific**: Different configurations for dev/prod  
✅ **Runtime Changes**: No restart required to change API URLs  
✅ **Visual Feedback**: Config panel shows current settings  
✅ **Backward Compatibility**: Existing code continues to work
