import sys
import subprocess
import importlib
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, RadioButtons, Slider
from matplotlib import gridspec
from matplotlib.transforms import Bbox
import numpy as np
import matplotlib
from matplotlib import image as mpimg
import webbrowser
import requests
from PIL import Image
import io

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        return False
    return True

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = {
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'requests': 'requests'
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name} is already installed")
        except ImportError:
            print(f"✗ {module_name} is not installed. Installing...")
            missing_packages.append((module_name, package_name))
    
    # Install missing packages
    for module_name, package_name in missing_packages:
        if install_package(package_name):
            print(f"✓ {module_name} installed successfully")
        else:
            print(f"✗ Failed to install {module_name}. Please install manually: pip install {package_name}")
            return False
    
    # Check tkinter (built-in on most systems)
    try:
        import tkinter
        print("✓ tkinter is available")
    except ImportError:
        print("✗ tkinter is not available. This may cause issues with file dialogs.")
        print("On some systems, you may need to install python3-tk package.")
    
    return True

# Check and install dependencies before importing
print("Checking dependencies...")
if not check_and_install_dependencies():
    print("Some dependencies could not be installed. Please install them manually and try again.")
    sys.exit(1)

print("All dependencies are ready!")

# Open file picker dialog
root = tk.Tk()
root.withdraw() # Hide the main window
file_path = filedialog.askopenfilename(
    title="Select CSV file",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)

if not file_path:
    print("No file selected. Exiting.")
    sys.exit()

# Set output directory to input file's directory
output_dir = os.path.dirname(file_path)
# Create a timestamped subfolder for all outputs
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = os.path.join(output_dir, f'plotts_{timestamp}')
os.makedirs(output_dir, exist_ok=True)

# Load your data
df = pd.read_csv(file_path)

# Ensure bounding box columns are numeric, coerce errors to NaN
df['x_min'] = pd.to_numeric(df['x_min'], errors='coerce')
df['x_max'] = pd.to_numeric(df['x_max'], errors='coerce')
df['y_min'] = pd.to_numeric(df['y_min'], errors='coerce')
df['y_max'] = pd.to_numeric(df['y_max'], errors='coerce')

# Create output directory for plots
os.makedirs(output_dir, exist_ok=True)

# Add a 'marked' column to the DataFrame, default to empty string
if 'marked' not in df.columns:
    df['marked'] = ''

# Find all label columns
label_columns = [col for col in df.columns if col.startswith('label_')]

# Detect image URL columns
image_url_columns = []
for col in df.columns:
    if any(keyword in col.lower() for keyword in ['url', 'link', 'image', 'img', 'src']):
        # Check if the column contains URLs
        sample_values = df[col].dropna().head(10)
        if len(sample_values) > 0:
            # Check if at least some values look like URLs
            url_count = sum(1 for val in sample_values if str(val).startswith(('http://', 'https://', 'www.')))
            if url_count > 0:
                image_url_columns.append(col)

print(f"Detected potential image URL columns: {image_url_columns}")

# Function to load image from URL
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

# Function to open image in browser
def open_image_in_browser(url):
    """Open image URL in default browser"""
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening URL in browser: {e}")
        messagebox.showerror("Error", f"Could not open image URL: {e}")

# Store loaded images
loaded_images = {}

# --- Annotation state for undo/redo/clear, per image_id ---
class AnnotationState:
    def __init__(self):
        self.annotations = []  # List of annotation_entry dicts
        self.markers = []      # List of (marker, label_text, x, y, mark_value)
        self.undone = []      # Stack for redo
        self.counter = 1
        self.mode = 'x'
        self.hover_text = None  # Store hover text per image
        self.image_url = None  # Store image URL for this image_id
    def reset(self):
        self.annotations.clear()
        self.markers.clear()
        self.undone.clear()
        self.counter = 1
        if self.hover_text:
            self.hover_text.remove()
            self.hover_text = None

# Prepare per-image annotation state
df['image_id'] = df['image_id'].astype(str)
image_ids = list(df['image_id'].unique())
annotation_states = {img_id: AnnotationState() for img_id in image_ids}

# Store image URLs for each image_id
for img_id in image_ids:
    df_sel = df[df['image_id'] == img_id]
    if not df_sel.empty and image_url_columns:
        # Get the first non-null URL from any image URL column
        for url_col in image_url_columns:
            url = df_sel[url_col].dropna().iloc[0] if not df_sel[url_col].dropna().empty else None
            if url:
                annotation_states[img_id].image_url = url
                break

# Pre-populate annotation states from 'marked' column if it exists
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
                        # Don't set mode here, let user control it
                    else:
                        ann['mark_value'] = 'x'
                        # Don't set mode here, let user control it
                    for label_col in [col for col in df.columns if col.startswith('label_')]:
                        ann[label_col] = row[label_col]
                    state.annotations.append(ann)
                except Exception as e:
                    print(f"Warning: Could not process existing annotation for row {idx}: {e}")
            elif mark_val and mark_val.lower() == 'yes':
                try:
                    ann = {'image_id': img_id, 'x': (row['x_min'] + row['x_max']) / 2, 'y': (row['y_min'] + row['y_max']) / 2, 'mark_value': 'x'}
                    for label_col in [col for col in df.columns if col.startswith('label_')]:
                        ann[label_col] = row[label_col]
                    state.annotations.append(ann)
                except Exception as e:
                    print(f"Warning: Could not process existing annotation for row {idx}: {e}")


# --- Generate thumbnails for each image ---
def generate_thumbnail(df_selected):
    # Skip if df_selected is empty or all bounding box columns are NaN
    if df_selected.empty or df_selected['x_min'].isna().all() or df_selected['x_max'].isna().all() or df_selected['y_min'].isna().all() or df_selected['y_max'].isna().all():
        print(f"[Warning] Skipping thumbnail: No valid bounding box data for image_id: {df_selected['image_id'].iloc[0] if not df_selected.empty else 'N/A'}")
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.axis('off')
        fig.canvas.draw()
        img = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        return img
    fig, ax = plt.subplots(figsize=(2, 2))
    for _, row in df_selected.dropna(subset=['x_min', 'x_max', 'y_min', 'y_max']).iterrows():
        rect = patches.Rectangle(
            (row['x_min'], row['y_min']),
            row['x_max'] - row['x_min'],
            row['y_max'] - row['y_min'],
            linewidth=1,
            edgecolor='r',
            facecolor='none'
        )
        ax.add_patch(rect)
    ax.set_xlim(df_selected['x_min'].min()-10, df_selected['x_max'].max()+10)
    ax.set_ylim(df_selected['y_min'].min()-10, df_selected['y_max'].max()+10)
    ax.axis('off')
    fig.canvas.draw()
    img = np.array(fig.canvas.renderer.buffer_rgba())
    plt.close(fig)
    return img

thumbnails = []
for img_id in image_ids:
    df_sel = df[df['image_id'] == img_id]
    thumbnails.append(generate_thumbnail(df_sel))

# --- Main interactive gallery ---
current_image_idx = [0]  # Mutable for inner functions

# Get screen size for dynamic sizing
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

# Calculate figure size based on screen size (80% of screen)
fig_width = int(screen_width * 0.8 / 100)
fig_height = int(screen_height * 0.8 / 100)

# Ensure minimum and maximum sizes
fig_width = max(12, min(fig_width, 24))
fig_height = max(8, min(fig_height, 16))

fig = plt.figure(figsize=(fig_width, fig_height))

# --- MODIFIED: Adjusted height_ratios and hspace for navigation display at bottom ---
gs = gridspec.GridSpec(3, 2, width_ratios=[1, 5], height_ratios=[10, 0, 3], wspace=0.15, hspace=0.1)

controls_ax = fig.add_subplot(gs[0, 0])
controls_ax.axis('off')
main_ax = fig.add_subplot(gs[0, 1])
thumb_container_ax = fig.add_subplot(gs[2, :])
thumb_container_ax.axis('off')

total_thumbs = len(image_ids)
slider = None  # No slider needed

thumb_axes = []
for i in range(total_thumbs):
    ax = fig.add_axes([0, 0, 1, 1], frameon=True) # Initially place them off-screen
    ax.imshow(thumbnails[i])
    ax.set_title(f'{image_ids[i]}', fontsize=7, y=-0.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(True) # Ensure frame is on for highlighting
    thumb_axes.append(ax)

# Add navigation text at the bottom
nav_text = thumb_container_ax.text(0.5, 0.1, f'Plot {current_image_idx[0]+1} of {total_thumbs}', 
                                  ha='center', va='center', fontsize=12, 
                                  bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.5'))

# --- Widget controls (now on the left) ---
bbox = controls_ax.get_position()
left, bottom, width, height = bbox.x0, bbox.y0, bbox.width, bbox.height
ax_mode = fig.add_axes([left + 0.02*width, bottom + 0.80*height, 0.9*width, 0.15*height])
radio = RadioButtons(ax_mode, ('x', 'number'))
ax_mode.set_title('Marking Mode')
ax_reset = fig.add_axes([left + 0.02*width, bottom + 0.71*height, 0.9*width, 0.07*height])
btn_reset = Button(ax_reset, 'Reset Counter')
ax_undo = fig.add_axes([left + 0.02*width, bottom + 0.61*height, 0.9*width, 0.07*height])
btn_undo = Button(ax_undo, 'Undo')
ax_redo = fig.add_axes([left + 0.02*width, bottom + 0.52*height, 0.9*width, 0.07*height])
btn_redo = Button(ax_redo, 'Redo')
ax_clear = fig.add_axes([left + 0.02*width, bottom + 0.43*height, 0.9*width, 0.07*height])
btn_clear = Button(ax_clear, 'Clear All')
ax_save = fig.add_axes([left + 0.02*width, bottom + 0.29*height, 0.9*width, 0.07*height])
btn_save = Button(ax_save, 'Save')
ax_toggle_labels = fig.add_axes([left + 0.02*width, bottom + 0.20*height, 0.9*width, 0.07*height])
btn_toggle_labels = Button(ax_toggle_labels, 'Disable Labels')

# Add image-related buttons if image URLs are available
image_buttons = []
if any(state.image_url for state in annotation_states.values()):
    # Position buttons below the existing ones with consistent spacing (0.10*height increments)
    ax_open_image = fig.add_axes([left + 0.02*width, bottom + 0.11*height, 0.9*width, 0.07*height])
    btn_open_image = Button(ax_open_image, 'Open Image')
    image_buttons.append(('open', btn_open_image))
    
    ax_show_bg = fig.add_axes([left + 0.02*width, bottom + 0.02*height, 0.9*width, 0.07*height])
    btn_show_bg = Button(ax_show_bg, 'Background Image')
    image_buttons.append(('bg', btn_show_bg))

labels_enabled = [True]
show_background_image = [False]  # Track if background image should be shown

# --- Drawing and event logic ---
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
    thumb_bbox = thumb_container_ax.get_position()
    
    # Show all thumbnails in a grid layout
    max_visible_thumbs = 20  # Maximum thumbnails to show at once
    current_idx = current_image_idx[0]
    
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
        
    thumb_width_per_item = (thumb_bbox.width / num_visible) * 0.9
    padding_per_item = (thumb_bbox.width / num_visible) * 0.1
    total_padding = padding_per_item * (num_visible - 1)
    total_thumb_width = thumb_width_per_item * num_visible
    
    # Center the visible thumbnails
    start_x = thumb_bbox.x0 + (thumb_bbox.width - total_thumb_width - total_padding) / 2
    
    for i, ax in enumerate(thumb_axes):
        if start_idx <= i < end_idx:
            ax.set_visible(True)
            visible_idx = i - start_idx
            ax.set_position([start_x + visible_idx * (thumb_width_per_item + padding_per_item),
                             thumb_bbox.y0,
                             thumb_width_per_item,
                             thumb_bbox.height])
        else:
            ax.set_visible(False)
    
    # Update navigation text
    nav_text.set_text(f'Plot {current_idx+1} of {total_thumbs}')
    
    fig.canvas.draw_idle()

def draw_main_plot(idx):
    try:
        main_ax.clear()
        img_id = image_ids[idx]
        df_selected = df[df['image_id'] == img_id].copy()
        
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
                facecolor='none'
            )
            main_ax.add_patch(rect)
        
        x_min_all = df_selected['x_min'].min() if not df_selected['x_min'].isnull().all() else 0
        x_max_all = df_selected['x_max'].max() if not df_selected['x_max'].isnull().all() else 100
        y_min_all = df_selected['y_min'].min() if not df_selected['y_min'].isnull().all() else 0
        y_max_all = df_selected['y_max'].max() if not df_selected['y_max'].isnull().all() else 100

        # Set axis limits
        main_ax.set_xlim(x_min_all - 10, x_max_all + 10)
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
        
        state = annotation_states[img_id]
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
        
        # Draw existing annotations
        for ann in state.annotations:
            x, y = ann['x'], ann['y']
            mark_value = ann.get('mark_value', '')
            if state.mode == 'number' and str(mark_value).isdigit():
                marker, = main_ax.plot(x, y, marker=f'${mark_value}$', color='red', markersize=14, mew=2)
            else:
                marker, = main_ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
            label_text = ', '.join(str(ann.get(label_col, '')) for label_col in label_columns)
            state.markers.append((marker, label_text, x, y, mark_value))
            
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

def onclick_main(event):
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
        
    label_text = None
    annotation_entry = {'image_id': img_id, 'x': x, 'y': y}
    mark_value = ''

    clicked_bb_index = None
    for idx_row, row in df_selected.iterrows():
        if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
            clicked_bb_index = row.name
            break
    
    if clicked_bb_index is not None:
        row = df.loc[clicked_bb_index]
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

def on_motion_main(event):
    if not labels_enabled[0]:
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        if state.hover_text:
            try:
                state.hover_text.set_visible(False)
                fig.canvas.draw_idle()
            except (NotImplementedError, ValueError):
                pass
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
            except (NotImplementedError, ValueError):
                pass
        return
    
    show_label = False
    x, y = event.xdata, event.ydata
    
    for idx_row, row in df_selected.iterrows():
        if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
            label_lines = []
            for label_col in label_columns:
                if label_col in row and str(row[label_col]).strip() and str(row[label_col]).lower() != 'nan':
                    display_name = label_col.replace('label_', '')
                    label_lines.append(f"{display_name}: {row[label_col]}")
            
            if label_lines:
                hover_text = '\n'.join(label_lines)
            else:
                hover_text = "No labels"
            
            if state.hover_text is None:
                try:
                    state.hover_text = main_ax.text(x, y, hover_text, color='blue', fontsize=10, va='bottom', ha='left', 
                                                  bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.5'))
                except (NotImplementedError, ValueError):
                    pass
            else:
                try:
                    state.hover_text.set_position((x, y))
                    state.hover_text.set_text(hover_text)
                    state.hover_text.set_visible(True)
                except (NotImplementedError, ValueError):
                    pass
            fig.canvas.draw_idle()
            show_label = True
            break
    
    if not show_label and state.hover_text:
        try:
            state.hover_text.set_visible(False)
            fig.canvas.draw_idle()
        except (NotImplementedError, ValueError):
            pass

def on_mode(label):
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    state.mode = label
    draw_main_plot(current_image_idx[0])

def on_reset(event):
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    state.counter = 1

def on_undo(event):
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    if state.annotations:
        ann = state.annotations.pop()
        state.undone.append(ann)
        draw_main_plot(current_image_idx[0])

def on_redo(event):
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    if state.undone:
        ann = state.undone.pop()
        state.annotations.append(ann)
        draw_main_plot(current_image_idx[0])

def on_clear(event):
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    state.reset()
    df.loc[df['image_id'] == img_id, 'marked'] = ''
    draw_main_plot(current_image_idx[0])

def on_toggle_labels(event):
    labels_enabled[0] = not labels_enabled[0]
    if labels_enabled[0]:
        btn_toggle_labels.label.set_text('Disable Labels')
    else:
        btn_toggle_labels.label.set_text('Enable Labels')
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        if state.hover_text:
            try:
                state.hover_text.set_visible(False)
                fig.canvas.draw_idle()
            except (NotImplementedError, ValueError):
                pass
    fig.canvas.draw_idle()

def on_open_image(event):
    """Open current image in browser"""
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    if state.image_url:
        open_image_in_browser(state.image_url)
    else:
        messagebox.showinfo("Info", "No image URL available for this plot.")

def on_toggle_background(event):
    """Toggle background image display"""
    show_background_image[0] = not show_background_image[0]
    if show_background_image[0]:
        btn_show_bg.label.set_text('Hide Background Image')
    else:
        btn_show_bg.label.set_text('Show Background Image')
    # Redraw the current plot to show/hide background
    draw_main_plot(current_image_idx[0])

# Thumbnail click handling is now integrated into onclick_main

# Remove the on_slider_change function since we no longer have a slider

def save_annotations(event=None):
    annotations = []
    for img_id in image_ids:
        state = annotation_states[img_id]
        annotations.extend(state.annotations)
    if annotations:
        annotations_df = pd.DataFrame(annotations)
        annotations_df.to_csv(os.path.join(output_dir, 'annotations_marked.csv'), index=False)
        df.to_csv(os.path.join(output_dir, 'marked_skus.csv'), index=False)
        print(f"Annotations saved to {os.path.join(output_dir, 'annotations_marked.csv')} and {os.path.join(output_dir, 'marked_skus.csv')}")
    else:
        print("No annotations were made.")

def save_all_annotated_plots():
    for img_id in image_ids:
        df_selected = df[df['image_id'] == img_id].copy()
        fig, ax = plt.subplots(figsize=(6, 6))
        
        if not df_selected.empty and not df_selected['x_min'].isna().all():
            df_selected['width'] = df_selected['x_max'] - df_selected['x_min']
            df_selected['height'] = df_selected['y_max'] - df_selected['y_min']
            for _, row in df_selected.iterrows():
                rect = patches.Rectangle(
                    (row['x_min'], row['y_min']),
                    row['width'],
                    row['height'],
                    linewidth=1,
                    edgecolor='r',
                    facecolor='none'
                )
                ax.add_patch(rect)
            
            x_min_all = df_selected['x_min'].min()
            x_max_all = df_selected['x_max'].max()
            y_min_all = df_selected['y_min'].min()
            y_max_all = df_selected['y_max'].max()
            ax.set_xlim(x_min_all - 10, x_max_all + 10)
            ax.set_ylim(y_min_all - 10, y_max_all + 10)
        else:
            ax.text(0.5, 0.5, "No bounding box data available", 
                    ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])

        state = annotation_states[img_id]
        for ann in state.annotations:
            x, y = ann['x'], ann['y']
            mark_value = ann.get('mark_value', '')
            if state.mode == 'number' and str(mark_value).isdigit():
                ax.plot(x, y, marker=f'${mark_value}$', color='red', markersize=10, mew=2)
            else:
                ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Bounding Boxes for image_id: {img_id}')
        out_path = os.path.join(output_dir, f'annotated_{img_id}.png')
        plt.savefig(out_path)
        plt.close(fig)
    print(f"All annotated plots saved to {output_dir}")

def on_close(event=None):
    save_all_annotated_plots()
    print("All annotated plots saved on close.")

fig.canvas.mpl_connect('close_event', on_close)

radio.on_clicked(on_mode)
btn_reset.on_clicked(on_reset)
btn_undo.on_clicked(on_undo)
btn_redo.on_clicked(on_redo)
btn_clear.on_clicked(on_clear)
btn_save.on_clicked(save_annotations)
btn_toggle_labels.on_clicked(on_toggle_labels)

# Connect image buttons if they exist
for btn_type, btn in image_buttons:
    if btn_type == 'open':
        btn.on_clicked(on_open_image)
    elif btn_type == 'bg':
        btn.on_clicked(on_toggle_background)

# Connect all events to the main figure
fig.canvas.mpl_connect('button_press_event', onclick_main)
fig.canvas.mpl_connect('motion_notify_event', on_motion_main)

update_thumbnail_visibility()
draw_main_plot(current_image_idx[0])
plt.show()