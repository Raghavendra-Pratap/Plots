"""
Main entry point for Unified Plotter application.

Handles application startup, dependency checking, and main execution flow.
"""

import sys
import os
import logging
from datetime import datetime

# Add the plotter directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dependencies import check_and_install_dependencies, import_dependencies
from ui_manager import UnifiedScreenManager
from settings import SettingsManager
from plotter import BoundingBoxPlotter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('plotter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def show_loading_screen():
    """Show a simple loading screen while dependencies are being checked"""
    try:
        import tkinter as tk
        from tkinter import font as tkFont
        
        # Create loading window
        loading_root = tk.Tk()
        loading_root.title("Unified Plotter - Loading")
        loading_root.configure(bg="#1a1a1a")
        loading_root.geometry("400x300")
        loading_root.resizable(False, False)
        
        # Center the window
        screen_width = loading_root.winfo_screenwidth()
        screen_height = loading_root.winfo_screenheight()
        center_x = int(screen_width/2 - 200)
        center_y = int(screen_height/2 - 150)
        loading_root.geometry(f"400x300+{center_x}+{center_y}")
        
        # Loading content
        title_label = tk.Label(loading_root, text="Unified Plotter", 
                             font=tkFont.Font(family="Helvetica", size=24, weight="bold"),
                             bg="#1a1a1a", fg="#ffffff")
        title_label.pack(pady=(50, 10))
        
        subtitle_label = tk.Label(loading_root, text="Professional Bounding Box Visualization", 
                                font=tkFont.Font(family="Helvetica", size=12),
                                bg="#1a1a1a", fg="#888888")
        subtitle_label.pack(pady=(0, 30))
        
        loading_label = tk.Label(loading_root, text="Loading...", 
                               font=tkFont.Font(family="Helvetica", size=14),
                               bg="#1a1a1a", fg="#cccccc")
        loading_label.pack(pady=(0, 20))
        
        # Progress bar
        progress_frame = tk.Frame(loading_root, bg="#333333", height=8, width=300)
        progress_frame.pack(pady=(0, 10))
        progress_frame.pack_propagate(False)
        
        progress_indicator = tk.Frame(progress_frame, bg="#00ff88", height=8)
        progress_indicator.pack(side="left", fill="y")
        
        # Version info
        version_label = tk.Label(loading_root, text="v2.0.0 Professional Edition", 
                               font=tkFont.Font(family="Helvetica", size=10),
                               bg="#1a1a1a", fg="#666666")
        version_label.pack(side="bottom", pady=(0, 20))
        
        loading_root.update()
        return loading_root
        
    except Exception as e:
        print(f"Error creating loading screen: {e}")
        return None

def main():
    """Main application entry point"""
    try:
        # Show loading screen
        loading_root = show_loading_screen()
        
        # Check dependencies with progress updates
        def update_progress(message, progress, total=100):
            if loading_root:
                loading_root.update()
        
        if not check_and_install_dependencies(update_progress):
            print("Some dependencies could not be installed. Please install them manually and try again.")
            if loading_root:
                loading_root.destroy()
            sys.exit(1)
        
        # Import dependencies
        if not import_dependencies():
            print("Failed to import dependencies. Exiting.")
            if loading_root:
                loading_root.destroy()
            sys.exit(1)
        
        # Close loading screen
        if loading_root:
            loading_root.destroy()
        
        # Initialize managers
        screen_manager = UnifiedScreenManager()
        settings_manager = SettingsManager()
        plotter = BoundingBoxPlotter()
        
        # Set up logging
        plotter.setup_logging()
        
        # Apply global settings
        plotter.apply_global_settings()
        
        # Define callbacks
        def select_file_and_close():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=os.getcwd()
            )
            if file_path:
                screen_manager.destroy()
                plotter.process_csv_file(file_path)
        
        def show_settings_page():
            """Show settings page"""
            screen_manager.clear_content()
            screen_manager.current_mode = "settings"
            
            # Hide the logo section for settings
            if screen_manager.logo_frame:
                screen_manager.logo_frame.pack_forget()
            
            # Create settings page
            from pages import SettingsPage
            settings_page = SettingsPage(
                screen_manager.content_frame,
                save_callback=lambda settings: _save_settings(settings),
                cancel_callback=lambda: _cancel_settings()
            )
            settings_page.create_settings_ui()
            screen_manager.settings_page = settings_page
        
        def _save_settings(settings):
            """Save settings and return to welcome screen"""
            print("Settings saved!")
            # Restore logo section
            if screen_manager.logo_frame:
                screen_manager.logo_frame.pack(pady=(0, 20))
            screen_manager.show_welcome_screen(select_file_and_close, show_settings_page)
        
        def _cancel_settings():
            """Cancel settings and return to welcome screen"""
            print("Settings cancelled - returning to welcome screen")
            # Restore logo section
            if screen_manager.logo_frame:
                screen_manager.logo_frame.pack(pady=(0, 20))
            screen_manager.show_welcome_screen(select_file_and_close, show_settings_page)
        
        # Create unified window and show welcome screen
        screen_manager.create_unified_window("Unified Plotter | Professional Bounding Box Visualization", show_title_bar=True)
        screen_manager.show_welcome_screen(select_file_and_close, show_settings_page)
        screen_manager.run()
        
    except Exception as e:
        logger.error(f"Error in main application: {e}", exc_info=True)
        print(f"Critical error: {e}")
        # Try to save error information
        try:
            import traceback
            error_file = os.path.join(os.path.expanduser("~"), 'plotter_crash.log')
            with open(error_file, 'w') as f:
                f.write(f"Plotter Crash Report\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {e}\n")
                f.write("Traceback:\n")
                traceback.print_exc(file=f)
            print(f"Crash details saved to: {error_file}")
        except:
            pass

if __name__ == "__main__":
    main()
