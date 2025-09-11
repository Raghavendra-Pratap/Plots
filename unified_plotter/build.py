#!/usr/bin/env python3
"""
Cross-platform build script for Unified Plotter
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    dirs_to_clean = ['build', 'dist', '__pycache__', '.pytest_cache']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    commands = [
        "pip install --upgrade pip",
        "pip install -r requirements.txt",
        "pip install pyinstaller cx-freeze setuptools wheel"
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    return True

def build_with_pyinstaller():
    """Build executable using PyInstaller"""
    print("🔨 Building with PyInstaller...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "unified-plotter",
        "--add-data", "version.py;.",
        "--hidden-import", "matplotlib.backends._tkagg",
        "--hidden-import", "matplotlib.backends.backend_tkagg",
        "--hidden-import", "PIL._tkinter_finder",
        "unified_plotter.py"
    ]
    
    if platform.system() == "Windows":
        cmd[4] = "version.py;."  # Windows uses semicolon
    else:
        cmd[4] = "version.py:."  # Unix uses colon
    
    return run_command(" ".join(cmd))

def build_with_cx_freeze():
    """Build executable using cx_Freeze"""
    print("🔨 Building with cx_Freeze...")
    return run_command("python setup.py build")

def create_installer():
    """Create installer package"""
    print("📦 Creating installer package...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        # Create NSIS installer (if available)
        print("   Windows installer creation not implemented yet")
    elif system == "darwin":
        # Create DMG for macOS
        print("   macOS DMG creation not implemented yet")
    else:
        # Create tar.gz for Linux
        print("   Linux package creation not implemented yet")

def main():
    """Main build function"""
    print("🚀 Starting Unified Plotter build process...")
    print(f"   Platform: {platform.system()} {platform.machine()}")
    print(f"   Python: {sys.version}")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Build steps
    steps = [
        ("Clean", clean_build),
        ("Install Dependencies", install_dependencies),
        ("Build PyInstaller", build_with_pyinstaller),
        ("Build cx_Freeze", build_with_cx_freeze),
        ("Create Installer", create_installer)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed!")
            sys.exit(1)
        print(f"✅ {step_name} completed!")
    
    print("\n🎉 Build completed successfully!")
    print("   Executables available in dist/ and build/ directories")

if __name__ == "__main__":
    main()
