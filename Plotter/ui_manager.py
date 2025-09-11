"""
Unified Screen Manager for consistent UI across all application screens.

Handles loading, welcome, progress, error, and settings screens with
consistent styling and behavior.
"""

import tkinter as tk
from tkinter import font as tkFont
import time
import threading

# Import page modules
from pages import WelcomePage, SettingsPage, ErrorPage, LoadingPage, ProgressPage

class UnifiedScreenManager:
    """Manages all screen components (loading, welcome, progress, error) in one unified window"""
    
    def __init__(self):
        # Standard window dimensions for all components
        self.window_width = 800
        self.window_height = 600
        self.root = None
        self.main_container = None
        self.current_mode = None
        
        # Component references
        self.logo_frame = None
        self.content_frame = None
        
        # Page instances
        self.welcome_page = None
        self.settings_page = None
        self.error_page = None
        self.loading_page = None
        self.progress_page = None
    
    def create_unified_window(self, title="Unified Plotter", show_title_bar=True):
        """Create the unified window with standard dimensions"""
        # Destroy existing window if it exists
        if self.root:
            try:
                self.root.destroy()
            except:
                pass  # Window already destroyed
            
        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg="#1a1a1a")
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - self.window_width / 2)
        center_y = int(screen_height/2 - self.window_height / 2)
        
        # Ensure positive coordinates
        center_x = max(0, center_x)
        center_y = max(0, center_y)
        
        self.root.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')
        
        # Configure window properties
        self.root.resizable(False, False)
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg="#1a1a1a", padx=40, pady=40)
        self.main_container.pack(expand=True, fill="both")
        
        # Create logo section (always visible)
        self.create_logo_section()
        
        # Create content frame (dynamic content area)
        self.content_frame = tk.Frame(self.main_container, bg="#1a1a1a")
        self.content_frame.pack(expand=True, fill="both", pady=(20, 0))
        
        # Create button frame (for welcome screen)
        self.button_frame = tk.Frame(self.main_container, bg="#1a1a1a")
        self.button_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Force window to appear immediately
        self.root.update_idletasks()
        self.root.deiconify()
        
        # Apply overrideredirect after window is positioned (fixes macOS positioning issue)
        if not show_title_bar:
            self.root.overrideredirect(1)
    
    def create_logo_section(self):
        """Create the logo section with title and subtitle"""
        self.logo_frame = tk.Frame(self.main_container, bg="#1a1a1a")
        self.logo_frame.pack(pady=(0, 20))
        
        # Logo text
        logo_text = tk.Label(self.logo_frame, text="Unified Plotter", 
                            font=tkFont.Font(family="Helvetica", size=28, weight="bold"),
                            bg="#1a1a1a", fg="#ffffff")
        logo_text.pack()
        
        # Subtitle
        subtitle_text = tk.Label(self.logo_frame, text="Professional Bounding Box Visualization Tool", 
                               font=tkFont.Font(family="Helvetica", size=12),
                               bg="#1a1a1a", fg="#888888")
        subtitle_text.pack(pady=(5, 0))
    
    def clear_content(self):
        """Clear the content frame for new content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Destroy existing page instances
        if self.welcome_page:
            self.welcome_page.destroy()
            self.welcome_page = None
        if self.settings_page:
            self.settings_page.destroy()
            self.settings_page = None
        if self.error_page:
            self.error_page.destroy()
            self.error_page = None
        if self.loading_page:
            self.loading_page.destroy()
            self.loading_page = None
        if self.progress_page:
            self.progress_page.destroy()
            self.progress_page = None
    
    def show_loading_screen(self):
        """Display loading screen with progress updates"""
        self.clear_content()
        self.current_mode = "loading"
        
        # Create loading page
        self.loading_page = LoadingPage(self.content_frame)
        self.loading_page.create_loading_ui()
    
    def show_welcome_screen(self, select_callback, settings_callback):
        """Display welcome screen with file selection"""
        self.clear_content()
        self.current_mode = "welcome"
        
        # Restore logo section for welcome screen
        if self.logo_frame:
            self.logo_frame.pack(pady=(0, 20))
        
        # Create welcome page
        self.welcome_page = WelcomePage(
            self.content_frame, 
            select_callback, 
            settings_callback, 
            self.root.destroy
        )
        self.welcome_page.create_welcome_ui()
    
    def show_progress_screen(self, message, progress=0, total=100):
        """Display progress screen for data processing"""
        self.clear_content()
        self.current_mode = "progress"
        
        # Create progress page
        self.progress_page = ProgressPage(self.content_frame)
        self.progress_page.create_progress_ui(message, progress, total)
    
    def show_error_screen(self, title, message, button_text="Home", button_callback=None):
        """Display error screen with custom message and button"""
        self.clear_content()
        self.current_mode = "error"
        
        # Create error page
        self.error_page = ErrorPage(self.content_frame, button_callback)
        self.error_page.create_error_ui(title, message, button_text)
    
    def update_progress(self, message, progress, total=100):
        """Update progress screen with new message and progress"""
        if self.current_mode == "loading" and self.loading_page:
            self.loading_page.update_progress(message, progress, total)
        elif self.current_mode == "progress" and self.progress_page:
            self.progress_page.update_progress(message, progress, total)
    
    def run(self):
        """Start the main event loop"""
        if self.root:
            self.root.mainloop()
    
    def destroy(self):
        """Destroy the window and cleanup"""
        if self.root:
            self.root.destroy()
            self.root = None
