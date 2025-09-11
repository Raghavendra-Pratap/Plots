#!/usr/bin/env python3
"""
Card UI Component for Unified Data Studio
Reusable card widget for displaying information
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class Card(QFrame):
    """Reusable card widget"""
    
    def __init__(self, title: str = "", content: str = ""):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setup_ui(title, content)
    
    def setup_ui(self, title: str, content: str):
        """Setup the card UI"""
        layout = QVBoxLayout(self)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(title_label)
        
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            layout.addWidget(content_label)
        
        layout.addStretch()
