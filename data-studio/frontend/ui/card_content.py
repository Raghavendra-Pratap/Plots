#!/usr/bin/env python3
"""
Card Content UI Component for Unified Data Studio
Content area for card widgets
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class CardContent(QWidget):
    """Content area for card widgets"""
    
    def __init__(self, content: str = ""):
        super().__init__()
        self.setup_ui(content)
    
    def setup_ui(self, content: str):
        """Setup the card content UI"""
        layout = QVBoxLayout(self)
        
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            layout.addWidget(content_label)
        
        layout.addStretch()
