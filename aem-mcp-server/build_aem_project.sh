#!/bin/bash

# AEM Project Build Script
# This script builds an AEM project using Maven

# Exit on error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Default values
PROJECT_PATH="${1:-/path/to/your/aem/project}"
MAVEN_PROFILE="${2:-autoInstallPackage}"
ADOBE_PROFILE="${2:-adobe-public}"

print_status "Starting AEM project build..."
print_status "Project path: $PROJECT_PATH"
print_status "Maven profile: $MAVEN_PROFILE"
print_status "Maven profile: $ADOBE_PROFILE"

# Check if project directory exists
if [ ! -d "$PROJECT_PATH" ]; then
    print_error "Project directory does not exist: $PROJECT_PATH"
    exit 1
fi

# Check if pom.xml exists
if [ ! -f "$PROJECT_PATH/pom.xml" ]; then
    print_error "pom.xml not found in project directory"
    exit 1
fi

# Change to project directory
cd "$PROJECT_PATH"

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    print_error "Maven is not installed or not in PATH"
    exit 1
fi

# Print Maven version
print_status "Maven version:"
mvn --version

# Clean any previous builds
print_status "Cleaning previous builds..."
mvn clean

# Build the project
print_status "Building AEM project..."
if [ -n "$MAVEN_PROFILE" ]; then
    mvn install -P"$MAVEN_PROFILE" -P"$ADOBE_PROFILE"
    print_status "Using Maven profiles: $MAVEN_PROFILE, $ADOBE_PROFILE
else
    mvn install
fi

# Check if build was successful
if [ $? -eq 0 ]; then
    print_status "AEM project build completed successfully!"
    
    # Find generated packages
    print_status "Generated packages:"
    find . -name "*.zip" -path "*/target/*" -type f | while read -r package; do
        echo "  - $package"
    done
else
    print_error "Build failed!"
    exit 1
fi

print_status "Build process completed."
