import sys
import subprocess
import importlib

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
        'numpy': 'numpy'
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

# Now import the required packages
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, RadioButtons, Slider
from tkinter import filedialog
import os
import numpy as np
from matplotlib import gridspec
from matplotlib.transforms import Bbox
import matplotlib
from datetime import datetime

# Open file picker dialog
file_path = filedialog.askopenfilename(
    title="Select CSV file",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)

if not file_path:
    print("No file selected. Exiting.")
    exit()

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

annotations = []

# Add a 'marked' column to the DataFrame, default to empty string
if 'marked' not in df.columns:
    df['marked'] = ''

# Find all label columns
label_columns = [col for col in df.columns if col.startswith('label_')]

# --- Annotation state for undo/redo/clear, per image_id ---
class AnnotationState:
    def __init__(self):
        self.annotations = []  # List of annotation_entry dicts
        self.markers = []      # List of (marker, label_text, x, y, mark_value)
        self.undone = []      # Stack for redo
        self.counter = 1
        self.mode = 'x'
        self.hover_text = None  # Store hover text per image
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

# Pre-populate annotation states from 'marked' column if it exists
if 'marked' in df.columns:
    for img_id in image_ids:
        state = annotation_states[img_id]
        df_sel = df[df['image_id'] == img_id]
        for idx, row in df_sel.iterrows():
            mark_val = str(row['marked']).strip()
            if mark_val and mark_val.lower() != 'nan':
                ann = {'image_id': img_id, 'x': (row['x_min'] + row['x_max']) / 2, 'y': (row['y_min'] + row['y_max']) / 2}
                if mark_val.isdigit():
                    ann['mark_value'] = mark_val
                    state.mode = 'number'
                else:
                    ann['mark_value'] = 'x'
                    state.mode = 'x'
                for label_col in [col for col in df.columns if col.startswith('label_')]:
                    ann[label_col] = row[label_col]
                state.annotations.append(ann)

# --- Generate thumbnails for each image ---
def generate_thumbnail(df_selected):
    # Skip if df_selected is empty or all bounding box columns are NaN
    if df_selected.empty or df_selected['x_min'].isna().all() or df_selected['x_max'].isna().all() or df_selected['y_min'].isna().all() or df_selected['y_max'].isna().all():
        print("[Warning] Skipping thumbnail: No valid bounding box data for this image_id.")
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
import tkinter as tk
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

# Calculate figure size based on screen size (80% of screen)
fig_width = int(screen_width * 0.8 / 100)  # Convert to inches (assuming 100 DPI)
fig_height = int(screen_height * 0.8 / 100)

# Ensure minimum and maximum sizes
fig_width = max(12, min(fig_width, 24))
fig_height = max(8, min(fig_height, 16))

fig = plt.figure(figsize=(fig_width, fig_height))

# Create a 2-row layout: 80% for main content, 20% for thumbnails
gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5], height_ratios=[8, 2], wspace=0.15, hspace=0.3)

# Top row (80%): Left column for controls, right for main plot
controls_ax = fig.add_subplot(gs[0, 0])
controls_ax.axis('off')
main_ax = fig.add_subplot(gs[0, 1])

# Bottom row (20%): Full width for thumbnails and scroll bar
thumb_container_ax = fig.add_subplot(gs[1, :])
thumb_container_ax.axis('off')

# Calculate how many thumbnails to show at once (based on available width)
max_visible_thumbs = 20  # Show more thumbnails in the full width
thumb_width = 1.0 / max_visible_thumbs

# Calculate positions within the 20% bottom area
# The bottom area is from 0 to 1 in the bottom row
# We'll use the top 60% for scroll bar, bottom 40% for thumbnails

# Add horizontal slider for thumbnail navigation - positioned in top 60% of bottom area
slider_ax = fig.add_axes([0.02, 0.65, 0.96, 0.08])
slider = Slider(
    ax=slider_ax,
    label='Thumbnail Navigation',
    valmin=0,
    valmax=max(0, len(image_ids) - max_visible_thumbs),
    valinit=0,
    valstep=1
)

# Create thumbnail axes with proper spacing - positioned in bottom 40% of bottom area
thumb_axes = []
for i in range(len(image_ids)):
    ax = fig.add_axes([0.02 + i * thumb_width, 0.15, thumb_width * 0.9, 0.4], frameon=False)
    ax.imshow(thumbnails[i])
    ax.axis('off')
    # Place image_id label below the thumbnail - make it smaller
    ax.text(0.5, -0.2, f'{image_ids[i]}', fontsize=7, ha='center', va='top', transform=ax.transAxes)
    thumb_axes.append(ax)

# --- Widget controls (now on the left) ---
# Use relative positions within controls_ax for widgets
bbox = controls_ax.get_position()
left, bottom, width, height = bbox.x0, bbox.y0, bbox.width, bbox.height
# Place widgets vertically in the left column with reduced left padding
ax_mode = fig.add_axes([left + 0.02*width, bottom + 0.65*height, 0.9*width, 0.15*height])
radio = RadioButtons(ax_mode, ('x', 'number'))
ax_mode.set_title('Marking Mode')
ax_reset = fig.add_axes([left + 0.02*width, bottom + 0.55*height, 0.9*width, 0.07*height])
btn_reset = Button(ax_reset, 'Reset Counter')
ax_undo = fig.add_axes([left + 0.02*width, bottom + 0.45*height, 0.9*width, 0.07*height])
btn_undo = Button(ax_undo, 'Undo')
ax_redo = fig.add_axes([left + 0.02*width, bottom + 0.35*height, 0.9*width, 0.07*height])
btn_redo = Button(ax_redo, 'Redo')
ax_clear = fig.add_axes([left + 0.02*width, bottom + 0.25*height, 0.9*width, 0.07*height])
btn_clear = Button(ax_clear, 'Clear All')
# Add Save button at the bottom
ax_save = fig.add_axes([left + 0.02*width, bottom + 0.10*height, 0.9*width, 0.07*height])
btn_save = Button(ax_save, 'Save')
# Add Toggle Labels button
ax_toggle_labels = fig.add_axes([left + 0.02*width, bottom + 0.02*height, 0.9*width, 0.07*height])
btn_toggle_labels = Button(ax_toggle_labels, 'Disable Labels')

labels_enabled = [True]  # Use list for mutability in nested functions

# --- Drawing and event logic ---
def update_thumbnail_visibility():
    """Update which thumbnails are visible based on slider position"""
    start_idx = int(slider.val)
    end_idx = min(start_idx + max_visible_thumbs, len(image_ids))
    
    for i, ax in enumerate(thumb_axes):
        if start_idx <= i < end_idx:
            ax.set_visible(True)
            # Update position for visible thumbnails - positioned in bottom 40% of bottom area
            visible_idx = i - start_idx
            ax.set_position([0.02 + visible_idx * thumb_width, 0.15, thumb_width * 0.9, 0.4])
        else:
            ax.set_visible(False)
    
    fig.canvas.draw_idle()

def draw_main_plot(idx):
    main_ax.clear()
    img_id = image_ids[idx]
    df_selected = df[df['image_id'] == img_id].copy()
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
    main_ax.set_xlim(df_selected['x_min'].min()-10, df_selected['x_max'].max()+10)
    main_ax.set_ylim(df_selected['y_min'].min()-10, df_selected['y_max'].max()+10)
    main_ax.set_xlabel('X')
    main_ax.set_ylabel('Y')
    main_ax.set_title(f'Bounding Boxes for image_id: {img_id}')
    # Draw all markers for this image
    state = annotation_states[img_id]
    # Set the radio button to the current state's mode
    if radio.value_selected != state.mode:
        radio.set_active(0 if state.mode == 'x' else 1)
    for marker, *_ in getattr(state, 'markers', []):
        marker.remove()
    state.markers.clear()
    
    # Clear hover text for current image
    if state.hover_text:
        state.hover_text.remove()
        state.hover_text = None
    
    for ann in state.annotations:
        x, y = ann['x'], ann['y']
        mark_value = ann.get('mark_value', '')
        if state.mode == 'number' and mark_value:
            marker, = main_ax.plot(x, y, marker='$'+str(mark_value)+'$', color='red', markersize=10, mew=2)
        else:
            marker, = main_ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
        label_text = ', '.join(str(ann.get(label_col, '')) for label_col in label_columns)
        state.markers.append((marker, label_text, x, y, mark_value))
    fig.canvas.draw_idle()

def onclick_main(event):
    if event.inaxes != main_ax:
        return
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    df_selected = df[df['image_id'] == img_id].copy()
    state = annotation_states[img_id]
    x, y = event.xdata, event.ydata
    label_text = None
    annotation_entry = {'image_id': img_id, 'x': x, 'y': y}
    mark_value = ''
    for idx_row, row in df_selected.iterrows():
        if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
            if state.mode == 'number':
                mark_value = str(state.counter)
                df.loc[row.name, 'marked'] = mark_value
                annotation_entry['mark_value'] = mark_value
                state.counter += 1
            else:
                mark_value = 'x'
                df.loc[row.name, 'marked'] = 'yes'
                annotation_entry['mark_value'] = mark_value
            for label_col in label_columns:
                annotation_entry[label_col] = row[label_col]
            label_text = ', '.join(str(row[label_col]) for label_col in label_columns)
    if state.mode == 'number' and mark_value and mark_value != 'x':
        marker, = main_ax.plot(x, y, marker='$'+str(mark_value)+'$', color='green', markersize=14, mew=2)
    else:
        marker, = main_ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
    state.annotations.append(annotation_entry)
    state.markers.append((marker, label_text, x, y, mark_value))
    state.undone.clear()
    fig.canvas.draw_idle()

def on_motion_main(event):
    if not labels_enabled[0]:  # Skip if labels are disabled
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        if state.hover_text:
            state.hover_text.set_visible(False)
            fig.canvas.draw_idle()
        return
        
    idx = current_image_idx[0]
    img_id = image_ids[idx]
    state = annotation_states[img_id]
    df_selected = df[df['image_id'] == img_id].copy()
    
    if event.inaxes != main_ax:
        if state.hover_text:
            state.hover_text.set_visible(False)
            fig.canvas.draw_idle()
        return
    
    show_label = False
    x, y = event.xdata, event.ydata
    
    # Check if mouse is over any bounding box (marked or unmarked)
    for idx_row, row in df_selected.iterrows():
        if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
            # Build multi-line label text for this bounding box
            label_lines = []
            for label_col in label_columns:
                if label_col in row and str(row[label_col]).strip() and str(row[label_col]).lower() != 'nan':
                    # Remove 'label_' prefix from column name for display
                    display_name = label_col.replace('label_', '')
                    label_lines.append(f"{display_name}: {row[label_col]}")
            
            if label_lines:
                hover_text = '\n'.join(label_lines)
            else:
                hover_text = "No labels"
            
            if state.hover_text is None:
                state.hover_text = main_ax.text(x, y, hover_text, color='blue', fontsize=10, va='bottom', ha='left', 
                                              bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.5'))
            else:
                state.hover_text.set_position((x, y))
                state.hover_text.set_text(hover_text)
                state.hover_text.set_visible(True)
            fig.canvas.draw_idle()
            show_label = True
            break
    
    if not show_label and state.hover_text:
        state.hover_text.set_visible(False)
        fig.canvas.draw_idle()

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
    draw_main_plot(current_image_idx[0])

def on_toggle_labels(event):
    labels_enabled[0] = not labels_enabled[0]
    if labels_enabled[0]:
        btn_toggle_labels.label.set_text('Disable Labels')
    else:
        btn_toggle_labels.label.set_text('Enable Labels')
        # Hide any visible label when disabling
        idx = current_image_idx[0]
        img_id = image_ids[idx]
        state = annotation_states[img_id]
        if state.hover_text:
            state.hover_text.set_visible(False)
            fig.canvas.draw_idle()
    fig.canvas.draw_idle()

def on_thumb_click(event):
    # Always switch and redraw, even if the same thumbnail is clicked
    for i, ax in enumerate(thumb_axes):
        if event.inaxes == ax:
            current_image_idx[0] = i
            print(f"Switching to image_id: {image_ids[i]}")  # Debug print
            draw_main_plot(i)
            break

def on_slider_change(val):
    update_thumbnail_visibility()

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
        df_selected['width'] = df_selected['x_max'] - df_selected['x_min']
        df_selected['height'] = df_selected['y_max'] - df_selected['y_min']
        fig, ax = plt.subplots(figsize=(6, 6))
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
        # Draw all markers for this image
        state = annotation_states[img_id]
        for ann in state.annotations:
            x, y = ann['x'], ann['y']
            mark_value = ann.get('mark_value', '')
            if state.mode == 'number' and mark_value and mark_value != 'x':
                ax.plot(x, y, marker='$'+str(mark_value)+'$', color='red', markersize=10, mew=2)
            else:
                ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
        ax.set_xlim(df_selected['x_min'].min()-10, df_selected['x_max'].max()+10)
        ax.set_ylim(df_selected['y_min'].min()-10, df_selected['y_max'].max()+10)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Bounding Boxes for image_id: {img_id}')
        out_path = os.path.join(output_dir, f'annotated_{img_id}.png')
        plt.savefig(out_path)
        plt.close(fig)
    print(f"All annotated plots saved to {output_dir}")

# Register a handler to save all annotated plots on close
import signal
import sys

def on_close(event=None):
    save_all_annotated_plots()
    print("All annotated plots saved on close.")

# Connect to the matplotlib close event
fig.canvas.mpl_connect('close_event', on_close)

radio.on_clicked(on_mode)
btn_reset.on_clicked(on_reset)
btn_undo.on_clicked(on_undo)
btn_redo.on_clicked(on_redo)
btn_clear.on_clicked(on_clear)
btn_save.on_clicked(save_annotations)
btn_toggle_labels.on_clicked(on_toggle_labels)
slider.on_changed(on_slider_change)

fig.canvas.mpl_connect('button_press_event', onclick_main)
fig.canvas.mpl_connect('motion_notify_event', on_motion_main)
fig.canvas.mpl_connect('button_press_event', on_thumb_click)

# Initialize the display
update_thumbnail_visibility()
draw_main_plot(current_image_idx[0])
plt.show()