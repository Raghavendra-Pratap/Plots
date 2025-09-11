"""
Dependency management and installation module.

Handles checking, installing, and importing all required dependencies
for the Unified Plotter application.
"""

import sys
import subprocess
import importlib
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        return False

def check_and_install_dependencies(progress_callback=None):
    """Check and install required dependencies with progress updates"""
    required_packages = {
        'matplotlib': 'matplotlib>=3.5.0',
        'pandas': 'pandas>=1.3.0',
        'numpy': 'numpy>=1.21.0',
        'PIL': 'Pillow>=8.0.0',  # Check for PIL instead of Pillow
        'psutil': 'psutil>=5.8.0',
        'requests': 'requests>=2.25.0'
    }
    
    if progress_callback:
        progress_callback("Checking dependencies...", 0, len(required_packages))
    
    installed_count = 0
    for package_name, package_spec in required_packages.items():
        try:
            if progress_callback:
                progress_callback(f"Checking {package_name}...", installed_count, len(required_packages))
            
            importlib.import_module(package_name)
            print(f"✓ {package_name} is already installed")
            installed_count += 1
        except ImportError:
            print(f"✗ {package_name} not found, installing...")
            if progress_callback:
                progress_callback(f"Installing {package_name}...", installed_count, len(required_packages))
            
            if install_package(package_spec):
                installed_count += 1
            else:
                print(f"⚠ Warning: Could not install {package_name}")
    
    if progress_callback:
        progress_callback("Dependencies check complete", len(required_packages), len(required_packages))
    
    return installed_count == len(required_packages)

def import_dependencies():
    """Import all required dependencies after they are installed"""
    global plt, patches, Button, RadioButtons, Slider, gridspec, Bbox, mpimg, np, pd, webbrowser, requests, Image, io
    
    try:
        # Import matplotlib with error handling
        import matplotlib
        matplotlib.use('TkAgg')  # Force TkAgg backend
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.widgets import Button, RadioButtons, Slider
        from matplotlib import gridspec
        from matplotlib.transforms import Bbox
        from matplotlib import image as mpimg
        print("✓ matplotlib imported successfully with TkAgg backend")
    except Exception as e:
        print(f"✗ Error importing matplotlib: {e}")
        print("Trying alternative backend...")
        try:
            import matplotlib
            matplotlib.use('Agg')  # Fallback to non-interactive backend
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.widgets import Button, RadioButtons, Slider
            from matplotlib import gridspec
            from matplotlib.transforms import Bbox
            from matplotlib import image as mpimg
            print("✓ matplotlib imported with Agg backend (non-interactive)")
        except Exception as e2:
            print(f"✗ Failed to import matplotlib: {e2}")
            print("Matplotlib will be installed by the dependency checker")
            # Set placeholder variables to prevent errors
            plt = None
            patches = None
            Button = None
            RadioButtons = None
            Slider = None
            gridspec = None
            Bbox = None
            mpimg = None

    # Import other dependencies
    import numpy as np
    import pandas as pd
    import webbrowser
    import requests
    from PIL import Image
    import io
        
    print("✓ All dependencies imported successfully")
    return True
