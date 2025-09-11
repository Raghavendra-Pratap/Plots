#!/bin/bash

# 🌍 Cross-Platform Build Script for Bounding Box Plotter
# This script builds your React app for multiple platforms

set -e  # Exit on any error

echo "🚀 Starting Cross-Platform Build Process"
echo "=========================================="

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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        print_error "Node.js version 16+ is required. Current version: $(node -v)"
        exit 1
    fi
    print_success "Node.js version: $(node -v)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    print_success "npm version: $(npm -v)"
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the project root."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if [ ! -d "node_modules" ]; then
        npm install
        print_success "Dependencies installed"
    else
        print_status "Dependencies already installed, skipping..."
    fi
}

# Build React app
build_react() {
    print_status "Building React application..."
    
    npm run build
    
    if [ -d "build" ]; then
        print_success "React app built successfully"
    else
        print_error "React build failed"
        exit 1
    fi
}

# Build Electron app (if electron directory exists)
build_electron() {
    if [ -d "electron" ]; then
        print_status "Building Electron desktop applications..."
        
        cd electron
        
        # Install Electron dependencies if needed
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        
        # Build for all platforms
        print_status "Building for Windows..."
        npm run dist:win || print_warning "Windows build failed"
        
        print_status "Building for macOS..."
        npm run dist:mac || print_warning "macOS build failed"
        
        print_status "Building for Linux..."
        npm run dist:linux || print_warning "Linux build failed"
        
        cd ..
        print_success "Electron builds completed"
    else
        print_warning "Electron directory not found, skipping desktop builds"
    fi
}

# Create PWA manifest
create_pwa() {
    print_status "Creating Progressive Web App manifest..."
    
    if [ ! -f "public/manifest.json" ]; then
        cat > public/manifest.json << EOF
{
  "short_name": "BB Plotter",
  "name": "Bounding Box Plotter",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
EOF
        print_success "PWA manifest created"
    else
        print_status "PWA manifest already exists"
    fi
}

# Create deployment packages
create_deployment_packages() {
    print_status "Creating deployment packages..."
    
    # Create web deployment package
    if [ -d "build" ]; then
        mkdir -p dist/web
        cp -r build/* dist/web/
        print_success "Web deployment package created in dist/web/"
    fi
    
    # Create source code package
    mkdir -p dist/source
    git archive --format=zip --output=dist/source/source-code.zip HEAD
    print_success "Source code package created in dist/source/"
    
    # Create documentation package
    mkdir -p dist/docs
    cp README.md CROSS_PLATFORM_PACKAGING.md dist/docs/ 2>/dev/null || true
    cp demo_data.csv dist/docs/ 2>/dev/null || true
    print_success "Documentation package created in dist/docs/"
}

# Create platform-specific installers
create_installers() {
    print_status "Creating platform-specific installers..."
    
    mkdir -p dist/installers
    
    # Copy Electron installers if they exist
    if [ -d "electron/dist" ]; then
        cp -r electron/dist/* dist/installers/
        print_success "Desktop installers copied to dist/installers/"
    fi
}

# Generate build report
generate_report() {
    print_status "Generating build report..."
    
    cat > dist/build-report.txt << EOF
Bounding Box Plotter - Build Report
==================================
Build Date: $(date)
Build Time: $(date +%s)

Platform Information:
- OS: $(uname -s)
- Architecture: $(uname -m)
- Node.js: $(node -v)
- npm: $(npm -v)

Build Results:
- React App: $(if [ -d "build" ]; then echo "SUCCESS"; else echo "FAILED"; fi)
- Electron: $(if [ -d "electron" ]; then echo "AVAILABLE"; else echo "NOT CONFIGURED"; fi)
- PWA: $(if [ -f "public/manifest.json" ]; then echo "CONFIGURED"; else echo "NOT CONFIGURED"; fi)

Output Directories:
- Web App: dist/web/
- Source Code: dist/source/
- Documentation: dist/docs/
- Installers: dist/installers/

Next Steps:
1. Test the web application in dist/web/
2. Verify desktop installers in dist/installers/
3. Deploy web app to your hosting provider
4. Distribute desktop installers to users
EOF
    
    print_success "Build report generated: dist/build-report.txt"
}

# Main build process
main() {
    echo ""
    print_status "Starting build process..."
    
    # Check prerequisites
    check_prerequisites
    
    # Install dependencies
    install_dependencies
    
    # Build React app
    build_react
    
    # Build Electron app
    build_electron
    
    # Create PWA manifest
    create_pwa
    
    # Create deployment packages
    create_deployment_packages
    
    # Create installers
    create_installers
    
    # Generate report
    generate_report
    
    echo ""
    print_success "🎉 Build process completed successfully!"
    echo ""
    print_status "Output directories:"
    echo "  📁 dist/web/          - Web application"
    echo "  📁 dist/source/       - Source code package"
    echo "  📁 dist/docs/         - Documentation"
    echo "  📁 dist/installers/   - Desktop installers"
    echo "  📄 dist/build-report.txt - Build report"
    echo ""
    print_status "Next steps:"
    echo "  1. Test the web application"
    echo "  2. Deploy to your hosting provider"
    echo "  3. Distribute desktop installers"
    echo "  4. Update your documentation"
    echo ""
}

# Run main function
main "$@" 