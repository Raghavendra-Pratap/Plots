"""
Settings page module for Unified Plotter.

Handles the settings page UI with device detection, performance profiling,
and configuration options.
"""

import tkinter as tk
from tkinter import font as tkFont
import os

class SettingsPage:
    """Manages the settings page UI and interactions"""
    
    def __init__(self, parent_frame, save_callback, cancel_callback):
        self.parent_frame = parent_frame
        self.save_callback = save_callback
        self.cancel_callback = cancel_callback
        
        # UI components
        self.settings_frame = None
        self.title_label = None
        self.desc_label = None
        self.cards_container = None
        self.left_column = None
        self.right_column = None
        self.button_frame = None
        self.save_button = None
        self.cancel_button = None
        
        # Settings variables
        self.settings_vars = {}
        self.profile_var = None
        
        # Default settings
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
    
    def create_settings_ui(self):
        """Create the settings page UI"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Create settings content
        self.settings_frame = tk.Frame(self.parent_frame, bg="#1a1a1a")
        self.settings_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        # Title
        self.title_label = tk.Label(
            self.settings_frame, 
            text="⚙️ Settings", 
            font=tkFont.Font(family="Helvetica", size=20, weight="bold"),
            bg="#1a1a1a", 
            fg="#ffffff"
        )
        self.title_label.pack(pady=(0, 5))
        
        # Description
        self.desc_label = tk.Label(
            self.settings_frame, 
            text="Configure application preferences and performance settings",
            font=tkFont.Font(family="Helvetica", size=12),
            bg="#1a1a1a", 
            fg="#cccccc"
        )
        self.desc_label.pack(pady=(0, 10))
        
        # Create scrollable frame for settings
        canvas = tk.Canvas(self.settings_frame, bg="#1a1a1a", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create a container frame for two-column layout
        self.cards_container = tk.Frame(scrollable_frame, bg="#1a1a1a")
        self.cards_container.pack(expand=True, fill="both", padx=30)
        
        # Create two columns with better spacing
        self.left_column = tk.Frame(self.cards_container, bg="#1a1a1a")
        self.left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.right_column = tk.Frame(self.cards_container, bg="#1a1a1a")
        self.right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # Create settings sections
        self._create_device_section()
        self._create_performance_section()
        self._create_features_section()
        self._create_memory_section()
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create button frame
        self.button_frame = tk.Frame(self.parent_frame, bg="#1a1a1a", height=50)
        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.button_frame.pack_propagate(False)
        
        # Create button container for centering
        button_container = tk.Frame(self.button_frame, bg="#1a1a1a")
        button_container.pack(expand=True)
        
        # Save button
        self.save_button = tk.Button(
            button_container, 
            text="💾 Save Settings", 
            command=self._save_settings,
            font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
            bg="#00ff88", 
            fg="#1a1a1a", 
            activebackground="#00cc6a", 
            activeforeground="#1a1a1a",
            relief=tk.FLAT, 
            padx=30, 
            pady=12, 
            cursor="hand2"
        )
        self.save_button.pack(side="right", padx=(15, 0))
        
        # Cancel button
        self.cancel_button = tk.Button(
            button_container, 
            text="❌ Cancel", 
            command=self._cancel_settings,
            font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
            bg="#666666", 
            fg="#ffffff", 
            activebackground="#888888", 
            activeforeground="#ffffff",
            relief=tk.FLAT, 
            padx=30, 
            pady=12, 
            cursor="hand2"
        )
        self.cancel_button.pack(side="right")
    
    def _create_device_section(self):
        """Create device information section"""
        # Get device profile
        device_profile = self._get_device_profile()
        performance_score = self._calculate_performance_score(device_profile)
        suggested_mode, suggested_text = self._get_performance_suggestion(performance_score)
        
        # Device info section
        device_frame = tk.LabelFrame(
            self.left_column, 
            text="📱 Device Information", 
            font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
            bg="#2a2a2a", 
            fg="#ffffff", 
            padx=15, 
            pady=15
        )
        device_frame.pack(fill="x", pady=(0, 8))
        
        # Center-aligned device info
        device_info = f"CPU: {device_profile['cpu_cores']} cores | RAM: {device_profile['ram_gb']:.1f}GB | Storage: {device_profile['storage_type'].upper()}"
        device_label = tk.Label(
            device_frame, 
            text=device_info, 
            font=tkFont.Font(family="Helvetica", size=13),
            bg="#2a2a2a", 
            fg="#ffffff"
        )
        device_label.pack(pady=5)
        
        # Performance score
        score_info = tk.Label(
            device_frame, 
            text=f"Performance Score: {performance_score}/100", 
            font=tkFont.Font(family="Helvetica", size=14, weight="bold"),
            bg="#2a2a2a", 
            fg="#00ff88"
        )
        score_info.pack(pady=(8, 3))
        
        # Suggested mode
        suggestion_info = tk.Label(
            device_frame, 
            text=f"Recommended: {suggested_text}", 
            font=tkFont.Font(family="Helvetica", size=12),
            bg="#2a2a2a", 
            fg="#cccccc"
        )
        suggestion_info.pack(pady=3)
    
    def _create_performance_section(self):
        """Create performance profile section"""
        profile_frame = tk.LabelFrame(
            self.left_column, 
            text="🚀 Performance Profile", 
            font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
            bg="#2a2a2a", 
            fg="#ffffff", 
            padx=15, 
            pady=15
        )
        profile_frame.pack(fill="x", pady=(0, 8))
        
        self.profile_var = tk.StringVar(value="balanced")
        
        # Center-aligned radio buttons for performance profiles
        tk.Radiobutton(
            profile_frame, 
            text="High Performance (All features)", 
            variable=self.profile_var, 
            value="high", 
            command=self._on_profile_change,
            font=tkFont.Font(family="Helvetica", size=13),
            bg="#2a2a2a", 
            fg="#ffffff", 
            selectcolor="#2a2a2a"
        ).pack(anchor="center", pady=2)
        
        tk.Radiobutton(
            profile_frame, 
            text="Balanced (Recommended)", 
            variable=self.profile_var, 
            value="balanced", 
            command=self._on_profile_change,
            font=tkFont.Font(family="Helvetica", size=13),
            bg="#2a2a2a", 
            fg="#ffffff", 
            selectcolor="#2a2a2a"
        ).pack(anchor="center", pady=2)
        
        tk.Radiobutton(
            profile_frame, 
            text="Low-End Optimized", 
            variable=self.profile_var, 
            value="low", 
            command=self._on_profile_change,
            font=tkFont.Font(family="Helvetica", size=13),
            bg="#2a2a2a", 
            fg="#ffffff", 
            selectcolor="#2a2a2a"
        ).pack(anchor="center", pady=2)
        
        tk.Radiobutton(
            profile_frame, 
            text="Custom (Manual configuration)", 
            variable=self.profile_var, 
            value="custom", 
            command=self._on_profile_change,
            font=tkFont.Font(family="Helvetica", size=13),
            bg="#2a2a2a", 
            fg="#ffffff", 
            selectcolor="#2a2a2a"
        ).pack(anchor="center", pady=2)
    
    def _create_features_section(self):
        """Create feature toggles section"""
        features_frame = tk.LabelFrame(
            self.right_column, 
            text="🎨 Feature Toggles", 
            font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
            bg="#2a2a2a", 
            fg="#ffffff", 
            padx=15, 
            pady=15
        )
        features_frame.pack(fill="x", pady=(0, 8))
        
        # Initialize settings variables
        self.settings_vars = {
            'show_background_images': tk.BooleanVar(value=self.settings['show_background_images']),
            'high_quality_thumbnails': tk.BooleanVar(value=self.settings['high_quality_thumbnails']),
            'real_time_hover': tk.BooleanVar(value=self.settings['real_time_hover']),
            'smooth_animations': tk.BooleanVar(value=self.settings['smooth_animations']),
            'anti_aliasing': tk.BooleanVar(value=self.settings['anti_aliasing'])
        }
        
        # Create checkboxes for features
        self._create_feature_checkbox(features_frame, "Background Images", 
                                    self.settings_vars['show_background_images'], 
                                    "Disabled by default - may impact performance")
        self._create_feature_checkbox(features_frame, "High-Quality Thumbnails", 
                                    self.settings_vars['high_quality_thumbnails'], 
                                    "Recommended for your device")
        self._create_feature_checkbox(features_frame, "Real-Time Hover", 
                                    self.settings_vars['real_time_hover'], 
                                    "Interactive hover effects")
        self._create_feature_checkbox(features_frame, "Smooth Animations", 
                                    self.settings_vars['smooth_animations'], 
                                    "UI transition effects")
        self._create_feature_checkbox(features_frame, "Anti-Aliasing", 
                                    self.settings_vars['anti_aliasing'], 
                                    "Sharp, crisp graphics")
    
    def _create_memory_section(self):
        """Create memory management section"""
        memory_frame = tk.LabelFrame(
            self.right_column, 
            text="💾 Memory Management", 
            font=tkFont.Font(family="Helvetica", size=15, weight="bold"),
            bg="#2a2a2a", 
            fg="#ffffff", 
            padx=15, 
            pady=15
        )
        memory_frame.pack(fill="x", pady=(0, 8))
        
        # Add memory management settings
        self.settings_vars.update({
            'progressive_loading': tk.BooleanVar(value=self.settings['progressive_loading']),
            'image_caching': tk.BooleanVar(value=self.settings['image_caching']),
            'aggressive_cleanup': tk.BooleanVar(value=self.settings['aggressive_cleanup'])
        })
        
        # Create memory management checkboxes
        self._create_feature_checkbox(memory_frame, "Progressive Thumbnail Loading", 
                                    self.settings_vars['progressive_loading'], 
                                    "Recommended for low-end devices")
        self._create_feature_checkbox(memory_frame, "Image Caching", 
                                    self.settings_vars['image_caching'], 
                                    "Recommended for your device")
        self._create_feature_checkbox(memory_frame, "Aggressive Memory Cleanup", 
                                    self.settings_vars['aggressive_cleanup'], 
                                    "Low-end optimization")
    
    def _create_feature_checkbox(self, parent, text, setting_var, description=""):
        """Create a feature checkbox with description"""
        frame = tk.Frame(parent, bg="#2a2a2a")
        frame.pack(fill="x", pady=2)
        
        cb = tk.Checkbutton(
            frame, 
            text=text, 
            variable=setting_var, 
            font=tkFont.Font(family="Helvetica", size=13),
            bg="#2a2a2a", 
            fg="#ffffff", 
            selectcolor="#2a2a2a"
        )
        cb.pack(anchor="center")
        
        if description:
            desc_label = tk.Label(
                frame, 
                text=description, 
                font=tkFont.Font(family="Helvetica", size=11),
                bg="#2a2a2a", 
                fg="#888888"
            )
            desc_label.pack(anchor="center", pady=(2, 0))
    
    def _get_device_profile(self):
        """Get device hardware profile"""
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
    
    def _calculate_performance_score(self, profile):
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
    
    def _get_performance_suggestion(self, score):
        """Get performance suggestion based on score"""
        if score >= 80:
            return 'high', 'High Performance (All features)'
        elif score >= 60:
            return 'balanced', 'Balanced (Recommended)'
        else:
            return 'low', 'Low-End Optimized'
    
    def _on_profile_change(self):
        """Handle performance profile change"""
        selected = self.profile_var.get()
        if selected != "custom":
            self._apply_performance_profile(selected)
            self._update_settings_display()
    
    def _apply_performance_profile(self, profile_name):
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
    
    def _update_settings_display(self):
        """Update the display of settings based on current values"""
        for key, var in self.settings_vars.items():
            if key in self.settings:
                var.set(self.settings[key])
    
    def _save_settings(self):
        """Save settings and return to welcome screen"""
        # Update settings from UI
        for key, var in self.settings_vars.items():
            self.settings[key] = var.get()
        
        # Call save callback
        if self.save_callback:
            self.save_callback(self.settings)
    
    def _cancel_settings(self):
        """Cancel settings and return to welcome screen"""
        if self.cancel_callback:
            self.cancel_callback()
    
    def destroy(self):
        """Clean up the settings page"""
        if self.settings_frame:
            self.settings_frame.destroy()
        if self.button_frame:
            self.button_frame.destroy()
