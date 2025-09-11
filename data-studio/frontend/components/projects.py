#!/usr/bin/env python3
"""
Projects Component for Unified Data Studio
Project management and organization interface
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal

class Projects(QWidget):
    """Projects component for project management"""
    
    # Signals
    project_created = Signal(str)
    status_updated = Signal(str)
    
    def __init__(self, data_service=None):
        super().__init__()
        
        # Store backend services
        self.data_service = data_service
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the projects user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Projects")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Manage your data science projects")
        desc.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        layout.addWidget(desc)
        
        # New project button
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_new_project)
        layout.addWidget(new_project_btn)
        
        # Open project button
        open_project_btn = QPushButton("Open Project")
        open_project_btn.clicked.connect(self.open_project)
        layout.addWidget(open_project_btn)
        
        # Add stretch to push content to top
        layout.addStretch()
    
    def create_new_project(self):
        """Create a new project"""
        self.status_updated.emit("New project functionality not yet implemented")
        self.project_created.emit("New Project")
    
    def open_project(self):
        """Open an existing project"""
        self.status_updated.emit("Open project functionality not yet implemented")
