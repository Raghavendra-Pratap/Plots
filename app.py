import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import requests
from PIL import Image
import io
import re

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

# --- 2. Initialize Session State ---
# This dictionary persists variables across user interactions.
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

# --- 3. Streamlit UI and Logic ---
st.title("Interactive Bounding Box Plotter")

# File uploader replaces tkinter's filedialog.askopenfilename
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

        df = st.session_state.df
        df['x_min'] = pd.to_numeric(df['x_min'], errors='coerce')
        df['x_max'] = pd.to_numeric(df['x_max'], errors='coerce')
        df['y_min'] = pd.to_numeric(df['y_min'], errors='coerce')
        df['y_max'] = pd.to_numeric(df['y_max'], errors='coerce')
        df['image_id'] = df['image_id'].astype(str)
        
        image_url_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['url', 'link', 'image', 'img', 'src']) and df[col].apply(is_url).any()]

        if not image_url_columns:
            st.warning("No image URL columns were found. Background images will not be displayed.")
        else:
            url_col = image_url_columns[0]
            st.session_state.image_urls = {
                img_id: df[df['image_id'] == img_id][url_col].dropna().iloc[0] if not df[df['image_id'] == img_id][url_col].dropna().empty else None
                for img_id in df['image_id'].unique()
            }
        
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Check if a file has been uploaded and processed
if not st.session_state.df.empty:
    df = st.session_state.df
    image_ids = list(df['image_id'].unique())
    num_images = len(image_ids)

    # --- 4. Main Application Logic ---
    st.sidebar.header("Navigation")
    # Navigation controls
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button("Previous"):
            st.session_state.current_image_idx = (st.session_state.current_image_idx - 1) % num_images
    with col2:
        st.write(f"Image {st.session_state.current_image_idx + 1} of {num_images}")
    with col3:
        if st.button("Next"):
            st.session_state.current_image_idx = (st.session_state.current_image_idx + 1) % num_images
    
    current_image_id = image_ids[st.session_state.current_image_idx]

    # --- Annotation controls ---
    st.sidebar.header("Annotation Controls")
    st.session_state.mode = st.sidebar.radio("Marking Mode", ('x', 'number'))
    
    if st.session_state.mode == 'number':
        st.sidebar.button("Reset Counter", on_click=lambda: st.session_state.update(counter=1))

    # Sidebar button for toggling background image
    st.session_state.show_background_image = st.sidebar.checkbox("Show background image", value=st.session_state.show_background_image)

    # --- Interactive plot display ---
    st.header(f"Bounding Boxes for Image: {current_image_id}")
    
    # Use a placeholder for the plot to update it
    plot_placeholder = st.empty()

    # Get data for the current image
    df_selected = df[df['image_id'] == current_image_id].copy()

    # --- Plotting function (refactored for Streamlit) ---
    def draw_plot():
        fig, ax = plt.subplots(figsize=(10, 8))

        if st.session_state.show_background_image and st.session_state.image_urls.get(current_image_id):
            img_array = load_image_from_url(st.session_state.image_urls[current_image_id])
            if img_array is not None:
                if not df_selected.empty and not df_selected['x_min'].isna().all():
                    x_min_all = df_selected['x_min'].min()
                    x_max_all = df_selected['x_max'].max()
                    y_min_all = df_selected['y_min'].min()
                    y_max_all = df_selected['y_max'].max()
                    ax.imshow(img_array, extent=[x_min_all, x_max_all, y_min_all, y_max_all], aspect='auto', alpha=1.0)
                else:
                    ax.imshow(img_array, aspect='auto')

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
                if st.session_state.mode == 'number' and str(ann['mark_value']).isdigit():
                    ax.plot(ann['x'], ann['y'], marker=f'${ann['mark_value']}$', color='red', markersize=14, mew=2)
                else:
                    ax.plot(ann['x'], ann['y'], marker='x', color='blue', markersize=10, mew=2)
        
        plot_placeholder.pyplot(fig)
        plt.close(fig)

    draw_plot()

    # --- Click event handling (simulated using Streamlit Image Coordinates) ---
    st.info("Click on a bounding box in the plot to add an annotation.")
    
    # You would need to use a custom component for direct click events on the plot.
    # The simplest way to handle this is to ask the user for coordinates, or use an external library like streamlit_image_coordinates.
    # For this example, we'll demonstrate a simplified interaction model.
    with st.form("annotation_form"):
        st.subheader("Add an Annotation")
        col_x, col_y = st.columns(2)
        with col_x:
            x_coord = st.number_input("X Coordinate", step=1.0)
        with col_y:
            y_coord = st.number_input("Y Coordinate", step=1.0)
        
        if st.form_submit_button("Add Annotation"):
            if current_image_id not in st.session_state.annotations:
                st.session_state.annotations[current_image_id] = []
            
            # Check if the coordinates are within any bounding box
            is_inside_box = False
            for _, row in df_selected.dropna(subset=['x_min', 'x_max', 'y_min', 'y_max']).iterrows():
                if row['x_min'] <= x_coord <= row['x_max'] and row['y_min'] <= y_coord <= row['y_max']:
                    is_inside_box = True
                    break
            
            if is_inside_box:
                mark_value = ''
                if st.session_state.mode == 'number':
                    mark_value = st.session_state.annotations.get(current_image_id, [])[-1]['mark_value'] + 1 if st.session_state.annotations.get(current_image_id) else 1
                else:
                    mark_value = 'x'
                
                new_annotation = {
                    'image_id': current_image_id, 
                    'x': x_coord, 
                    'y': y_coord, 
                    'mark_value': mark_value
                }
                st.session_state.annotations[current_image_id].append(new_annotation)
                st.success("Annotation added!")
                st.rerun() # Rerun to update the plot
            else:
                st.warning("Click coordinates are not within a bounding box.")

    # --- Save and Download ---
    st.sidebar.header("Export Data")
    if st.sidebar.button("Save and Export Annotations"):
        all_annotations = [ann for annotations_list in st.session_state.annotations.values() for ann in annotations_list]
        if all_annotations:
            annotations_df = pd.DataFrame(all_annotations)
            st.session_state.output_csv = annotations_df.to_csv(index=False).encode('utf-8')
            st.success("Annotations have been saved. You can now download the CSV.")
    
    if st.session_state.output_csv:
        st.sidebar.download_button(
            label="Download Annotations as CSV",
            data=st.session_state.output_csv,
            file_name='annotations_streamlit.csv',
            mime='text/csv',
        )

else:
    st.info("Please upload a CSV file to get started.")