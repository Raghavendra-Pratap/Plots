#!/usr/bin/env python3
"""
Playground Component for Unified Data Studio
Data import, exploration, and workflow building interface
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal

class Playground(QWidget):
    """Playground component for data exploration and workflow building"""
    
    # Signals
    file_imported = Signal(str)
    workflow_executed = Signal(str)
    status_updated = Signal(str)
    
    def __init__(self, duckdb_service=None, data_service=None, workflow_service=None):
        super().__init__()
        
        # Store backend services
        self.duckdb_service = duckdb_service
        self.data_service = data_service
        self.workflow_service = workflow_service
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the playground user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Data Playground")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Import data, explore datasets, and build workflows")
        desc.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        layout.addWidget(desc)
        
        # Import button
        import_btn = QPushButton("Import Data")
        import_btn.clicked.connect(self.import_data)
        layout.addWidget(import_btn)
        
        # Workflow button
        workflow_btn = QPushButton("Build Workflow")
        workflow_btn.clicked.connect(self.build_workflow)
        layout.addWidget(workflow_btn)
        
        # Add stretch to push content to top
        layout.addStretch()
    
    def import_data(self):
        """Import data files"""
        self.status_updated.emit("Import data functionality not yet implemented")
        self.file_imported.emit("sample_file.csv")
    
    def build_workflow(self):
        """Build a new workflow"""
        self.status_updated.emit("Workflow builder not yet implemented")
        self.workflow_executed.emit("Sample Workflow")
    
    def show_data_explorer(self):
        """Show data explorer"""
        self.status_updated.emit("Data explorer not yet implemented")
    
    def show_formula_engine(self):
        """Show formula engine"""
        self.status_updated.emit("Formula engine not yet implemented")
