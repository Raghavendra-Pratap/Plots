#!/bin/bash

# Build script for Obsidian Vault Ignore Plugin

echo "Building Obsidian Vault Ignore Plugin..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build the plugin
echo "Building plugin..."
npm run build

# Check if build was successful
if [ -f "main.js" ]; then
    echo "✅ Build successful! Plugin files:"
    echo "  - main.js"
    echo "  - manifest.json"
    echo "  - versions.json"
    echo ""
    echo "To install the plugin:"
    echo "1. Copy the plugin folder to your vault's .obsidian/plugins/ directory"
    echo "2. Enable the plugin in Obsidian's Community Plugins settings"
    echo ""
    echo "Plugin folder location: $(pwd)"
else
    echo "❌ Build failed! Please check the error messages above."
    exit 1
fi
