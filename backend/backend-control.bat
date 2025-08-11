@echo off
setlocal

:menu
echo ========================================
echo   Backend and MongoDB Control Script
echo ========================================
echo 1. Start Backend and MongoDB
echo 2. Stop Backend and MongoDB
echo 3. Restart Backend and MongoDB
echo 4. View Container Status
echo 5. View Backend Logs
echo 6. View MongoDB Logs
echo 7. Exit
echo ========================================
set /p choice="Please select an option (1-7): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto backend_logs
if "%choice%"=="6" goto mongo_logs
if "%choice%"=="7" goto exit
goto invalid

:start
echo Starting Backend and MongoDB containers...
docker-compose up -d
if %errorlevel% equ 0 (
    echo ✅ Services started successfully!
    echo Backend is available at: http://localhost:8000
    echo MongoDB is available at: localhost:27017
) else (
    echo ❌ Failed to start services!
)
goto menu

:stop
echo Stopping Backend and MongoDB containers...
docker-compose down
if %errorlevel% equ 0 (
    echo ✅ Services stopped successfully!
) else (
    echo ❌ Failed to stop services!
)
goto menu

:restart
echo Restarting Backend and MongoDB containers...
docker-compose down
docker-compose up -d
if %errorlevel% equ 0 (
    echo ✅ Services restarted successfully!
    echo Backend is available at: http://localhost:8000
    echo MongoDB is available at: localhost:27017
) else (
    echo ❌ Failed to restart services!
)
goto menu

:status
echo Current container status:
docker-compose ps
goto menu

:backend_logs
echo Showing Backend logs (Press Ctrl+C to stop):
docker-compose logs -f backend
goto menu

:mongo_logs
echo Showing MongoDB logs (Press Ctrl+C to stop):
docker-compose logs -f mongodb
goto menu

:invalid
echo Invalid option! Please select 1-7.
goto menu

:exit
echo Goodbye!
exit /b 0
