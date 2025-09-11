"""
Settings management module for Unified Plotter.

Handles device detection, performance profiling, and settings configuration
with intelligent recommendations based on hardware capabilities.
"""

import tkinter as tk
from tkinter import font as tkFont
import os

class SettingsManager:
    """Manages application settings and performance profiles"""
    
    def __init__(self):
        self.settings = {
            'show_background_images': False,
            'high_quality_thumbnails': True,
            'real_time_hover': True,
            'smooth_animations': False,
            'anti_aliasing': True,
            'progressive_loading': False,
            'image_caching': True,
            'aggressive_cleanup': False
        }
    
    def get_device_profile(self):
        """Get device hardware profile for intelligent suggestions"""
        try:
            import psutil
            cpu_cores = psutil.cpu_count()
            ram_gb = psutil.virtual_memory().total / (1024**3)
            
            # Simple storage type detection
            storage_type = 'hdd'  # Default assumption
            try:
                if os.path.exists('/sys/block/sda/queue/rotational'):
                    with open('/sys/block/sda/queue/rotational', 'r') as f:
                        if f.read().strip() == '0':
                            storage_type = 'ssd'
            except:
                pass
            
            return {
                'cpu_cores': cpu_cores,
                'ram_gb': ram_gb,
                'storage_type': storage_type
            }
        except ImportError:
            return {
                'cpu_cores': 4,
                'ram_gb': 8,
                'storage_type': 'hdd'
            }
    
    def calculate_performance_score(self, profile):
        """Calculate performance score based on device profile"""
        score = 0
        # CPU scoring
        if profile['cpu_cores'] >= 8:
            score += 40
        elif profile['cpu_cores'] >= 4:
            score += 30
        else:
            score += 20
        
        # RAM scoring
        if profile['ram_gb'] >= 16:
            score += 40
        elif profile['ram_gb'] >= 8:
            score += 30
        else:
            score += 20
        
        # Storage scoring
        if profile['storage_type'] == 'ssd':
            score += 20
        else:
            score += 10
        
        return min(score, 100)
    
    def get_performance_suggestion(self, score):
        """Get performance suggestion based on score"""
        if score >= 80:
            return 'high', 'High Performance (All features)'
        elif score >= 60:
            return 'balanced', 'Balanced (Recommended)'
        else:
            return 'low', 'Low-End Optimized'
    
    def apply_performance_profile(self, profile_name):
        """Apply predefined performance profile settings"""
        if profile_name == 'high':
            self.settings['show_background_images'] = True
            self.settings['high_quality_thumbnails'] = True
            self.settings['real_time_hover'] = True
            self.settings['smooth_animations'] = True
            self.settings['anti_aliasing'] = True
            self.settings['progressive_loading'] = False
            self.settings['image_caching'] = True
            self.settings['aggressive_cleanup'] = False
        elif profile_name == 'balanced':
            self.settings['show_background_images'] = False
            self.settings['high_quality_thumbnails'] = True
            self.settings['real_time_hover'] = True
            self.settings['smooth_animations'] = False
            self.settings['anti_aliasing'] = True
            self.settings['progressive_loading'] = False
            self.settings['image_caching'] = True
            self.settings['aggressive_cleanup'] = False
        elif profile_name == 'low':
            self.settings['show_background_images'] = False
            self.settings['high_quality_thumbnails'] = False
            self.settings['real_time_hover'] = False
            self.settings['smooth_animations'] = False
            self.settings['anti_aliasing'] = False
            self.settings['progressive_loading'] = True
            self.settings['image_caching'] = False
            self.settings['aggressive_cleanup'] = True
    
    def create_settings_ui(self, parent, screen_manager, select_callback, settings_callback):
        """Create the settings page UI"""
        try:
            # Clear the current content and show settings
            screen_manager.clear_content()
            screen_manager.current_mode = "settings"
            
            # Hide the logo section for settings
            if screen_manager.logo_frame:
                screen_manager.logo_frame.pack_forget()
            
            # Create settings content in the main window
            settings_frame = tk.Frame(screen_manager.content_frame, bg="#1a1a1a")
            settings_frame.pack(expand=True, fill="both", padx=10, pady=5)
            
            # Title
            title_label = tk.Label(settings_frame, text="⚙️ Settings", 
                                 font=tkFont.Font(family="Helvetica", size=20, weight="bold"),
                                 bg="#1a1a1a", fg="#ffffff")
            title_label.pack(pady=(0, 5))
            
            # Description
            desc_label = tk.Label(settings_frame, 
                                 text="Configure application preferences and performance settings",
                                 font=tkFont.Font(family="Helvetica", size=12),
                                 bg="#1a1a1a", fg="#cccccc")
            desc_label.pack(pady=(0, 10))
            
            # Create scrollable frame for settings
            canvas = tk.Canvas(settings_frame, bg="#1a1a1a", highlightthickness=0)
            scrollbar = tk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create a container frame for two-column layout
            cards_container = tk.Frame(scrollable_frame, bg="#1a1a1a")
            cards_container.pack(expand=True, fill="both", padx=30)
            
            # Create two columns with better spacing
            left_column = tk.Frame(cards_container, bg="#1a1a1a")
            left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
            
            right_column = tk.Frame(cards_container, bg="#1a1a1a")
            right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
            
            # Get device profile
            device_profile = self.get_device_profile()
            performance_score = self.calculate_performance_score(device_profile)
            suggested_mode, suggested_text = self.get_performance_suggestion(performance_score)
            
            # Device info section
            device_frame = tk.LabelFrame(left_column, text="📱 Device Information", 
                                       font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
                                       bg="#2a2a2a", fg="#ffffff", padx=15, pady=15)
            device_frame.pack(fill="x", pady=(0, 8))
            
            # Center-aligned device info
            device_info = f"CPU: {device_profile['cpu_cores']} cores | RAM: {device_profile['ram_gb']:.1f}GB | Storage: {device_profile['storage_type'].upper()}"
            device_label = tk.Label(device_frame, text=device_info, 
                                  font=tkFont.Font(family="Helvetica", size=13),
                                  bg="#2a2a2a", fg="#ffffff")
            device_label.pack(pady=5)
            
            # Performance score
            score_info = tk.Label(device_frame, text=f"Performance Score: {performance_score}/100", 
                                font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
                                bg="#2a2a2a", fg="#00ff88")
            score_info.pack(pady=(8, 3))
            
            # Suggested mode
            suggestion_info = tk.Label(device_frame, text=f"Recommended: {suggested_text}", 
                                     font=tkFont.Font(family="Helvetica", size=12),
                                     bg="#2a2a2a", fg="#cccccc")
            suggestion_info.pack(pady=3)
            
            # Performance profile section
            profile_frame = tk.LabelFrame(left_column, text="🚀 Performance Profile", 
                                        font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
                                        bg="#2a2a2a", fg="#ffffff", padx=15, pady=15)
            profile_frame.pack(fill="x", pady=(0, 8))
            
            profile_var = tk.StringVar(value="balanced")
            
            def on_profile_change():
                selected = profile_var.get()
                if selected != "custom":
                    self.apply_performance_profile(selected)
                    update_settings_display()
            
            # Center-aligned radio buttons for performance profiles
            tk.Radiobutton(profile_frame, text="High Performance (All features)", 
                          variable=profile_var, value="high", command=on_profile_change,
                          font=tkFont.Font(family="Helvetica", size=13),
                          bg="#2a2a2a", fg="#ffffff", selectcolor="#2a2a2a").pack(anchor="center", pady=2)
            
            tk.Radiobutton(profile_frame, text="Balanced (Recommended)", 
                          variable=profile_var, value="balanced", command=on_profile_change,
                          font=tkFont.Font(family="Helvetica", size=13),
                          bg="#2a2a2a", fg="#ffffff", selectcolor="#2a2a2a").pack(anchor="center", pady=2)
            
            tk.Radiobutton(profile_frame, text="Low-End Optimized", 
                          variable=profile_var, value="low", command=on_profile_change,
                          font=tkFont.Font(family="Helvetica", size=13),
                          bg="#2a2a2a", fg="#ffffff", selectcolor="#2a2a2a").pack(anchor="center", pady=2)
            
            tk.Radiobutton(profile_frame, text="Custom (Manual configuration)", 
                          variable=profile_var, value="custom", command=on_profile_change,
                          font=tkFont.Font(family="Helvetica", size=13),
                          bg="#2a2a2a", fg="#ffffff", selectcolor="#2a2a2a").pack(anchor="center", pady=2)
            
            # Feature toggles section
            features_frame = tk.LabelFrame(right_column, text="🎨 Feature Toggles", 
                                         font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
                                         bg="#2a2a2a", fg="#ffffff", padx=15, pady=15)
            features_frame.pack(fill="x", pady=(0, 8))
            
            # Initialize settings variables
            settings_vars = {
                'show_background_images': tk.BooleanVar(value=self.settings['show_background_images']),
                'high_quality_thumbnails': tk.BooleanVar(value=self.settings['high_quality_thumbnails']),
                'real_time_hover': tk.BooleanVar(value=self.settings['real_time_hover']),
                'smooth_animations': tk.BooleanVar(value=self.settings['smooth_animations']),
                'anti_aliasing': tk.BooleanVar(value=self.settings['anti_aliasing']),
                'progressive_loading': tk.BooleanVar(value=self.settings['progressive_loading']),
                'image_caching': tk.BooleanVar(value=self.settings['image_caching']),
                'aggressive_cleanup': tk.BooleanVar(value=self.settings['aggressive_cleanup'])
            }
            
            def create_feature_checkbox(parent, text, setting_var, description=""):
                frame = tk.Frame(parent, bg="#2a2a2a")
                frame.pack(fill="x", pady=2)
                
                cb = tk.Checkbutton(frame, text=text, variable=setting_var, 
                                  font=tkFont.Font(family="Helvetica", size=13),
                                  bg="#2a2a2a", fg="#ffffff", selectcolor="#2a2a2a")
                cb.pack(anchor="center")
                
                if description:
                    desc_label = tk.Label(frame, text=description, 
                                        font=tkFont.Font(family="Helvetica", size=11),
                                        bg="#2a2a2a", fg="#888888")
                    desc_label.pack(anchor="center", pady=(2, 0))
                
                return cb
            
            def update_settings_display():
                """Update the display of settings based on current values"""
                for key, var in settings_vars.items():
                    var.set(self.settings[key])
            
            # Create checkboxes for features in single column
            feature_checkboxes = {}
            
            feature_checkboxes['bg_images'] = create_feature_checkbox(features_frame, "Background Images", 
                                                                    settings_vars['show_background_images'], 
                                                                    "Disabled by default - may impact performance")
            feature_checkboxes['thumbnails'] = create_feature_checkbox(features_frame, "High-Quality Thumbnails", 
                                                                    settings_vars['high_quality_thumbnails'], 
                                                                    "Recommended for your device")
            feature_checkboxes['hover'] = create_feature_checkbox(features_frame, "Real-Time Hover", 
                                                                settings_vars['real_time_hover'], 
                                                                "Interactive hover effects")
            feature_checkboxes['animations'] = create_feature_checkbox(features_frame, "Smooth Animations", 
                                                                    settings_vars['smooth_animations'], 
                                                                    "UI transition effects")
            feature_checkboxes['anti_aliasing'] = create_feature_checkbox(features_frame, "Anti-Aliasing", 
                                                                        settings_vars['anti_aliasing'], 
                                                                        "Sharp, crisp graphics")
            
            # Memory management section
            memory_frame = tk.LabelFrame(right_column, text="💾 Memory Management", 
                                       font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
                                       bg="#2a2a2a", fg="#ffffff", padx=15, pady=15)
            memory_frame.pack(fill="x", pady=(0, 8))
            
            # Create memory management checkboxes in single column
            feature_checkboxes['progressive'] = create_feature_checkbox(memory_frame, "Progressive Thumbnail Loading", 
                                                                      settings_vars['progressive_loading'], 
                                                                      "Recommended for low-end devices")
            feature_checkboxes['caching'] = create_feature_checkbox(memory_frame, "Image Caching", 
                                                                  settings_vars['image_caching'], 
                                                                  "Recommended for your device")
            feature_checkboxes['cleanup'] = create_feature_checkbox(memory_frame, "Aggressive Memory Cleanup", 
                                                                  settings_vars['aggressive_cleanup'], 
                                                                  "Low-end optimization")
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Update button frame
            screen_manager.button_frame.pack_forget()
            button_frame = tk.Frame(screen_manager.root, bg="#1a1a1a", height=50)
            button_frame.pack(side="bottom", fill="x", padx=10, pady=5)
            button_frame.pack_propagate(False)
            
            # Create button container for centering
            button_container = tk.Frame(button_frame, bg="#1a1a1a")
            button_container.pack(expand=True)
            
            def save_settings():
                """Save settings and return to welcome screen"""
                print("Settings saved!")
                # Update settings from UI
                for key, var in settings_vars.items():
                    self.settings[key] = var.get()
                # Restore logo section
                if screen_manager.logo_frame:
                    screen_manager.logo_frame.pack(pady=(0, 20))
                screen_manager.show_welcome_screen(select_callback, settings_callback)
            
            def cancel_settings():
                """Cancel and return to welcome screen"""
                print("Settings cancelled - returning to welcome screen")
                try:
                    # Restore logo section
                    if screen_manager.logo_frame:
                        screen_manager.logo_frame.pack(pady=(0, 20))
                    # Return to welcome screen
                    screen_manager.show_welcome_screen(select_callback, settings_callback)
                    print("Successfully returned to welcome screen")
                except Exception as e:
                    print(f"Error returning to welcome screen: {e}")
            
            # Save button
            save_button = tk.Button(button_container, text="💾 Save Settings", 
                                  command=save_settings,
                                  font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
                                  bg="#00ff88", fg="#1a1a1a", 
                                  activebackground="#00cc6a", activeforeground="#1a1a1a",
                                  relief=tk.FLAT, padx=30, pady=12, cursor="hand2")
            save_button.pack(side="right", padx=(15, 0))
            
            # Cancel button
            cancel_button = tk.Button(button_container, text="❌ Cancel", 
                                    command=cancel_settings,
                                    font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
                                    bg="#666666", fg="#ffffff", 
                                    activebackground="#888888", activeforeground="#ffffff",
                                    relief=tk.FLAT, padx=30, pady=12, cursor="hand2")
            cancel_button.pack(side="right")
            
        except Exception as e:
            print(f"Error opening settings: {e}")
            # Fallback to simple message
            print("Settings page would open here")
