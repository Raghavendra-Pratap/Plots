"""
Error page module for Unified Plotter.

Handles error screen UI with custom messages and action buttons.
"""

import tkinter as tk
from tkinter import font as tkFont

class ErrorPage:
    """Manages the error page UI and interactions"""
    
    def __init__(self, parent_frame, button_callback=None):
        self.parent_frame = parent_frame
        self.button_callback = button_callback
        
        # UI components
        self.error_icon = None
        self.error_title = None
        self.error_message = None
        self.action_button = None
    
    def create_error_ui(self, title, message, button_text="Home", button_callback=None):
        """Create the error page UI"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Use provided callback or default
        if button_callback:
            self.button_callback = button_callback
        
        # Error icon
        self.error_icon = tk.Label(
            self.parent_frame, 
            text="⚠️", 
            font=tkFont.Font(family="Helvetica", size=48),
            bg="#1a1a1a", 
            fg="#ff6b6b"
        )
        self.error_icon.pack(pady=(20, 10))
        
        # Error title
        self.error_title = tk.Label(
            self.parent_frame, 
            text=title, 
            font=tkFont.Font(family="Helvetica", size=24, weight="bold"),
            bg="#1a1a1a", 
            fg="#ffffff"
        )
        self.error_title.pack(pady=(0, 20))
        
        # Error message
        self.error_message = tk.Label(
            self.parent_frame, 
            text=message, 
            font=tkFont.Font(family="Helvetica", size=14),
            justify=tk.CENTER, 
            bg="#1a1a1a", 
            fg="#cccccc", 
            pady=10, 
            wraplength=500
        )
        self.error_message.pack(expand=True)
        
        # Action button
        if self.button_callback:
            self.action_button = tk.Button(
                self.parent_frame, 
                text=button_text, 
                command=self.button_callback, 
                font=tkFont.Font(family="Helvetica", size=16, weight="bold"), 
                bg="#00ff88", 
                fg="#1a1a1a", 
                activebackground="#00cc6a", 
                activeforeground="#1a1a1a",
                relief=tk.FLAT, 
                borderwidth=0, 
                padx=30, 
                pady=15,
                cursor="hand2"
            )
            self.action_button.pack(pady=(20, 0))
    
    def destroy(self):
        """Clean up the error page"""
        if self.error_icon:
            self.error_icon.destroy()
        if self.error_title:
            self.error_title.destroy()
        if self.error_message:
            self.error_message.destroy()
        if self.action_button:
            self.action_button.destroy()
