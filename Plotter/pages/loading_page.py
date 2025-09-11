"""
Loading page module for Unified Plotter.

Handles loading screen UI with progress updates and animations.
"""

import tkinter as tk
from tkinter import font as tkFont

class LoadingPage:
    """Manages the loading page UI and interactions"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # UI components
        self.loading_label = None
        self.progress_frame = None
        self.progress_indicator = None
        self.status_text = None
        self.progress_text = None
        self.spinner_canvas = None
        self.version_text = None
        
        # Animation variables
        self.spinner_angle = 0
        self.progress_value = 0
        self.animation_running = False
    
    def create_loading_ui(self):
        """Create the loading page UI"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Loading message
        loading_text = (
            "Initializing Unified Plotter...\n\n"
            "Setting up professional visualization environment\n"
            "Loading enterprise-grade features\n"
            "Preparing for optimal performance\n\n"
            "Please wait while we prepare everything for you."
        )
        
        self.loading_label = tk.Label(
            self.parent_frame, 
            text=loading_text, 
            font=tkFont.Font(family="Helvetica", size=14),
            justify=tk.CENTER, 
            bg="#1a1a1a", 
            fg="#cccccc", 
            pady=20, 
            wraplength=500
        )
        self.loading_label.pack(expand=True)
        
        # Progress bar
        self.progress_frame = tk.Frame(
            self.parent_frame, 
            bg="#333333", 
            height=8, 
            width=400
        )
        self.progress_frame.pack(pady=(20, 10))
        self.progress_frame.pack_propagate(False)
        
        self.progress_indicator = tk.Frame(
            self.progress_frame, 
            bg="#00ff88", 
            height=8
        )
        self.progress_indicator.pack(side="left", fill="y")
        
        # Status text
        self.status_text = tk.Label(
            self.parent_frame, 
            text="Starting up...", 
            font=tkFont.Font(family="Helvetica", size=12),
            bg="#1a1a1a", 
            fg="#888888"
        )
        self.status_text.pack(pady=(10, 0))
        
        # Progress text
        self.progress_text = tk.Label(
            self.parent_frame, 
            text="0%", 
            font=tkFont.Font(family="Helvetica", size=11, weight="bold"),
            bg="#1a1a1a", 
            fg="#00ff88"
        )
        self.progress_text.pack(pady=(5, 0))
        
        # Spinner
        self.spinner_canvas = tk.Canvas(
            self.parent_frame, 
            width=40, 
            height=40, 
            bg="#1a1a1a", 
            highlightthickness=0
        )
        self.spinner_canvas.pack(pady=(20, 0))
        
        # Version info
        self.version_text = tk.Label(
            self.parent_frame, 
            text="v2.0.0 Professional Edition", 
            font=tkFont.Font(family="Helvetica", size=10),
            bg="#1a1a1a", 
            fg="#666666"
        )
        self.version_text.pack(side="bottom", pady=(20, 0))
        
        # Start loading animation
        self.start_loading_animation()
    
    def start_loading_animation(self):
        """Start the loading spinner animation"""
        self.spinner_angle = 0
        self.animation_running = True
        self.animate_spinner()
    
    def animate_spinner(self):
        """Animate the loading spinner"""
        if self.spinner_canvas and self.animation_running:
            self.spinner_canvas.delete("all")
            
            # Draw spinner
            center_x, center_y = 20, 20
            radius = 15
            
            # Draw spinner arc
            self.spinner_canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=self.spinner_angle, extent=270,
                outline="#00ff88", width=3, style="arc"
            )
            
            self.spinner_angle = (self.spinner_angle + 10) % 360
            
            # Schedule next frame
            self.parent_frame.after(50, self.animate_spinner)
    
    def update_loading_progress(self):
        """Update loading progress bar"""
        if self.progress_frame and self.progress_indicator:
            # Calculate progress width
            progress_width = int((self.progress_value / 100) * 400)
            self.progress_indicator.configure(width=progress_width)
            
            # Update progress text
            if self.progress_text:
                self.progress_text.configure(text=f"{int(self.progress_value)}%")
    
    def update_progress(self, message, progress, total=100):
        """Update progress screen with new message and progress"""
        if self.status_text:
            self.status_text.configure(text=message)
        
        # Update progress bar
        progress_percent = (progress / total) * 100
        self.progress_value = progress_percent
        self.update_loading_progress()
    
    def stop_animation(self):
        """Stop the loading animation"""
        self.animation_running = False
    
    def destroy(self):
        """Clean up the loading page"""
        self.stop_animation()
        if self.loading_label:
            self.loading_label.destroy()
        if self.progress_frame:
            self.progress_frame.destroy()
        if self.status_text:
            self.status_text.destroy()
        if self.progress_text:
            self.progress_text.destroy()
        if self.spinner_canvas:
            self.spinner_canvas.destroy()
        if self.version_text:
            self.version_text.destroy()
