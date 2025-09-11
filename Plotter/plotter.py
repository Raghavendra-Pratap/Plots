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
    
    def setup_logging(self):
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
    
    def apply_global_settings(self):
        """Apply global settings to the application"""
        try:
            # Apply settings to matplotlib
            if self.global_settings.get('anti_aliasing', True):
                plt.rcParams['axes.antialiased'] = True
                plt.rcParams['lines.antialiased'] = True
            
            # Apply image caching setting
            if self.global_settings.get('image_caching', True):
                logger.info("Image caching enabled for better performance")
            
            logger.info("Global settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying global settings: {e}")
            # Continue without failing if matplotlib settings can't be applied
    
    def process_csv_file(self, file_path):
        """Process a CSV file and create the plotting interface"""
        global df, output_dir, image_ids, annotation_states, thumbnails, thumb_axes, current_image_idx, label_columns, image_url_columns
        
        logger.info(f"Starting CSV processing: {file_path}")
        
        # Set output directory to input file's directory
        output_dir = os.path.dirname(file_path)
        logger.info(f"Input file directory: {output_dir}")
        print(f"✓ Input file directory: {output_dir}")
        
        try:
            # Load CSV data
            logger.info("Loading CSV data...")
            df = pd.read_csv(file_path)
            logger.info(f"CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")
            print(f"✓ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Validate CSV columns
            required_columns = ['image_id', 'x_min', 'x_max', 'y_min', 'y_max']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                error_message = f"""The selected CSV file is missing required columns for bounding box visualization.

Missing columns: {', '.join(missing_columns)}

Required columns:
• image_id - Unique identifier for each image
• x_min - Left boundary of bounding box
• x_max - Right boundary of bounding box
• y_min - Top boundary of bounding box
• y_max - Bottom boundary of bounding box

Please ensure your CSV file contains these columns and try again.

File: {os.path.basename(file_path)}"""
                
                messagebox.showerror("Invalid CSV File", error_message)
                return False
            
            # Ensure bounding box columns are numeric
            df['x_min'] = pd.to_numeric(df['x_min'], errors='coerce')
            df['x_max'] = pd.to_numeric(df['x_max'], errors='coerce')
            df['y_min'] = pd.to_numeric(df['y_min'], errors='coerce')
            df['y_max'] = pd.to_numeric(df['y_max'], errors='coerce')
            
            # Add a 'marked' column to the DataFrame
            if 'marked' not in df.columns:
                df['marked'] = ''
            
            # Find all label columns
            label_columns = [col for col in df.columns if col.startswith('label_')]
            logger.info(f"Detected label columns: {label_columns}")
            print(f"✓ Detected label columns: {label_columns}")
            
            # Detect image URL columns
            image_url_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['url', 'link', 'image', 'img', 'src']):
                    sample_values = df[col].dropna().head(10)
                    if len(sample_values) > 0:
                        url_count = sum(1 for val in sample_values if str(val).startswith(('http://', 'https://', 'www.')))
                        if url_count > 0:
                            image_url_columns.append(col)
            
            logger.info(f"Detected image URL columns: {image_url_columns}")
            print(f"✓ Detected image URL columns: {image_url_columns}")
            
            # Apply settings
            apply_global_settings()
            
            # Prepare per-image annotation state
            df['image_id'] = df['image_id'].astype(str)
            image_ids = list(df['image_id'].unique())
            annotation_states = {img_id: AnnotationState() for img_id in image_ids}
            logger.info(f"Created annotation states for {len(image_ids)} unique images")
            
            # Store image URLs for each image_id
            for img_id in image_ids:
                df_sel = df[df['image_id'] == img_id]
                if not df_sel.empty and image_url_columns:
                    for url_col in image_url_columns:
                        url = df_sel[url_col].dropna().iloc[0] if not df_sel[url_col].dropna().empty else None
                        if url:
                            annotation_states[img_id].image_url = url
                            break
            
            # Pre-populate annotation states from 'marked' column
            if 'marked' in df.columns:
                for img_id in image_ids:
                    state = annotation_states[img_id]
                    df_sel = df[df['image_id'] == img_id]
                    for idx, row in df_sel.iterrows():
                        mark_val = str(row['marked']).strip()
                        if mark_val and mark_val.lower() != 'nan' and mark_val.lower() != 'yes':
                            try:
                                ann = {'image_id': img_id, 'x': (row['x_min'] + row['x_max']) / 2, 'y': (row['y_min'] + row['y_max']) / 2}
                                if mark_val.isdigit():
                                    ann['mark_value'] = mark_val
                                else:
                                    ann['mark_value'] = 'x'
                                for label_col in [col for col in df.columns if col.startswith('label_')]:
                                    ann[label_col] = row[label_col]
                                state.annotations.append(ann)
                            except Exception as e:
                                logger.warning(f"Could not process existing annotation for row {idx}: {e}")
                        elif mark_val and mark_val.lower() == 'yes':
                            try:
                                ann = {'image_id': img_id, 'x': (row['x_min'] + row['x_max']) / 2, 'y': (row['y_min'] + row['y_max']) / 2, 'mark_value': 'x'}
                                for label_col in [col for col in df.columns if col.startswith('label_')]:
                                    ann[label_col] = row[label_col]
                                state.annotations.append(ann)
                            except Exception as e:
                                logger.warning(f"Could not process existing annotation for row {idx}: {e}")
            
            # Create the plotting interface
            logger.info("Creating plotting interface...")
            self.create_plotting_interface()
            
            logger.info("CSV processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            error_message = f"""Could not load the CSV file. Please check that:

• The file exists and is accessible
• The file is a valid CSV format
• You have permission to read the file
• The file is not corrupted

Error details: {str(e)}

File: {os.path.basename(file_path)}"""
            
            messagebox.showerror("Error Loading CSV", error_message)
            return False
    
    def create_plotting_interface(self):
        """Create the main plotting interface with matplotlib"""
        global fig, main_ax, controls_ax, thumb_container_ax, thumb_axes, current_image_idx, nav_text, btn_help, btn_website
        
        # Get screen size for dynamic sizing
        try:
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
        except Exception as e:
            print(f"Warning: Could not get screen size: {e}")
            screen_width = 1920
            screen_height = 1080
        
        # Calculate figure size based on screen size (80% of screen)
        fig_width = int(screen_width * 0.8 / 100)
        fig_height = int(screen_height * 0.8 / 100)
        
        # Ensure minimum and maximum sizes
        fig_width = max(12, min(fig_width, 24))
        fig_height = max(8, min(fig_height, 16))
        
        # Create figure
        try:
            fig = plt.figure(figsize=(fig_width, fig_height))
            print("✓ Main figure created successfully")
        except Exception as e:
            print(f"✗ Error creating main figure: {e}")
            fig = plt.figure(figsize=(16, 12))
        
        # Set the window title
        try:
            if hasattr(fig.canvas, 'manager') and hasattr(fig.canvas.manager, 'set_window_title'):
                fig.canvas.manager.set_window_title("Unified Plotter - Professional Bounding Box Visualization")
            elif hasattr(fig.canvas, 'set_window_title'):
                fig.canvas.set_window_title("Unified Plotter - Professional Bounding Box Visualization")
            print("✓ Window title set successfully")
        except Exception as e:
            print(f"Warning: Could not set window title: {e}")
        
        # Create GridSpec and axes
        try:
            gs = gridspec.GridSpec(3, 2, width_ratios=[5, 1], height_ratios=[10, 0, 3.5], wspace=0.15, hspace=0.1)
            main_ax = fig.add_subplot(gs[0, 0])
            main_ax.set_zorder(1000)
            controls_ax = fig.add_subplot(gs[0, 1])
            controls_ax.axis('off')
            thumb_container_ax = fig.add_subplot(gs[2, :])
            thumb_container_ax.axis('off')
            print("✓ Main axes created successfully")
        except Exception as e:
            print(f"✗ Error creating main axes: {e}")
            return False
        
        # Generate thumbnails
        thumbnails = []
        print("Creating thumbnails...")
        for i, img_id in enumerate(image_ids):
            try:
                df_selected = df[df['image_id'] == img_id].copy()
                if not df_selected.empty:
                    thumb = generate_thumbnail(df_selected)
                    if thumb is not None:
                        thumbnails.append(thumb)
                    else:
                        # Create a blank thumbnail as fallback
                        fig_thumb, ax_thumb = plt.subplots(figsize=(2, 2))
                        ax_thumb.axis('off')
                        fig_thumb.canvas.draw()
                        blank_thumb = np.array(fig_thumb.canvas.renderer.buffer_rgba())
                        plt.close(fig_thumb)
                        thumbnails.append(blank_thumb)
                else:
                    # Create a blank thumbnail as fallback
                    fig_thumb, ax_thumb = plt.subplots(figsize=(2, 2))
                    ax_thumb.axis('off')
                    fig_thumb.canvas.draw()
                    blank_thumb = np.array(fig_thumb.canvas.renderer.buffer_rgba())
                    plt.close(fig_thumb)
                    thumbnails.append(blank_thumb)
                
                if (i + 1) % 10 == 0:
                    print(f"  Created {i + 1}/{len(image_ids)} thumbnails")
                    
            except Exception as e:
                print(f"✗ Error creating thumbnail for {img_id}: {e}")
                thumbnails.append(np.zeros((200, 200, 4), dtype=np.uint8))
        
        print(f"✓ Created {len(thumbnails)} thumbnails")
        
        # Create thumbnail axes
        thumb_axes = []
        print("Creating thumbnail axes...")
        for i in range(len(image_ids)):
            try:
                ax = fig.add_axes([0, 0, 1, 1], frameon=True)
                ax.imshow(thumbnails[i])
                ax.set_title(f'{image_ids[i]}', fontsize=8, y=-0.35)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_frame_on(True)
                ax.set_aspect('equal')
                thumb_axes.append(ax)
            except Exception as e:
                print(f"✗ Error creating thumbnail axis {i}: {e}")
                ax = fig.add_axes([0, 0, 1, 1], frameon=True)
                ax.axis('off')
                ax.set_aspect('equal')
                thumb_axes.append(ax)
        
        print(f"✓ Created {len(thumb_axes)} thumbnail axes")
        
        # Add dataset progress text
        try:
            initial_text = f'Dataset Progress: 1/{len(image_ids)}'
            nav_text = thumb_container_ax.text(0.5, -0.05, initial_text, 
                                              ha='center', va='center', fontsize=12, 
                                              bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.5'))
            print("✓ Dataset progress text created successfully")
        except Exception as e:
            print(f"✗ Error creating dataset progress text: {e}")
            initial_text = f'Dataset Progress: 1/{len(image_ids)}'
            nav_text = thumb_container_ax.text(0.5, -0.05, initial_text, 
                                              ha='center', va='center', fontsize=12)
        
        # Add help button
        try:
            help_button_ax = fig.add_axes([0.95, 0.02, 0.03, 0.03])
            help_button_ax.set_zorder(100)
            btn_help = Button(help_button_ax, '?', color='white', hovercolor='lightgray')
            print("✓ Help button created successfully")
        except Exception as e:
            print(f"⚠ Could not create help button: {e}")
            btn_help = None
        
        # Add navigation arrows
        try:
            left_arrow = thumb_container_ax.text(0.02, 0.5, '◀', ha='center', va='center', fontsize=16, 
                                               color='gray', alpha=0.7, fontweight='bold')
            right_arrow = thumb_container_ax.text(0.98, 0.5, '▶', ha='center', va='center', fontsize=16, 
                                                color='gray', alpha=0.7, fontweight='bold')
            print("✓ Navigation arrows created successfully")
        except Exception as e:
            print(f"⚠ Could not create navigation arrows: {e}")
        
        # Create control buttons
        self.create_control_buttons()
        
        # Connect events
        self.connect_events()
        
        # Start the interface
        try:
            update_thumbnail_visibility()
            draw_main_plot(current_image_idx[0])
            print("✓ All components initialized successfully")
            print("✓ Starting plotter...")
            plt.show()
        except Exception as e:
            print(f"✗ Error during final initialization: {e}")
            return False
        
        return True
    
    def create_control_buttons(self):
        """Create all the control widgets and buttons"""
        global radio, btn_reset, btn_undo, btn_redo, btn_clear, btn_flip_y, btn_save, btn_toggle_labels, btn_close, btn_show_bg
        
        # Get control panel layout
        bbox = controls_ax.get_position()
        left, bottom, width, height = bbox.x0, bbox.y0, bbox.width, bbox.height
        
        # Create all buttons
        try:
            ax_mode = fig.add_axes([left + 0.02*width, bottom + 0.80*height, 0.9*width, 0.15*height])
            ax_mode.set_zorder(100)
            radio = RadioButtons(ax_mode, ('x', 'number'))
            ax_mode.set_title('Marking Mode')
            print("✓ Mode radio buttons created")
        except Exception as e:
            print(f"✗ Error creating mode radio buttons: {e}")
            return False
        
        try:
            ax_reset = fig.add_axes([left + 0.02*width, bottom + 0.71*height, 0.9*width, 0.07*height])
            ax_reset.set_zorder(100)
            btn_reset = Button(ax_reset, 'Reset Counter')
            print("✓ Reset button created")
        except Exception as e:
            print(f"✗ Error creating reset button: {e}")
            return False
        
        try:
            ax_undo = fig.add_axes([left + 0.02*width, bottom + 0.61*height, 0.9*width, 0.07*height])
            ax_undo.set_zorder(100)
            btn_undo = Button(ax_undo, 'Undo')
            print("✓ Undo button created")
        except Exception as e:
            print(f"✗ Error creating undo button: {e}")
            return False
        
        try:
            ax_redo = fig.add_axes([left + 0.02*width, bottom + 0.52*height, 0.9*width, 0.07*height])
            ax_redo.set_zorder(100)
            btn_redo = Button(ax_redo, 'Redo')
            print("✓ Redo button created")
        except Exception as e:
            print(f"✗ Error creating redo button: {e}")
            return False
        
        try:
            ax_clear = fig.add_axes([left + 0.02*width, bottom + 0.43*height, 0.9*width, 0.07*height])
            ax_clear.set_zorder(100)
            btn_clear = Button(ax_clear, 'Clear All')
            print("✓ Clear button created")
        except Exception as e:
            print(f"✗ Error creating clear button: {e}")
            return False
        
        try:
            ax_flip_y = fig.add_axes([left + 0.02*width, bottom + 0.34*height, 0.9*width, 0.07*height])
            ax_flip_y.set_zorder(100)
            btn_flip_y = Button(ax_flip_y, 'Unflip Y-axis')
            print("✓ Flip Y-axis button created")
        except Exception as e:
            print(f"✗ Error creating flip Y-axis button: {e}")
            return False
        
        try:
            ax_save = fig.add_axes([left + 0.02*width, bottom + 0.25*height, 0.9*width, 0.07*height])
            ax_save.set_zorder(100)
            btn_save = Button(ax_save, 'Save')
            print("✓ Save button created")
        except Exception as e:
            print(f"✗ Error creating save button: {e}")
            return False
        
        try:
            ax_toggle_labels = fig.add_axes([left + 0.02*width, bottom + 0.16*height, 0.9*width, 0.07*height])
            ax_toggle_labels.set_zorder(100)
            btn_toggle_labels = Button(ax_toggle_labels, 'Disable Labels')
            print("✓ Toggle labels button created")
        except Exception as e:
            print(f"✗ Error creating toggle labels button: {e}")
            return False
        
        try:
            ax_open_image = fig.add_axes([left + 0.02*width, bottom + 0.07*height, 0.9*width, 0.07*height])
            ax_open_image.set_zorder(100)
            btn_open_image = Button(ax_open_image, 'Open Image')
            print("✓ Open Image button created")
        except Exception as e:
            print(f"✗ Error creating open image button: {e}")
            return False
        
        try:
            ax_close = fig.add_axes([left + 0.02*width, bottom - 0.02*height, 0.9*width, 0.07*height])
            ax_close.set_zorder(100)
            btn_close = Button(ax_close, 'Close')
            print("✓ Close button created")
        except Exception as e:
            print(f"✗ Error creating close button: {e}")
            return False
        
        return True
    
    def connect_events(self):
        """Connect all the events and button callbacks"""
        # Connect all events to the main figure
        fig.canvas.mpl_connect('button_press_event', self.onclick_main)
        fig.canvas.mpl_connect('motion_notify_event', self.on_motion_main)
        fig.canvas.mpl_connect('resize_event', self.on_resize)
        fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Connect button events
        if radio:
            radio.on_clicked(self.on_mode)
        if btn_reset:
            btn_reset.on_clicked(self.on_reset)
        if btn_undo:
            btn_undo.on_clicked(self.on_undo)
        if btn_redo:
            btn_redo.on_clicked(self.on_redo)
        if btn_clear:
            btn_clear.on_clicked(self.on_clear)
        if btn_save:
            btn_save.on_clicked(self.save_annotations)
        if btn_toggle_labels:
            btn_toggle_labels.on_clicked(self.on_toggle_labels)
        if btn_flip_y:
            btn_flip_y.on_clicked(self.on_flip_y)
        if btn_open_image:
            btn_open_image.on_clicked(self.on_open_image)
        if btn_close:
            btn_close.on_clicked(self.return_to_welcome)
        if btn_help:
            btn_help.on_clicked(self.show_help)
        
        print("✓ All events connected successfully")
    
    def onclick_main(self, event):
        """Handle mouse clicks on the main plot"""
        if event.button != 1:  # Only handle left clicks
            return
        
        # Handle thumbnail clicks
        for i, ax in enumerate(thumb_axes):
            if event.inaxes == ax:
                current_image_idx[0] = i
                draw_main_plot(i)
                update_thumbnail_visibility()
                return
        
        # Handle main plot clicks for annotations
        if event.inaxes != main_ax:
            return
        
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        df_selected = df[df['image_id'] == img_id].copy()
        state = annotation_states[img_id]
        x, y = event.xdata, event.ydata
        
        if df_selected.empty or df_selected['x_min'].isna().all():
            return
        
        # Find which bounding box was clicked
        clicked_bb_index = None
        for idx_row, row in df_selected.iterrows():
            if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
                clicked_bb_index = row.name
                break
        
        if clicked_bb_index is not None:
            row = df.loc[clicked_bb_index]
            
            # Check if this bounding box already has a mark
            existing_mark = str(row.get('marked', '')).strip()
            if existing_mark and existing_mark.lower() != 'nan' and existing_mark.lower() != '':
                print(f"⚠ Bounding box already marked as '{existing_mark}' - cannot add new annotation")
                return
            
            # Add new annotation
            annotation_entry = {'image_id': img_id, 'x': x, 'y': y}
            mark_value = ''
            
            if state.mode == 'number':
                mark_value = str(state.counter)
                df.loc[row.name, 'marked'] = mark_value
                annotation_entry['mark_value'] = mark_value
                state.counter += 1
                print(f"Added number annotation: {mark_value} at ({x:.1f}, {y:.1f})")
            else:
                mark_value = 'x'
                df.loc[row.name, 'marked'] = 'yes'
                annotation_entry['mark_value'] = mark_value
                print(f"Added X annotation at ({x:.1f}, {y:.1f})")
            
            for label_col in label_columns:
                annotation_entry[label_col] = row[label_col]
            
            state.annotations.append(annotation_entry)
            draw_main_plot(current_image_idx[0])
            state.undone.clear()
    
    def on_motion_main(self, event):
        """Handle mouse motion for hover effects"""
        if not labels_enabled[0]:
            return
        
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        df_selected = df[df['image_id'] == img_id].copy()
        
        if event.inaxes != main_ax:
            if state.hover_text:
                try:
                    state.hover_text.set_visible(False)
                    fig.canvas.draw_idle()
                except:
                    pass
            return
        
        if df_selected.empty or df_selected['x_min'].isna().all():
            return
        
        # Check if mouse is over a bounding box
        x, y = event.xdata, event.ydata
        hovered_bb = None
        
        for _, row in df_selected.iterrows():
            if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
                hovered_bb = row
                break
        
        if hovered_bb is not None:
            # Create hover text with professional styling - each label column gets its own row
            if label_columns:
                label_lines = []
                for label_col in label_columns:
                    value = str(hovered_bb.get(label_col, '')).strip()
                    if value and value.lower() != 'nan' and value != '':
                        # Remove "label_" prefix from column name for display
                        display_name = label_col.replace('label_', '')
                        label_lines.append(f"{display_name}: {value}")
                
                if label_lines:
                    label_text = '\n'.join(label_lines)
                    if state.hover_text:
                        state.hover_text.remove()
                    state.hover_text = main_ax.text(x, y, label_text, fontsize=9, 
                                                  bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                                                          edgecolor='gray', alpha=1.0, linewidth=1),
                                                  ha='left', va='bottom')
                    fig.canvas.draw_idle()
        else:
            if state.hover_text:
                try:
                    state.hover_text.set_visible(False)
                    fig.canvas.draw_idle()
                except:
                    pass
    
    def on_resize(self, event):
        """Handle window resize events"""
        try:
            update_thumbnail_visibility()
            print("✓ Thumbnail layout updated after resize")
        except Exception as e:
            print(f"⚠ Error updating thumbnails after resize: {e}")
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        try:
            # Navigation shortcuts
            if event.key == 'left' or event.key == 'a':
                current_image_idx[0] = max(0, current_image_idx[0] - 1)
                draw_main_plot(current_image_idx[0])
                update_thumbnail_visibility()
            elif event.key == 'right' or event.key == 'd':
                current_image_idx[0] = min(len(image_ids) - 1, current_image_idx[0] + 1)
                draw_main_plot(current_image_idx[0])
                update_thumbnail_visibility()
            elif event.key == 'home':
                current_image_idx[0] = 0
                draw_main_plot(current_image_idx[0])
                update_thumbnail_visibility()
            elif event.key == 'end':
                current_image_idx[0] = len(image_ids) - 1
                draw_main_plot(current_image_idx[0])
                update_thumbnail_visibility()
            
            # Mode and annotation shortcuts
            elif event.key == ' ' or event.key == 'space':
                # Toggle marking mode
                if radio:
                    current_mode = radio.value_selected
                    new_mode = 'number' if current_mode == 'x' else 'x'
                    radio.set_active(0 if new_mode == 'x' else 1)
                    self.on_mode(new_mode)
            elif event.key == 'r':
                self.on_reset(None)
            elif event.key == 'u' or (event.key == 'z' and 'ctrl' in str(event)):
                self.on_undo(None)
            elif event.key == 'y' and 'ctrl' in str(event):
                self.on_redo(None)
            elif event.key == 'c':
                self.on_clear(None)
            elif event.key == 'l':
                self.on_toggle_labels(None)
            elif event.key == 'f':
                self.on_flip_y(None)
            elif event.key == 's':
                self.save_annotations(None)
            elif event.key == 'o':
                self.on_open_image(None)
            elif event.key == 'h':
                self.show_help(None)
            elif event.key == 'escape':
                self.return_to_welcome(None)
                
        except Exception as e:
            print(f"⚠ Error in keyboard shortcuts: {e}")
    
    def on_mode(self, label):
        """Handle mode change"""
        for state in annotation_states.values():
            state.mode = label
        print(f"Mode changed to: {label}")
    
    def on_reset(self, event):
        """Reset annotation counter"""
        for state in annotation_states.values():
            state.counter = 1
        print("Annotation counter reset")
    
    def on_undo(self, event):
        """Undo last annotation"""
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        
        if state.annotations:
            last_annotation = state.annotations.pop()
            state.undone.append(last_annotation)
            draw_main_plot(idx)
            print("Undid last annotation")
    
    def on_redo(self, event):
        """Redo undone annotation"""
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        
        if state.undone:
            annotation = state.undone.pop()
            state.annotations.append(annotation)
            draw_main_plot(idx)
            print("Redid annotation")
    
    def on_clear(self, event):
        """Clear all annotations"""
        for state in annotation_states.values():
            state.annotations.clear()
            state.undone.clear()
        draw_main_plot(current_image_idx[0])
        print("Cleared all annotations")
    
    def on_toggle_labels(self, event):
        """Toggle hover labels"""
        labels_enabled[0] = not labels_enabled[0]
        btn_toggle_labels.label.set_text('Enable Labels' if labels_enabled[0] else 'Disable Labels')
        print(f"Labels {'enabled' if labels_enabled[0] else 'disabled'}")
    
    def on_flip_y(self, event):
        """Flip Y-axis"""
        y_axis_flipped[0] = not y_axis_flipped[0]
        btn_flip_y.label.set_text('Flip Y-axis' if y_axis_flipped[0] else 'Unflip Y-axis')
        draw_main_plot(current_image_idx[0])
        print(f"Y-axis {'flipped' if y_axis_flipped[0] else 'unflipped'}")
    
    def save_annotations(self, event=None):
        """Save annotations to CSV"""
        try:
            # Create output directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if output_dir is None:
                output_dir = os.path.join(os.getcwd(), f'plots_{timestamp}')
            else:
                output_dir = os.path.join(output_dir, f'plots_{timestamp}')
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the updated DataFrame
            output_file = os.path.join(output_dir, f'annotated_data_{timestamp}.csv')
            df.to_csv(output_file, index=False)
            print(f"✓ Annotations saved to: {output_file}")
            
            messagebox.showinfo("Success", f"Annotations saved to:\n{output_file}")
            
        except Exception as e:
            print(f"✗ Error saving annotations: {e}")
            messagebox.showerror("Error", f"Could not save annotations: {e}")
    
    def on_open_image(self, event):
        """Open current image in browser"""
        try:
            idx = current_image_idx[0]
            img_id = image_ids[idx]
            state = annotation_states[img_id]
            
            if state.image_url:
                open_image_in_browser(state.image_url)
                print(f"✓ Opened image {img_id} in browser: {state.image_url}")
            else:
                messagebox.showinfo("No Image URL", f"No image URL available for image {img_id}")
                print(f"⚠ No image URL available for image {img_id}")
        except Exception as e:
            print(f"✗ Error opening image: {e}")
            messagebox.showerror("Error", f"Could not open image: {e}")
    
    def show_help(self, event):
        """Show help dialog with keyboard shortcuts and usage instructions"""
        try:
            help_text = """
🎯 BOUNDING BOX PLOTTER - HELP & SHORTCUTS

📋 KEYBOARD SHORTCUTS:
• ← / A - Previous image
• → / D - Next image  
• Home - First image
• End - Last image
• Space - Toggle marking mode
• R - Reset counter
• U - Undo last annotation
• Ctrl+Z - Undo last annotation
• Ctrl+Y - Redo annotation
• C - Clear all annotations
• L - Toggle hover labels
• F - Flip Y-axis
• S - Save annotations
• O - Open current image in browser
• H - Show this help
• Esc - Close plotter

🖱️ MOUSE CONTROLS:
• Click on bounding box - Add annotation
• Click on thumbnail - Navigate to image
• Hover over bounding box - Show labels

🎨 ANNOTATION MODES:
• X Mode - Mark with 'X' symbol
• Number Mode - Mark with sequential numbers

💾 SAVING:
• Annotations are saved to CSV in the same directory as input file
• Output folder: plots_<timestamp>/
• File: annotated_data_<timestamp>.csv

🔧 TIPS:
• Use keyboard shortcuts for faster navigation
• Labels show AI, Heuristic, and Ground Truth classifications
• Background images can be enabled in settings
• All annotations are automatically saved when you close

Version: 2.0 | Professional Bounding Box Visualization
            """
            
            # Create help window
            help_window = tk.Tk()
            help_window.title("Plotter Help & Shortcuts")
            help_window.geometry("600x500")
            help_window.configure(bg='#2a2a2a')
            
            # Create text widget with scrollbar
            text_frame = tk.Frame(help_window, bg='#2a2a2a')
            text_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 10), 
                                bg='#2a2a2a', fg='white', padx=10, pady=10)
            scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            text_widget.insert('1.0', help_text)
            text_widget.config(state='disabled')
            
            # Add close button
            close_btn = tk.Button(help_window, text="Close Help", command=help_window.destroy,
                                font=('Helvetica', 12), bg='#4a4a4a', fg='white', 
                                padx=20, pady=5)
            close_btn.pack(pady=10)
            
            help_window.mainloop()
            print("✓ Help dialog shown")
            
        except Exception as e:
            print(f"✗ Error showing help: {e}")
            messagebox.showerror("Error", f"Could not show help: {e}")
    
    def return_to_welcome(self, event=None):
        """Return to welcome screen"""
        try:
            plt.close('all')
            print("✓ Returning to welcome screen...")
        except Exception as e:
            print(f"✗ Error returning to welcome screen: {e}")
