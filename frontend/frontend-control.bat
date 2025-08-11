@echo off
setlocal enabledelayedexpansion

REM Frontend Docker Control Script for Windows
REM This script provides easy management of the frontend Docker container

title Frontend Docker Control

:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

:menu
cls
echo ========================================
echo     Frontend Docker Control Script
echo ========================================
echo 1. Build Frontend Container
echo 2. Start Frontend Container
echo 3. Stop Frontend Container
echo 4. Restart Frontend Container
echo 5. View Container Status
echo 6. View Container Logs
echo 7. Clean Build (No Cache)
echo 8. Remove Container and Images
echo 9. Exit
echo ========================================
set /p choice="Please select an option (1-9): "

if "%choice%"=="1" goto build
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto status
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto clean_build
if "%choice%"=="8" goto remove_all
if "%choice%"=="9" goto exit
echo [ERROR] Invalid option. Please try again.
pause
goto menu

:build
echo [INFO] Building frontend container...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    goto menu
)
echo [SUCCESS] Frontend container built successfully!
pause
goto menu

:start
echo [INFO] Starting frontend container...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Start failed!
    pause
    goto menu
)
echo [SUCCESS] Frontend container started successfully!
echo [INFO] Frontend is available at: http://localhost:3000
pause
goto menu

:stop
echo [INFO] Stopping frontend container...
docker-compose down
if errorlevel 1 (
    echo [ERROR] Stop failed!
    pause
    goto menu
)
echo [SUCCESS] Frontend container stopped successfully!
pause
goto menu

:restart
echo [INFO] Restarting frontend container...
docker-compose restart
if errorlevel 1 (
    echo [ERROR] Restart failed!
    pause
    goto menu
)
echo [SUCCESS] Frontend container restarted successfully!
pause
goto menu

:status
echo [INFO] Container status:
docker-compose ps
pause
goto menu

:logs
echo [INFO] Showing container logs (press Ctrl+C to exit):
docker-compose logs -f frontend
pause
goto menu

:clean_build
echo [INFO] Building frontend container with no cache...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Clean build failed!
    pause
    goto menu
)
echo [SUCCESS] Clean build completed successfully!
pause
goto menu

:remove_all
echo [WARNING] This will remove the container and all associated images.
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    echo [INFO] Removing containers and images...
    docker-compose down --rmi all --volumes --remove-orphans
    if errorlevel 1 (
        echo [ERROR] Removal failed!
        pause
        goto menu
    )
    echo [SUCCESS] All containers and images removed successfully!
) else (
    echo [INFO] Operation cancelled.
)
pause
goto menu

:exit
echo [INFO] Goodbye!
pause
exit /b 0
