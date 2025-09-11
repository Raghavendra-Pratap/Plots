"""
Simple plotter implementation that integrates with the modular structure.

This provides the core plotting functionality while maintaining compatibility
with the existing modular architecture.
"""

import sys
import os
import logging
import tempfile
import webbrowser
import io
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkFont
import threading
import time

# Set matplotlib backend before importing
os.environ['MPLBACKEND'] = 'TkAgg'

# Import all required modules
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, RadioButtons, Slider
from matplotlib import gridspec
from matplotlib.transforms import Bbox
from matplotlib import image as mpimg
from PIL import Image
import requests

# Global variables
df = None
output_dir = None
image_ids = []
annotation_states = {}
thumbnails = []
thumb_axes = []
current_image_idx = [0]
label_columns = []
image_url_columns = []
loaded_images = {}
labels_enabled = [True]
show_background_image = [False]
y_axis_flipped = [True]

# Global flags for preventing duplicate operations
_save_popup_showing = False
_close_operation_in_progress = False

# Global settings (default values, will be updated by SettingsManager)
global_settings = {
    'show_background_images': False,
    'high_quality_thumbnails': True,
    'real_time_hover': True,
    'smooth_animations': False,
    'anti_aliasing': True,
    'progressive_loading': False,
    'image_caching': True,
    'aggressive_cleanup': False,
    'disable_background_image_button': False,
    'save_plots_on_close': True,
    'log_retention': 7, # Days
    'enable_debug_logging': False,
    'thumbnail_width': 200,
    'thumbnail_padding': 5
}

# Matplotlib components
fig = None
main_ax = None
controls_ax = None
thumb_container_ax = None
nav_text = None
help_text_box = None
btn_help = None
btn_website = None

# Control buttons
btn_reset = None
btn_undo = None
btn_redo = None
btn_clear = None
btn_save = None
btn_close = None
btn_mode = None
btn_toggle_labels = None
btn_open_image = None
btn_toggle_background = None
btn_flip_y = None

# Progress management
progress_manager = None

# Logging setup
def setup_logging():
    """Setup logging system for the application"""
    # Create logs directory
    log_dir = os.path.join(tempfile.gettempdir(), 'plotter_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create session-specific log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'plotter_session_{timestamp}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("NEW PLOTTER SESSION STARTED")
    logger.info(f"Session ID: {timestamp}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {os.name}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    return logger, log_file, log_dir

# Initialize logging
logger, current_log_file, log_directory = setup_logging()

class AnnotationState:
    """Manages annotation state for a single image"""
    def __init__(self):
        self.annotations = []  # List of annotation dictionaries
        self.markers = []      # List of marker objects
        self.current_mode = 'x'  # 'x' for X marks, 'number' for numbered annotations
        self.next_number = 1
        self.counter = 1
        self.undone = []
        self.hover_text = None
        self.image_url = None
        self.mode = 'x'  # Current mode for this image
    
    def reset(self):
        """Reset annotation state"""
        self.annotations = []
        self.markers = []
        self.next_number = 1
        self.counter = 1
        self.undone = []
        self.hover_text = None

def generate_thumbnail(df_selected):
    """Generate thumbnail for the given dataframe"""
    try:
        if df_selected.empty or df_selected['x_min'].isna().all():
            # Create empty thumbnail
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=8)
            fig.canvas.draw()
            thumb = np.array(fig.canvas.renderer.buffer_rgba())
            plt.close(fig)
            return thumb
        
        # Calculate bounds
        x_min = df_selected['x_min'].min()
        x_max = df_selected['x_max'].max()
        y_min = df_selected['y_min'].min()
        y_max = df_selected['y_max'].max()
        
        # Add padding
        padding = max((x_max - x_min) * 0.1, (y_max - y_min) * 0.1, 10)
        x_min -= padding
        x_max += padding
        y_min -= padding
        y_max += padding
        
        # Create thumbnail
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_max, y_min)  # Inverted for image coordinates
        
        # Draw bounding boxes
        for _, row in df_selected.iterrows():
            rect = patches.Rectangle(
                (row['x_min'], row['y_min']),
                row['x_max'] - row['x_min'],
                row['y_max'] - row['y_min'],
                linewidth=1,
                edgecolor='r',
                facecolor='none'
            )
            ax.add_patch(rect)
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')
        
        fig.canvas.draw()
        thumb = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        
        return thumb
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

def load_image_from_url(url):
    """Load image from URL and return as numpy array"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        return np.array(img)
    except Exception as e:
        print(f"Error loading image from {url}: {e}")
        return None

def open_image_in_browser(url):
    """Open image URL in default browser"""
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening URL in browser: {e}")
        messagebox.showerror("Error", f"Could not open image URL: {e}")

def apply_global_settings():
    """Apply the global settings to the plotting functionality"""
    global labels_enabled, show_background_image
    
    # Apply performance settings
    if 'real_time_hover' in global_settings:
        labels_enabled[0] = global_settings['real_time_hover']
        print(f"✓ Labels enabled set to: {labels_enabled[0]} (from settings: {global_settings['real_time_hover']})")
    else:
        print(f"⚠ 'real_time_hover' not found in global_settings. Available keys: {list(global_settings.keys())}")
    
    if 'show_background_images' in global_settings:
        show_background_image[0] = global_settings['show_background_images']
    
    # Apply other settings as needed
    print(f"✓ Applied performance settings: {global_settings.get('performance_mode', 'balanced')}")
    print(f"✓ Current labels_enabled state: {labels_enabled[0]}")

def highlight_thumbnail(index):
    """Highlights the thumbnail at the given index and un-highlights others."""
    for i, ax in enumerate(thumb_axes):
        if i == index:
            ax.spines['bottom'].set_color('blue')
            ax.spines['top'].set_color('blue')
            ax.spines['right'].set_color('blue')
            ax.spines['left'].set_color('blue')
            ax.spines['bottom'].set_linewidth(3)
            ax.spines['top'].set_linewidth(3)
            ax.spines['right'].set_linewidth(3)
            ax.spines['left'].set_linewidth(3)
        else:
            ax.spines['bottom'].set_color('black')
            ax.spines['top'].set_color('black')
            ax.spines['right'].set_color('black')
            ax.spines['left'].set_color('black')
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['top'].set_linewidth(1)
            ax.spines['right'].set_linewidth(1)
            ax.spines['left'].set_linewidth(1)

def update_thumbnail_visibility():
    """Update which thumbnails are visible and center them"""
    global nav_text
    thumb_bbox = thumb_container_ax.get_position()
    
    # Show all thumbnails in a grid layout
    # Strictly limit to maximum 15 thumbnails for consistent layout
    total_thumbs = len(image_ids)
    current_idx = current_image_idx[0]
    max_visible_thumbs = 15  # Fixed maximum for consistent layout
    
    # Calculate how many thumbnails to show around the current one
    half_visible = max_visible_thumbs // 2
    start_idx = max(0, current_idx - half_visible)
    end_idx = min(total_thumbs, start_idx + max_visible_thumbs)
    
    # Adjust start_idx if we're near the end
    if end_idx - start_idx < max_visible_thumbs and start_idx > 0:
        start_idx = max(0, end_idx - max_visible_thumbs)
    
    num_visible = end_idx - start_idx
    if num_visible == 0:
        return
    
    # Fixed thumbnail size and padding (in figure coordinates)
    # These values ensure consistent thumbnail sizing regardless of plot area
    # Users can adjust these values in the settings if needed
    fixed_thumb_width = global_settings.get('thumbnail_width', 0.05)  # Fixed width for each thumbnail (5% of figure width)
    fixed_padding = global_settings.get('thumbnail_padding', 0.008)  # Fixed padding between thumbnails (0.8% of figure width)
    
    # Ensure we can fit exactly 15 thumbnails with comfortable spacing
    # Calculate if we need to adjust sizing for the maximum case
    if num_visible == 15:
        # For exactly 15 thumbnails, ensure they fit with some margin
        total_needed = (fixed_thumb_width * 15) + (fixed_padding * 14)
        if total_needed > 0.9:  # If we need more than 90% of available width
            # Reduce thumbnail width proportionally
            scale_factor = 0.9 / total_needed
            fixed_thumb_width *= scale_factor
            fixed_padding *= scale_factor
    
    # Calculate total width needed for visible thumbnails
    total_thumb_width = fixed_thumb_width * num_visible
    total_padding = fixed_padding * (num_visible - 1)
    total_width_needed = total_thumb_width + total_padding
    
    # Add margin on both sides to prevent boundary breaking
    side_margin = 0.02  # 2% margin on each side
    available_width = thumb_bbox.width - (2 * side_margin)
    
    # Ensure we don't exceed available width
    if total_width_needed > available_width:
        # Reduce padding further if needed
        excess_width = total_width_needed - available_width
        if num_visible > 1:
            padding_reduction = excess_width / (num_visible - 1)
            fixed_padding = max(0.002, fixed_padding - padding_reduction)  # Keep minimum padding
            # Recalculate total width
            total_padding = fixed_padding * (num_visible - 1)
            total_width_needed = total_thumb_width + total_padding
    
    # Center the visible thumbnails with side margins
    start_x = thumb_bbox.x0 + side_margin + (available_width - total_width_needed) / 2
    
    for i, ax in enumerate(thumb_axes):
        if start_idx <= i < end_idx:
            ax.set_visible(True)
            visible_idx = i - start_idx
            ax.set_position([start_x + visible_idx * (fixed_thumb_width + fixed_padding),
                             thumb_bbox.y0,
                             fixed_thumb_width,
                             thumb_bbox.height])
        else:
            ax.set_visible(False)
    
    # Update dataset progress text with dynamic sizing
    if nav_text:
        if total_thumbs > 20:
            # Show percentage for datasets with more than 20 images
            progress_percent = (current_idx + 1) / total_thumbs * 100
            nav_text.set_text(f'Dataset Progress: {progress_percent:.1f}% ({current_idx + 1}/{total_thumbs})')
        else:
            # Show simple progress for smaller datasets
            nav_text.set_text(f'Dataset Progress: {current_idx + 1}/{total_thumbs}')
        
        # Ensure the text is visible
        nav_text.set_visible(True)
        
        # Dynamically resize the text box to fit the content
        try:
            # Get the current text and calculate approximate width needed
            text_content = nav_text.get_text()
            # Estimate width based on text length and font size
            estimated_width = len(text_content) * 0.6  # Approximate character width
            # Ensure minimum and maximum widths
            estimated_width = max(0.3, min(estimated_width, 0.8))
            
            # Get current position and update width
            current_pos = nav_text.get_position()
            current_bbox = nav_text.get_bbox_patch()
            if current_bbox:
                # Update the bbox width to fit the text
                current_bbox.set_width(estimated_width)
                # Center the text box
                nav_text.set_position((0.5, current_pos[1]))
        except Exception as e:
            print(f"⚠ Error resizing dataset progress text box: {e}")
    
    # Update navigation arrows visibility
    try:
        # Get references to the navigation arrows
        left_arrow = None
        right_arrow = None
        for text_obj in thumb_container_ax.texts:
            if text_obj.get_text() == '◀':
                left_arrow = text_obj
            elif text_obj.get_text() == '▶':
                right_arrow = text_obj
        
        # Show/hide arrows based on thumbnail visibility
        if left_arrow:
            left_arrow.set_visible(start_idx > 0)
        if right_arrow:
            right_arrow.set_visible(end_idx < total_thumbs)
                
    except Exception as e:
        print(f"⚠ Error updating navigation arrows: {e}")
    
    fig.canvas.draw_idle()

def draw_main_plot(idx):
    try:
        main_ax.clear()
        img_id = image_ids[idx]
        df_selected = df[df['image_id'] == img_id].copy()
        
        # Get the annotation state early to avoid scope issues
        state = annotation_states[img_id]
        
        if df_selected.empty or df_selected['x_min'].isna().all():
            main_ax.text(0.5, 0.5, "No bounding box data available", 
                         ha='center', va='center', transform=main_ax.transAxes, fontsize=12)
            main_ax.set_title(f'Bounding Boxes for image_id: {img_id}')
            main_ax.set_xticks([])
            main_ax.set_yticks([])
            fig.canvas.draw_idle()
            return

        df_selected['width'] = df_selected['x_max'] - df_selected['x_min']
        df_selected['height'] = df_selected['y_max'] - df_selected['y_min']
        df_selected['area'] = df_selected['width'] * df_selected['height']
        df_selected['center_x'] = (df_selected['x_min'] + df_selected['x_max']) / 2
        df_selected['center_y'] = (df_selected['y_min'] + df_selected['y_max']) / 2
        for _, row in df_selected.iterrows():
            rect = patches.Rectangle(
                (row['x_min'], row['y_min']),
                row['width'],
                row['height'],
                linewidth=1,
                edgecolor='r',
                facecolor='none',
                zorder=1  # Low z-order so markers appear on top
            )
            main_ax.add_patch(rect)
        
        x_min_all = df_selected['x_min'].min() if not df_selected['x_min'].isnull().all() else 0
        x_max_all = df_selected['x_max'].max() if not df_selected['x_max'].isnull().all() else 100
        y_min_all = df_selected['y_min'].min() if not df_selected['y_min'].isnull().all() else 0
        y_max_all = df_selected['y_max'].max() if not df_selected['y_max'].isnull().all() else 100

        # Set axis limits
        main_ax.set_xlim(x_min_all - 10, x_max_all + 10)
        
        # Apply Y-axis flip if enabled
        if y_axis_flipped[0]:
            main_ax.set_ylim(y_max_all + 10, y_min_all - 10)
        else:
            main_ax.set_ylim(y_min_all - 10, y_max_all + 10)
        
        # Add background image if enabled and available
        if show_background_image[0] and state.image_url:
            try:
                # Load image if not already loaded
                if state.image_url not in loaded_images:
                    img_array = load_image_from_url(state.image_url)
                    if img_array is not None:
                        loaded_images[state.image_url] = img_array
                    else:
                        print(f"Could not load image from {state.image_url}")
                        loaded_images[state.image_url] = None
                
                # Display background image
                if loaded_images.get(state.image_url) is not None:
                    img_array = loaded_images[state.image_url]
                    # Invert y-axis for image display (matplotlib vs image coordinates)
                    main_ax.imshow(img_array, extent=[x_min_all - 10, x_max_all + 10, y_min_all - 10, y_max_all + 10], 
                                 alpha=0.7, zorder=0)
                    main_ax.set_title(f'Bounding Boxes for image_id: {img_id} (with background image)')
                else:
                    main_ax.set_title(f'Bounding Boxes for image_id: {img_id}')
            except Exception as e:
                print(f"Error displaying background image: {e}")
                main_ax.set_title(f'Bounding Boxes for image_id: {img_id}')
        else:
            main_ax.set_title(f'Bounding Boxes for image_id: {img_id}')
        
        main_ax.set_xlabel('X')
        main_ax.set_ylabel('Y')
        
        # Synchronize radio button with current state mode
        if radio.value_selected != state.mode:
            radio.set_active(0 if state.mode == 'x' else 1)
        
        # Clear existing markers safely
        for marker, *_ in getattr(state, 'markers', []):
            try:
                if marker and marker in main_ax.get_children():
                    marker.remove()
            except (NotImplementedError, ValueError):
                pass  # Ignore errors when removing already removed artists
        state.markers.clear()
        
        # Clear hover text safely
        if state.hover_text:
            try:
                if state.hover_text in main_ax.get_children():
                    state.hover_text.remove()
            except (NotImplementedError, ValueError):
                pass
            state.hover_text = None
        
        # Draw existing annotations (only for new annotations, not existing CSV marks)
        for ann in state.annotations:
            x, y = ann['x'], ann['y']
            mark_value = ann.get('mark_value', '')
            
            # Check if this annotation corresponds to an existing CSV mark
            # If so, skip drawing it to avoid duplicates
            skip_drawing = False
            if 'marked' in df.columns:
                for _, row in df_selected.iterrows():
                    if (row['x_min'] <= x <= row['x_max'] and 
                        row['y_min'] <= y <= row['y_max']):
                        existing_mark = str(row.get('marked', '')).strip()
                        if existing_mark and existing_mark.lower() != 'nan' and existing_mark.lower() != '':
                            skip_drawing = True
                            break
            
            if not skip_drawing:
                if state.mode == 'number' and str(mark_value).isdigit():
                    marker, = main_ax.plot(x, y, marker=f'${mark_value}$', color='red', markersize=14, mew=2)
                else:
                    marker, = main_ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
                label_text = ', '.join(str(ann.get(label_col, '')) for label_col in label_columns)
                state.markers.append((marker, label_text, x, y, mark_value))
        
        # Draw existing marks from CSV 'marked' column
        if 'marked' in df.columns:
            for _, row in df_selected.iterrows():
                marked_value = str(row.get('marked', '')).strip()
                if marked_value and marked_value.lower() != 'nan' and marked_value.lower() != '':
                    x, y = (row['x_min'] + row['x_max']) / 2, (row['y_min'] + row['y_max']) / 2
                    
                    # Convert "yes" to "x" for display
                    if marked_value.lower() == 'yes':
                        display_value = 'x'
                        marker_color = 'green'  # Different color for existing "yes" marks
                        marker_size = 12
                        # Display as X marker with high z-order
                        marker, = main_ax.plot(x, y, marker='x', color=marker_color, markersize=marker_size, mew=2, zorder=10)
                    else:
                        display_value = marked_value
                        marker_color = 'purple'  # Different color for other existing marks
                        # Display as text (no X marker) with high z-order
                        marker = main_ax.text(x, y, display_value, color=marker_color, fontsize=12, 
                                            ha='center', va='center', weight='bold', zorder=10)
                    
                    # Add to markers list for hover functionality
                    label_text = ', '.join(str(row.get(label_col, '')) for label_col in label_columns)
                    state.markers.append((marker, label_text, x, y, marked_value))
            
        highlight_thumbnail(idx)
        fig.canvas.draw_idle()
    except Exception as e:
        print(f"Error in draw_main_plot: {e}")
        # Try to recover by redrawing
        try:
            main_ax.clear()
            main_ax.text(0.5, 0.5, f"Error displaying plot: {e}", 
                         ha='center', va='center', transform=main_ax.transAxes, fontsize=10, color='red')
            fig.canvas.draw_idle()
        except:
            pass

class BoundingBoxPlotter:
    """Main plotting class for bounding box visualization"""
    
    def __init__(self):
        # Initialize all the global variables
        self.df = None
        self.output_dir = None
        self.image_ids = []
        self.annotation_states = {}
        self.thumbnails = []
        self.thumb_axes = []
        self.current_image_idx = [0]
        self.label_columns = []
        self.image_url_columns = []
        self.loaded_images = {}
        self.labels_enabled = [True]
        self.show_background_image = [False]
        self.y_axis_flipped = [True]
        
        # UI components
        self.nav_text = None
        self.help_text_box = None
        self.btn_help = None
        self.btn_website = None
        
        # Global flags for preventing duplicate operations
        self._save_popup_showing = False
        self._close_operation_in_progress = False
        
        # Global settings (default values, will be updated by SettingsManager)
        self.global_settings = {
            'show_background_images': False,
            'high_quality_thumbnails': True,
            'real_time_hover': True,
            'smooth_animations': False,
            'anti_aliasing': True,
            'progressive_loading': False,
            'image_caching': True,
            'aggressive_cleanup': False,
            'disable_background_image_button': False,
            'save_plots_on_close': True,
            'log_retention': 7, # Days
            'enable_debug_logging': False,
            'thumbnail_width': 200,
            'thumbnail_padding': 5
        }
        
        # Matplotlib components
        self.fig = None
        self.main_ax = None
        self.controls_ax = None
        self.thumb_container_ax = None
        
        # Control buttons
        self.btn_reset = None
        self.btn_undo = None
        self.btn_redo = None
        self.btn_clear = None
        self.btn_save = None
        self.btn_close = None
        self.btn_mode = None
        self.btn_toggle_labels = None
        self.btn_open_image = None
        self.btn_toggle_background = None
        self.btn_flip_y = None
        
        # Progress management
        self.progress_manager = None
    
    def apply_global_settings(self):
        """Apply global settings to the application"""
        try:
            # Apply settings to matplotlib
            if self.global_settings.get('anti_aliasing', True):
                plt.rcParams['font.antialiased'] = True
                plt.rcParams['axes.antialiased'] = True
                plt.rcParams['lines.antialiased'] = True
            
            # Apply image caching setting
            if self.global_settings.get('image_caching', True):
                logger.info("Image caching enabled for better performance")
            
            logger.info("Global settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying global settings: {e}")
            # Continue without failing if matplotlib settings can't be applied
