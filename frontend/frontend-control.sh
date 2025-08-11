#!/bin/bash

# Frontend Docker Control Script
# This script provides easy management of the frontend Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to show menu
show_menu() {
    echo "========================================"
    echo "    Frontend Docker Control Script"
    echo "========================================"
    echo "1. Build Frontend Container"
    echo "2. Start Frontend Container"
    echo "3. Stop Frontend Container"
    echo "4. Restart Frontend Container"
    echo "5. View Container Status"
    echo "6. View Container Logs"
    echo "7. Clean Build (No Cache)"
    echo "8. Remove Container and Images"
    echo "9. Exit"
    echo "========================================"
}

# Function to build container
build_container() {
    print_status "Building frontend container..."
    docker-compose build
    print_success "Frontend container built successfully!"
}

# Function to start container
start_container() {
    print_status "Starting frontend container..."
    docker-compose up -d
    print_success "Frontend container started successfully!"
    print_status "Frontend is available at: http://localhost:3000"
}

# Function to stop container
stop_container() {
    print_status "Stopping frontend container..."
    docker-compose down
    print_success "Frontend container stopped successfully!"
}

# Function to restart container
restart_container() {
    print_status "Restarting frontend container..."
    docker-compose restart
    print_success "Frontend container restarted successfully!"
}

# Function to show status
show_status() {
    print_status "Container status:"
    docker-compose ps
}

# Function to show logs
show_logs() {
    print_status "Showing container logs (press Ctrl+C to exit):"
    docker-compose logs -f frontend
}

# Function to clean build
clean_build() {
    print_status "Building frontend container with no cache..."
    docker-compose build --no-cache
    print_success "Clean build completed successfully!"
}

# Function to remove everything
remove_all() {
    print_warning "This will remove the container and all associated images."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing containers and images..."
        docker-compose down --rmi all --volumes --remove-orphans
        print_success "All containers and images removed successfully!"
    else
        print_status "Operation cancelled."
    fi
}

# Check if Docker is running
check_docker

# Main loop
while true; do
    show_menu
    read -p "Please select an option (1-9): " choice
    
    case $choice in
        1)
            build_container
            ;;
        2)
            start_container
            ;;
        3)
            stop_container
            ;;
        4)
            restart_container
            ;;
        5)
            show_status
            ;;
        6)
            show_logs
            ;;
        7)
            clean_build
            ;;
        8)
            remove_all
            ;;
        9)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please try again."
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
    clear
done
