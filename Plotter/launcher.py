#!/usr/bin/env python3
"""
Launcher script for Unified Plotter.

This script provides a simple way to launch the Unified Plotter application
from the command line or by double-clicking.
"""

import sys
import os

# Add the plotter directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the Unified Plotter application"""
    try:
        import main
        main.main()
    except ImportError as e:
        print(f"Error importing main module: {e}")
        print("Please ensure all required dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
