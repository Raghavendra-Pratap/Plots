"""
Progress page module for Unified Plotter.

Handles progress screen UI for data processing operations.
"""

import tkinter as tk
from tkinter import font as tkFont

class ProgressPage:
    """Manages the progress page UI and interactions"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # UI components
        self.progress_label = None
        self.progress_frame = None
        self.progress_indicator = None
        self.progress_text = None
    
    def create_progress_ui(self, message, progress=0, total=100):
        """Create the progress page UI"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Progress message
        self.progress_label = tk.Label(
            self.parent_frame, 
            text=message, 
            font=tkFont.Font(family="Helvetica", size=16),
            justify=tk.CENTER, 
            bg="#1a1a1a", 
            fg="#ffffff", 
            pady=20, 
            wraplength=500
        )
        self.progress_label.pack(expand=True)
        
        # Progress bar
        self.progress_frame = tk.Frame(
            self.parent_frame, 
            bg="#333333", 
            height=12, 
            width=500
        )
        self.progress_frame.pack(pady=(20, 10))
        self.progress_frame.pack_propagate(False)
        
        # Progress indicator
        self.progress_indicator = tk.Frame(
            self.progress_frame, 
            bg="#00ff88", 
            height=12
        )
        self.progress_indicator.pack(side="left", fill="y")
        
        # Progress text
        self.progress_text = tk.Label(
            self.parent_frame, 
            text=f"{progress}%", 
            font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
            bg="#1a1a1a", 
            fg="#00ff88"
        )
        self.progress_text.pack(pady=(10, 0))
        
        # Update initial progress
        self.update_progress(message, progress, total)
    
    def update_progress(self, message, progress, total=100):
        """Update progress screen with new message and progress"""
        if self.progress_label:
            self.progress_label.configure(text=message)
        
        # Update progress bar
        progress_percent = (progress / total) * 100
        if self.progress_indicator:
            progress_width = int((progress_percent / 100) * 500)
            self.progress_indicator.configure(width=progress_width)
        
        # Update progress text
        if self.progress_text:
            self.progress_text.configure(text=f"{int(progress_percent)}%")
    
    def destroy(self):
        """Clean up the progress page"""
        if self.progress_label:
            self.progress_label.destroy()
        if self.progress_frame:
            self.progress_frame.destroy()
        if self.progress_text:
            self.progress_text.destroy()
