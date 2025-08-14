#!/bin/bash

echo "🚀 Setting up Bounding Box Plotter Development Environment..."

# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    libgif-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libatk1.0-dev \
    libgdk-pixbuf2.0-dev \
    libgtk-3-dev \
    libtiff5-dev \
    libjpeg-dev \
    libpng-dev \
    libgif-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libgirepository1.0-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
cd bounding-box-plotter
pip install -r requirements.txt

# Install development tools
pip install \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    pytest-mock \
    pre-commit \
    ipython \
    jupyter \
    notebook

# Install PyInstaller for building executables
pip install pyinstaller

# Install additional development tools
pip install \
    sphinx \
    sphinx-rtd-theme \
    twine \
    build

# Set up pre-commit hooks
pre-commit install

# Create necessary directories
mkdir -p logs
mkdir -p builds
mkdir -p dist

# Set permissions
chmod +x build.py
chmod +x bounding_box_plotter.py

echo "✅ Development environment setup complete!"
echo "🐍 Python version: $(python --version)"
echo "📦 Installed packages: $(pip list | wc -l)"
echo "🚀 Ready to develop Bounding Box Plotter!" 