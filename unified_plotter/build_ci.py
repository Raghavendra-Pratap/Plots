#!/usr/bin/env python3
"""
CI Build Script for Unified Plotter
This script handles cross-platform builds in CI environments
"""
import os
import sys
import subprocess
import platform

def run_command(cmd, description):
    """Run a command and handle errors gracefully"""
    print(f"🔨 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def build_pyinstaller():
    """Build using PyInstaller"""
    print("🚀 Starting PyInstaller build...")
    
    # Check for the main script file
    script_file = None
    possible_names = ["unified-plotter.py", "unified_plotter.py"]
    
    for name in possible_names:
        if os.path.exists(name):
            script_file = name
            print(f"✅ Found script file: {name}")
            break
    
    if not script_file:
        print("❌ No main script file found!")
        print("Available Python files:")
        for file in os.listdir("."):
            if file.endswith(".py"):
                print(f"  - {file}")
        return False
    
    # Basic PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "unified-plotter",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "matplotlib.backends._tkagg",
        "--hidden-import", "matplotlib.backends.backend_tkagg",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--add-data", "version.py:.",
        "--distpath", "./dist",
        "--workpath", "./build",
        script_file
    ]
    
    return run_command(" ".join(cmd), "PyInstaller build")

def build_cx_freeze():
    """Build using cx_Freeze"""
    print("🚀 Starting cx_Freeze build...")
    
    # Create a simple setup script for cx_Freeze
    setup_content = '''
from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["tkinter", "matplotlib", "pandas", "numpy", "PIL"],
    "excludes": ["test", "unittest"],
    "include_files": ["version.py"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="unified-plotter",
    version="2.1.0",
    description="Professional tool for visualizing and annotating bounding box data",
    options={"build_exe": build_exe_options},
    executables=[Executable("unified-plotter.py", base=base, target_name="unified-plotter")]
)
'''
    
    with open("setup_cx.py", "w") as f:
        f.write(setup_content)
    
    return run_command("python setup_cx.py build", "cx_Freeze build")

def main():
    """Main build function"""
    print(f"🏗️  Building Unified Plotter on {platform.system()}")
    print(f"Python version: {sys.version}")
    
    # Ensure we're in the right directory
    if not os.path.exists("unified-plotter.py"):
        print("❌ unified-plotter.py not found. Please run from the unified_plotter directory.")
        sys.exit(1)
    
    # Create output directories
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    success = True
    
    # Try PyInstaller first
    if not build_pyinstaller():
        print("⚠️  PyInstaller build failed, trying cx_Freeze...")
        success = build_cx_freeze()
    
    if success:
        print("🎉 Build completed successfully!")
        # List what was created
        if os.path.exists("dist"):
            print("📦 Created files:")
            for root, dirs, files in os.walk("dist"):
                for file in files:
                    print(f"  - {os.path.join(root, file)}")
    else:
        print("❌ All build methods failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
