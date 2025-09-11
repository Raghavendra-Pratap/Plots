import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import requests
from PIL import Image
import io
import re
import base64
from datetime import datetime
import os

# --- 1. Helper functions ---
def load_image_from_url(url):
    """Load image from URL and return as numpy array"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        return np.array(img)
    except Exception as e:
        st.error(f"Error loading image from {url}: {e}")
        return None

def is_url(string):
    """Check if a string is a valid URL"""
    return re.match(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(string)) is not None

def generate_thumbnail(df_selected):
    """Generate thumbnail for an image"""
    if df_selected.empty or df_selected['x_min'].isna().all():
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.axis('off')
        ax.text(0.5, 0.5, "No data", ha='center', va='center', transform=ax.transAxes, fontsize=8)
        return fig
    else:
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
        
        x_min_all = df_selected['x_min'].min()
        x_max_all = df_selected['x_max'].max()
        y_min_all = df_selected['y_min'].min()
        y_max_all = df_selected['y_max'].max()
        ax.set_xlim(x_min_all - 10, x_max_all + 10)
        ax.set_ylim(y_min_all - 10, y_max_all + 10)
        ax.axis('off')
        return fig

# --- 2. Initialize Session State ---
if 'annotations' not in st.session_state:
    st.session_state.annotations = {}
if 'current_image_idx' not in st.session_state:
    st.session_state.current_image_idx = 0
if 'mode' not in st.session_state:
    st.session_state.mode = 'x'
if 'show_background_image' not in st.session_state:
    st.session_state.show_background_image = False
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'image_urls' not in st.session_state:
    st.session_state.image_urls = {}
if 'output_csv' not in st.session_state:
    st.session_state.output_csv = None
if 'counters' not in st.session_state:
    st.session_state.counters = {}
if 'undone' not in st.session_state:
    st.session_state.undone = {}
if 'labels_enabled' not in st.session_state:
    st.session_state.labels_enabled = True
if 'loaded_images' not in st.session_state:
    st.session_state.loaded_images = {}

# --- 3. Streamlit UI and Logic ---
st.title("Interactive Bounding Box Plotter")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # --- Data Loading and Pre-processing ---
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        
        # Reset state on new file upload
        st.session_state.annotations = {}
        st.session_state.current_image_idx = 0
        st.session_state.image_urls = {}
        st.session_state.output_csv = None
        st.session_state.counters = {}
        st.session_state.undone = {}
        st.session_state.loaded_images = {}

        df = st.session_state.df
        df['x_min'] = pd.to_numeric(df['x_min'], errors='coerce')
        df['x_max'] = pd.to_numeric(df['x_max'], errors='coerce')
        df['y_min'] = pd.to_numeric(df['y_min'], errors='coerce')
        df['y_max'] = pd.to_numeric(df['y_max'], errors='coerce')
        df['image_id'] = df['image_id'].astype(str)
        
        # Detect image URL columns
        image_url_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['url', 'link', 'image', 'img', 'src']):
                sample_values = df[col].dropna().head(10)
                if len(sample_values) > 0:
                    url_count = sum(1 for val in sample_values if str(val).startswith(('http://', 'https://', 'www.')))
                    if url_count > 0:
                        image_url_columns.append(col)

        st.info(f"Detected potential image URL columns: {image_url_columns}")

        if image_url_columns:
            url_col = image_url_columns[0]
            st.session_state.image_urls = {
                img_id: df[df['image_id'] == img_id][url_col].dropna().iloc[0] if not df[df['image_id'] == img_id][url_col].dropna().empty else None
                for img_id in df['image_id'].unique()
            }
        else:
            st.warning("No image URL columns were found. Background images will not be displayed.")
        
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Check if a file has been uploaded and processed
if not st.session_state.df.empty:
    df = st.session_state.df
    image_ids = list(df['image_id'].unique())
    num_images = len(image_ids)
    
    # Find label columns
    label_columns = [col for col in df.columns if col.startswith('label_')]

    # --- 4. Main Application Logic ---
    st.sidebar.header("Navigation")
    
    # Thumbnail navigation
    st.sidebar.subheader("Thumbnail Navigation")
    
    # Calculate how many thumbnails to show
    max_visible_thumbs = 10
    current_idx = st.session_state.current_image_idx
    half_visible = max_visible_thumbs // 2
    start_idx = max(0, current_idx - half_visible)
    end_idx = min(num_images, start_idx + max_visible_thumbs)
    
    # Adjust start_idx if we're near the end
    if end_idx - start_idx < max_visible_thumbs and start_idx > 0:
        start_idx = max(0, end_idx - max_visible_thumbs)
    
    # Create columns for thumbnails
    cols = st.sidebar.columns(min(max_visible_thumbs, end_idx - start_idx))
    
    for i, col in enumerate(cols):
        idx = start_idx + i
        if idx < num_images:
            img_id = image_ids[idx]
            df_sel = df[df['image_id'] == img_id]
            
            # Generate thumbnail
            fig = generate_thumbnail(df_sel)
            
            # Highlight current image
            if idx == current_idx:
                fig.patch.set_facecolor('lightblue')
            
            # Display thumbnail with click functionality
            if col.button(f"📷 {img_id}", key=f"thumb_{idx}"):
                st.session_state.current_image_idx = idx
                st.rerun()
            
            plt.close(fig)
    
    # Navigation controls
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button("◀ Previous", key="prev_btn"):
            st.session_state.current_image_idx = (st.session_state.current_image_idx - 1) % num_images
            st.rerun()
    with col2:
        st.write(f"**{st.session_state.current_image_idx + 1} / {num_images}**")
    with col3:
        if st.button("Next ▶", key="next_btn"):
            st.session_state.current_image_idx = (st.session_state.current_image_idx + 1) % num_images
            st.rerun()
    
    current_image_id = image_ids[st.session_state.current_image_idx]

    # --- Annotation controls ---
    st.sidebar.header("Annotation Controls")
    
    # Marking mode
    st.session_state.mode = st.sidebar.radio("Marking Mode", ('x', 'number'))
    
    # Counter management
    if st.session_state.mode == 'number':
        if current_image_id not in st.session_state.counters:
            st.session_state.counters[current_image_id] = 1
        st.sidebar.write(f"Counter: {st.session_state.counters[current_image_id]}")
        if st.sidebar.button("Reset Counter", key="reset_counter"):
            st.session_state.counters[current_image_id] = 1
            st.rerun()
    
    # Undo/Redo controls
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Undo", key="undo_btn"):
            if current_image_id in st.session_state.annotations and st.session_state.annotations[current_image_id]:
                if current_image_id not in st.session_state.undone:
                    st.session_state.undone[current_image_id] = []
                st.session_state.undone[current_image_id].append(st.session_state.annotations[current_image_id].pop())
                st.rerun()
    with col2:
        if st.button("Redo", key="redo_btn"):
            if current_image_id in st.session_state.undone and st.session_state.undone[current_image_id]:
                if current_image_id not in st.session_state.annotations:
                    st.session_state.annotations[current_image_id] = []
                st.session_state.annotations[current_image_id].append(st.session_state.undone[current_image_id].pop())
                st.rerun()
    
    # Clear all annotations
    if st.sidebar.button("Clear All", key="clear_all"):
        if current_image_id in st.session_state.annotations:
            st.session_state.annotations[current_image_id] = []
        if current_image_id in st.session_state.counters:
            st.session_state.counters[current_image_id] = 1
        st.rerun()
    
    # Labels toggle
    st.session_state.labels_enabled = st.sidebar.checkbox("Show Labels", value=st.session_state.labels_enabled, key="show_labels")
    
    # Background image toggle
    if any(st.session_state.image_urls.values()):
        st.session_state.show_background_image = st.sidebar.checkbox("Show Background Image", value=st.session_state.show_background_image, key="show_bg")
        
        # Open image button
        if st.sidebar.button("Open Image in Browser", key="open_image"):
            if st.session_state.image_urls.get(current_image_id):
                url = st.session_state.image_urls[current_image_id]
                st.markdown(f'<a href="{url}" target="_blank">Click here to open image in new tab</a>', unsafe_allow_html=True)
            else:
                st.warning("No image URL available for this plot.")

    # --- Interactive plot display ---
    st.header(f"Bounding Boxes for Image: {current_image_id}")
    
    # Get data for the current image
    df_selected = df[df['image_id'] == current_image_id].copy()

    # --- Plotting function ---
    def draw_plot():
        fig, ax = plt.subplots(figsize=(12, 10))

        # Add background image if enabled and available
        if st.session_state.show_background_image and st.session_state.image_urls.get(current_image_id):
            url = st.session_state.image_urls[current_image_id]
            if url not in st.session_state.loaded_images:
                img_array = load_image_from_url(url)
                if img_array is not None:
                    st.session_state.loaded_images[url] = img_array
                else:
                    st.session_state.loaded_images[url] = None
            
            if st.session_state.loaded_images.get(url) is not None:
                img_array = st.session_state.loaded_images[url]
                if not df_selected.empty and not df_selected['x_min'].isna().all():
                    x_min_all = df_selected['x_min'].min()
                    x_max_all = df_selected['x_max'].max()
                    y_min_all = df_selected['y_min'].min()
                    y_max_all = df_selected['y_max'].max()
                    ax.imshow(img_array, extent=[x_min_all - 10, x_max_all + 10, y_min_all - 10, y_max_all + 10], 
                             alpha=0.7, zorder=0)
                    ax.set_title(f'Bounding Boxes for image_id: {current_image_id} (with background image)')
                else:
                    ax.imshow(img_array, alpha=0.7, zorder=0)
                    ax.set_title(f'Bounding Boxes for image_id: {current_image_id} (with background image)')

        # Draw bounding boxes
        if not df_selected.empty and not df_selected['x_min'].isna().all():
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

            x_min_all = df_selected['x_min'].min()
            x_max_all = df_selected['x_max'].max()
            y_min_all = df_selected['y_min'].min()
            y_max_all = df_selected['y_max'].max()
            
            ax.set_xlim(x_min_all - 10, x_max_all + 10)
            ax.set_ylim(y_min_all - 10, y_max_all + 10)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
        else:
            ax.text(0.5, 0.5, "No bounding box data available", 
                    ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f'Bounding Boxes for image_id: {current_image_id}')
        
        # Display annotations
        if current_image_id in st.session_state.annotations:
            for ann in st.session_state.annotations[current_image_id]:
                x, y = ann['x'], ann['y']
                mark_value = ann.get('mark_value', '')
                if st.session_state.mode == 'number' and str(mark_value).isdigit():
                    ax.plot(x, y, marker=f'${mark_value}$', color='red', markersize=14, mew=2)
                else:
                    ax.plot(x, y, marker='x', color='blue', markersize=10, mew=2)
        
        st.pyplot(fig)
        plt.close(fig)

    draw_plot()

    # --- Click event handling using streamlit-plotly-events ---
    st.info("Click on a bounding box in the plot to add an annotation.")
    
    # Note: For direct plot clicking, you would need to use streamlit-plotly-events
    # For now, we'll provide a simplified coordinate input system
    with st.expander("Manual Annotation (if plot clicking doesn't work)", expanded=False):
        with st.form("annotation_form"):
            st.subheader("Add an Annotation")
            col_x, col_y = st.columns(2)
            with col_x:
                x_coord = st.number_input("X Coordinate", step=1.0, key="x_coord")
            with col_y:
                y_coord = st.number_input("Y Coordinate", step=1.0, key="y_coord")
            
            if st.form_submit_button("Add Annotation"):
                if current_image_id not in st.session_state.annotations:
                    st.session_state.annotations[current_image_id] = []
                
                # Check if the coordinates are within any bounding box
                is_inside_box = False
                clicked_row = None
                for _, row in df_selected.dropna(subset=['x_min', 'x_max', 'y_min', 'y_max']).iterrows():
                    if row['x_min'] <= x_coord <= row['x_max'] and row['y_min'] <= y_coord <= row['y_max']:
                        is_inside_box = True
                        clicked_row = row
                        break
                
                if is_inside_box:
                    # Initialize counter if needed
                    if current_image_id not in st.session_state.counters:
                        st.session_state.counters[current_image_id] = 1
                    
                    # Create annotation
                    mark_value = ''
                    if st.session_state.mode == 'number':
                        mark_value = str(st.session_state.counters[current_image_id])
                        st.session_state.counters[current_image_id] += 1
                    else:
                        mark_value = 'x'
                    
                    new_annotation = {
                        'image_id': current_image_id, 
                        'x': x_coord, 
                        'y': y_coord, 
                        'mark_value': mark_value
                    }
                    
                    # Add label information
                    for label_col in label_columns:
                        if label_col in clicked_row:
                            new_annotation[label_col] = clicked_row[label_col]
                    
                    st.session_state.annotations[current_image_id].append(new_annotation)
                    
                    # Clear undone stack when new annotation is added
                    if current_image_id in st.session_state.undone:
                        st.session_state.undone[current_image_id] = []
                    
                    st.success(f"Added {mark_value} annotation at ({x_coord:.1f}, {y_coord:.1f})")
                    st.rerun()
                else:
                    st.warning("Click coordinates are not within a bounding box.")

    # --- Annotation display ---
    if current_image_id in st.session_state.annotations and st.session_state.annotations[current_image_id]:
        st.subheader("Current Annotations")
        annotations_df = pd.DataFrame(st.session_state.annotations[current_image_id])
        st.dataframe(annotations_df, use_container_width=True)

    # --- Save and Download ---
    st.sidebar.header("Export Data")
    
    if st.sidebar.button("Save and Export Annotations", key="save_btn"):
        all_annotations = []
        for img_id, annotations_list in st.session_state.annotations.items():
            all_annotations.extend(annotations_list)
        
        if all_annotations:
            annotations_df = pd.DataFrame(all_annotations)
            
            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save annotations
            annotations_csv = annotations_df.to_csv(index=False)
            st.session_state.output_csv = annotations_csv.encode('utf-8')
            
            # Update original dataframe with marked column
            df_updated = df.copy()
            df_updated['marked'] = ''
            
            for ann in all_annotations:
                img_id = ann['image_id']
                x, y = ann['x'], ann['y']
                mark_value = ann['mark_value']
                
                # Find matching rows and update marked column
                mask = (df_updated['image_id'] == img_id) & \
                       (df_updated['x_min'] <= x) & (df_updated['x_max'] >= x) & \
                       (df_updated['y_min'] <= y) & (df_updated['y_max'] >= y)
                
                if mark_value == 'x':
                    df_updated.loc[mask, 'marked'] = 'yes'
                else:
                    df_updated.loc[mask, 'marked'] = mark_value
            
            # Save updated dataframe
            updated_csv = df_updated.to_csv(index=False)
            st.session_state.updated_csv = updated_csv.encode('utf-8')
            
            st.success("Annotations have been saved. You can now download the files.")
        else:
            st.warning("No annotations to save.")
    
    if st.session_state.output_csv:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.download_button(
                label="Download Annotations",
                data=st.session_state.output_csv,
                file_name=f'annotations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv',
            )
        with col2:
            if hasattr(st.session_state, 'updated_csv'):
                st.download_button(
                    label="Download Updated Data",
                    data=st.session_state.updated_csv,
                    file_name=f'marked_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                )

else:
    st.info("Please upload a CSV file to get started.")