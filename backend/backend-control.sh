#!/bin/bash

show_menu() {
    echo "========================================"
    echo "   Backend and MongoDB Control Script"
    echo "========================================"
    echo "1. Start Backend and MongoDB"
    echo "2. Stop Backend and MongoDB"
    echo "3. Restart Backend and MongoDB"
    echo "4. View Container Status"
    echo "5. View Backend Logs"
    echo "6. View MongoDB Logs"
    echo "7. Exit"
    echo "========================================"
}

start_services() {
    echo "Starting Backend and MongoDB containers..."
    if docker-compose up -d; then
        echo "✅ Services started successfully!"
        echo "Backend is available at: http://localhost:8000"
        echo "MongoDB is available at: localhost:27017"
    else
        echo "❌ Failed to start services!"
    fi
}

stop_services() {
    echo "Stopping Backend and MongoDB containers..."
    if docker-compose down; then
        echo "✅ Services stopped successfully!"
    else
        echo "❌ Failed to stop services!"
    fi
}

restart_services() {
    echo "Restarting Backend and MongoDB containers..."
    if docker-compose down && docker-compose up -d; then
        echo "✅ Services restarted successfully!"
        echo "Backend is available at: http://localhost:8000"
        echo "MongoDB is available at: localhost:27017"
    else
        echo "❌ Failed to restart services!"
    fi
}

show_status() {
    echo "Current container status:"
    docker-compose ps
}

show_backend_logs() {
    echo "Showing Backend logs (Press Ctrl+C to stop):"
    docker-compose logs -f backend
}

show_mongo_logs() {
    echo "Showing MongoDB logs (Press Ctrl+C to stop):"
    docker-compose logs -f mongodb
}

while true; do
    show_menu
    read -p "Please select an option (1-7): " choice
    
    case $choice in
        1)
            start_services
            ;;
        2)
            stop_services
            ;;
        3)
            restart_services
            ;;
        4)
            show_status
            ;;
        5)
            show_backend_logs
            ;;
        6)
            show_mongo_logs
            ;;
        7)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option! Please select 1-7."
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
    clear
done
