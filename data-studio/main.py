#!/usr/bin/env python3
"""
Unified Data Studio - Main PySide6 Desktop Application
Cross-platform desktop application for data processing and analytics
"""

import sys
import os
import platform
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont

# Import our components
from frontend.components.main_window import MainWindow
from backend.services.duckdb_service import DuckDBService
from backend.services.data_service import DataService
from backend.services.workflow_service import WorkflowService
from backend.models.database import init_database

class UnifiedDataStudio(QMainWindow):
    """Main application window for Unified Data Studio"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified Data Studio")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize backend services
        self.init_backend_services()
        
        # Setup platform-specific configurations
        self.setup_platform_specifics()
        
        # Setup the main user interface
        self.setup_ui()
        
        # Initialize database
        self.init_database()
        
    def init_backend_services(self):
        """Initialize backend services"""
        try:
            self.duckdb_service = DuckDBService()
            self.data_service = DataService()
            self.workflow_service = WorkflowService()
            print("Backend services initialized successfully")
        except Exception as e:
            print(f"Failed to initialize backend services: {e}")
            # Continue without backend services for now
    
    def setup_platform_specifics(self):
        """Handle platform-specific configurations"""
        if platform.system() == "Darwin":  # macOS
            # macOS-specific menu bar
            self.setUnifiedTitleAndToolBarOnMac(True)
            # Set macOS-specific font
            self.setFont(QFont("SF Pro Display", 12))
            
        elif platform.system() == "Windows":
            # Windows-specific styling
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QTabWidget::pane {
                    border: 1px solid #c0c0c0;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #e0e0e0;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #0078d4;
                }
            """)
            # Set Windows-specific font
            self.setFont(QFont("Arial", 9))
            
        else:  # Linux
            # Linux automatically adapts to system theme
            self.setFont(QFont("Ubuntu", 10))
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main window component
        self.main_window = MainWindow(
            duckdb_service=self.duckdb_service,
            data_service=self.data_service,
            workflow_service=self.workflow_service
        )
        main_layout.addWidget(self.main_window)
    
    def init_database(self):
        """Initialize the database"""
        try:
            init_database()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization failed: {e}")

def main():
    """Main application entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Unified Data Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Unified Data Studio")
    
    # High-DPI scaling is now automatic in modern Qt versions
    
    # Set application icon if available
    icon_path = project_root / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    main_window = UnifiedDataStudio()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
