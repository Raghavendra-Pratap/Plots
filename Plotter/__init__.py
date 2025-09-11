"""
Unified Plotter - Professional Bounding Box Visualization Tool

A modular, professional-grade application for visualizing and annotating 
bounding box data from CSV files with enterprise-grade features.

Modules:
- main: Main application entry point
- ui_manager: Unified screen management and UI components
- settings: Settings page and configuration management
- plotter: Core plotting and visualization functionality
- utils: Utility functions and helpers
- dependencies: Dependency management and installation
"""

__version__ = "2.0.0"
__author__ = "Unified Plotter Team"

# Import main components for easy access
from .main import main
from .ui_manager import UnifiedScreenManager
from .settings import SettingsManager
from .plotter import BoundingBoxPlotter

__all__ = [
    'main',
    'UnifiedScreenManager', 
    'SettingsManager',
    'BoundingBoxPlotter'
]
