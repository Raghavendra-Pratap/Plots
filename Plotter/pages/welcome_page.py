"""
Welcome page module for Unified Plotter.

Handles the welcome screen UI with file selection and navigation buttons.
"""

import tkinter as tk
from tkinter import font as tkFont

class WelcomePage:
    """Manages the welcome page UI and interactions"""
    
    def __init__(self, parent_frame, select_callback, settings_callback, exit_callback):
        self.parent_frame = parent_frame
        self.select_callback = select_callback
        self.settings_callback = settings_callback
        self.exit_callback = exit_callback
        
        # UI components
        self.description_label = None
        self.select_button = None
        self.settings_button = None
        self.exit_button = None
        self.button_frame = None
    
    def create_welcome_ui(self):
        """Create the welcome page UI"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Description text
        description_text = (
            "Welcome to the professional bounding box visualization tool!\n\n"
            "This advanced tool helps you visualize and annotate bounding box data\n"
            "directly from your CSV files with enterprise-grade features.\n\n"
            "📋 Requirements:\n"
            "• CSV must include: image_id, x_min, x_max, y_min, y_max\n"
            "• Optional: label_* columns or image URL columns\n\n"
            "🚀 Click below to begin your professional workflow.\n"
            "⬇"
        )
        
        self.description_label = tk.Label(
            self.parent_frame, 
            text=description_text, 
            font=tkFont.Font(family="Helvetica", size=12),
            justify=tk.CENTER, 
            bg="#1a1a1a", 
            fg="#cccccc", 
            pady=20, 
            wraplength=700
        )
        self.description_label.pack()
        
        # Main action button
        self.select_button = tk.Button(
            self.parent_frame, 
            text="📁 Select CSV File", 
            command=self.select_callback, 
            font=tkFont.Font(family="Helvetica", size=15, weight="bold"), 
            bg="#e0e0e0", 
            fg="#333333", 
            activebackground="#d0d0d0", 
            activeforeground="#333333",
            relief=tk.RAISED, 
            borderwidth=2, 
            padx=35, 
            pady=20,
            cursor="hand2"
        )
        self.select_button.pack(pady=(30, 0))
        
        # Create button frame for bottom buttons
        self.button_frame = tk.Frame(self.parent_frame, bg="#1a1a1a")
        self.button_frame.pack(side="bottom", fill="x", pady=(30, 0))
        
        # Settings button
        self.settings_button = tk.Button(
            self.button_frame, 
            text="⚙️ Settings", 
            command=self.settings_callback, 
            font=tkFont.Font(family="Helvetica", size=16, weight="bold"), 
            bg="#666666", 
            fg="#ffffff", 
            activebackground="#888888", 
            activeforeground="#ffffff",
            relief=tk.FLAT, 
            borderwidth=0, 
            padx=30, 
            pady=15,
            cursor="hand2"
        )
        self.settings_button.pack(side="left", padx=(0, 15))
        
        # Exit button
        self.exit_button = tk.Button(
            self.button_frame, 
            text="❌ Exit", 
            command=self.exit_callback, 
            font=tkFont.Font(family="Helvetica", size=16, weight="bold"), 
            bg="#666666", 
            fg="#ffffff", 
            activebackground="#888888", 
            activeforeground="#ffffff",
            relief=tk.FLAT, 
            borderwidth=0, 
            padx=30, 
            pady=15,
            cursor="hand2"
        )
        self.exit_button.pack(side="right", padx=(15, 0))
    
    def destroy(self):
        """Clean up the welcome page"""
        if self.button_frame:
            self.button_frame.destroy()
        if self.description_label:
            self.description_label.destroy()
        if self.select_button:
            self.select_button.destroy()
        if self.settings_button:
            self.settings_button.destroy()
        if self.exit_button:
            self.exit_button.destroy()
