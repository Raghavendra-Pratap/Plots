import polars as pl
import subprocess
import platform
import os

def open_system_file_manager(path=None):
    """Open system file manager (Finder/Explorer)"""
    if path is None:
        path = os.getcwd()
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run(['open', path])
    elif system == "Windows":
        subprocess.run(['explorer', path])
    elif system == "Linux":
        subprocess.run(['xdg-open', path])
    else:
        print(f"Unsupported operating system: {system}")

# Usage
open_system_file_manager()  # Opens current directory
open_system_file_manager('/path/to/folder')  # Opens specific folder