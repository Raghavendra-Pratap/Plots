#!/usr/bin/env python3
"""
FastAPI Backend Startup Script
Manages virtual environment and starts the FastAPI server
"""

import os
import sys
import subprocess
import venv
import platform
from pathlib import Path

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    return venv_path

def get_python_executable(venv_path):
    """Get the Python executable path for the virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def get_pip_executable(venv_path):
    """Get the pip executable path for the virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"

def install_requirements(venv_path):
    """Install required packages in the virtual environment"""
    pip_path = get_pip_executable(venv_path)
    
    # Core FastAPI dependencies
    packages = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pandas>=2.0.0",
        "duckdb>=0.9.0",
        "polars>=0.19.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6"
    ]
    
    print("Installing required packages...")
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([str(pip_path), "install", package], check=True, capture_output=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def start_fastapi_server(venv_path):
    """Start the FastAPI server using uvicorn"""
    python_path = get_python_executable(venv_path)
    app_path = Path("app_fastapi.py")
    
    if not app_path.exists():
        print(f"❌ FastAPI app not found at {app_path}")
        return False
    
    print("Starting FastAPI server...")
    print(f"Python: {python_path}")
    print(f"App: {app_path}")
    
    try:
        # Start the server
        subprocess.run([
            str(python_path), "-m", "uvicorn", 
            "app_fastapi:app", 
            "--host", "0.0.0.0", 
            "--port", "5001",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    
    return True

def main():
    """Main function"""
    print("🚀 FastAPI Backend Startup Script")
    print("=" * 40)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Setup virtual environment
    venv_path = setup_virtual_environment()
    
    # Install requirements
    if not install_requirements(venv_path):
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Start server
    if not start_fastapi_server(venv_path):
        print("❌ Failed to start FastAPI server")
        sys.exit(1)
    
    print("✅ FastAPI server started successfully")

if __name__ == "__main__":
    main()
