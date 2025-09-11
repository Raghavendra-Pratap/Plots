# 🔧 Features & Functions Documentation

## 📋 **Table of Contents**

1. [Core Functionality](#core-functionality)
2. [User Interface](#user-interface)
3. [Data Processing](#data-processing)
4. [Annotation Tools](#annotation-tools)
5. [Performance Features](#performance-features)
6. [Export & Output](#export--output)
7. [Technical Features](#technical-features)
8. [Error Handling](#error-handling)

---

## 🎯 **Core Functionality**

### **Bounding Box Visualization**
- **Red Rectangle Display**: Clear visual representation of bounding boxes
- **Coordinate System**: Support for both matplotlib and image-style coordinate systems
- **Multi-Image Support**: Navigate through multiple images in a single session
- **Thumbnail Navigation**: Visual preview of all images with current position indicator

### **CSV Data Import**
- **Automatic Column Detection**: Identifies required and optional columns
- **Data Validation**: Ensures coordinate data is numeric and valid
- **Flexible Format Support**: Handles various CSV structures and naming conventions
- **Memory-Efficient Loading**: Processes large datasets without memory issues

---

## 🖥️ **User Interface**

### **Welcome Screen**
```python
def show_welcome_screen_and_get_filepath():
    """
    Modern Tkinter-based welcome interface with:
    - File selection dialog
    - Performance settings configuration
    - Device capability detection
    - Professional styling and animations
    """
```

**Features:**
- **File Selection**: Intuitive CSV file picker
- **Settings Panel**: Comprehensive performance configuration
- **Device Detection**: Automatic hardware capability assessment
- **Performance Profiles**: Pre-configured settings for different device types

### **Main Plotting Interface**
```python
def create_main_plot_interface():
    """
    Creates the main matplotlib interface with:
    - Main plotting area (left panel)
    - Control panel (right panel)
    - Thumbnail navigation (bottom panel)
    - Dynamic sizing based on screen resolution
    """
```

**Layout:**
- **Left Panel (70%)**: Main plotting area with bounding boxes
- **Right Panel (30%)**: Control buttons and annotation tools
- **Bottom Panel**: Thumbnail strip with navigation

### **Control Panel Buttons**

#### **Annotation Mode Selection**
- **X Mode**: Mark bounding boxes with "X" symbols
- **Number Mode**: Mark bounding boxes with sequential numbers (1, 2, 3...)

#### **Annotation Control**
- **Reset Counter**: Reset numbering sequence to 1
- **Undo**: Remove last annotation (supports multiple undos)
- **Redo**: Restore previously undone annotations
- **Clear All**: Remove all annotations from current plot

#### **Display Control**
- **Flip Y-Axis**: Toggle between coordinate systems
- **Save**: Export annotations and data
- **Toggle Labels**: Enable/disable hover labels
- **Close**: Return to welcome screen

---

## 📊 **Data Processing**

### **CSV Structure Requirements**

#### **Required Columns**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `image_id` | String | Unique image identifier | "IMG_001", "69811866" |
| `x_min` | Numeric | Left boundary coordinate | 100, 250.5 |
| `x_max` | Numeric | Right boundary coordinate | 200, 350.2 |
| `y_min` | Numeric | Top boundary coordinate | 150, 300.1 |
| `y_max` | Numeric | Bottom boundary coordinate | 250, 400.8 |

#### **Optional Columns**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `label_*` | String | Any column starting with "label_" | `label_GT class name` |
| `marked` | String | Existing annotations | "yes", "1", "A" |
| `Image Link` | URL | Background image URL | "https://example.com/img.jpg" |

### **Data Processing Functions**

#### **CSV Loading & Validation**
```python
def process_csv_file(file_path):
    """
    Comprehensive CSV processing:
    - Loads CSV data with pandas
    - Validates coordinate columns
    - Detects label columns automatically
    - Creates output directory structure
    - Initializes annotation states
    """
```

#### **Label Detection**
```python
# Automatic detection of label columns
label_columns = [col for col in df.columns if col.startswith('label_')]
print(f"✓ Detected label columns: {label_columns}")
```

#### **Coordinate System Support**
```python
# Support for both coordinate systems
if y_axis_flipped[0]:
    # Image-style: Y increases downward
    ax.set_ylim(y_max_all + 10, y_min_all - 10)
else:
    # Matplotlib default: Y increases upward
    ax.set_ylim(y_min_all - 10, y_max_all + 10)
```

---

## 🎨 **Annotation Tools**

### **Click-to-Mark System**
```python
def onclick_main(event):
    """
    Handles mouse clicks for annotation:
    - Left-click only (button == 1)
    - Detects bounding box intersections
    - Prevents duplicate annotations
    - Updates DataFrame in real-time
    """
```

**Features:**
- **Precise Detection**: Accurate bounding box intersection testing
- **Duplicate Prevention**: Cannot annotate already marked boxes
- **Real-time Updates**: Immediate visual feedback
- **Data Persistence**: Changes saved to DataFrame

### **Annotation Modes**

#### **X Mode**
- **Symbol**: Green "X" marker
- **Storage**: Saves as "yes" in CSV
- **Visual**: High z-order display above bounding boxes

#### **Number Mode**
- **Symbol**: Red numbered markers (1, 2, 3...)
- **Storage**: Saves actual numbers in CSV
- **Counter**: Automatic sequential numbering

### **State Management**
```python
class AnnotationState:
    """
    Per-image annotation state management:
    - List of annotations with metadata
    - Undo/redo stack
    - Hover text management
    - Image URL storage
    """
    
    def __init__(self):
        self.annotations = []      # Annotation entries
        self.markers = []          # Visual markers
        self.undone = []          # Undo stack
        self.counter = 1          # Number counter
        self.mode = 'x'           # Current mode
        self.hover_text = None    # Hover label text
        self.image_url = None     # Background image URL
```

### **Undo/Redo System**
```python
def on_undo(event):
    """
    Undo functionality:
    - Removes last annotation
    - Updates DataFrame
    - Maintains undo stack
    - Redraws plot
    """

def on_redo(event):
    """
    Redo functionality:
    - Restores undone annotations
    - Updates DataFrame
    - Maintains redo stack
    - Redraws plot
    """
```

---

## ⚡ **Performance Features**

### **Device Detection**
```python
def get_device_profile():
    """
    Automatic hardware detection:
    - CPU core count
    - RAM capacity
    - Storage type (SSD/HDD)
    - Performance score calculation
    """
```

### **Performance Profiles**

#### **High Performance (16GB+ RAM)**
- All features enabled
- High-quality thumbnails
- Background images
- Smooth animations
- Anti-aliasing enabled

#### **Balanced (8-16GB RAM)**
- Most features enabled
- Optimized thumbnail quality
- Background images enabled
- Reduced animations
- Anti-aliasing enabled

#### **Low-End (<8GB RAM)**
- Minimal features
- Low-quality thumbnails
- No background images
- No animations
- Basic rendering

### **Memory Management**
```python
def manage_memory():
    """
    Configurable memory optimization:
    - Image caching control
    - Aggressive cleanup options
    - Progressive thumbnail loading
    - Memory usage monitoring
    """
```

### **Progressive Loading**
```python
if global_settings.get('progressive_loading', False):
    # Create placeholder thumbnails first
    # Load actual thumbnails progressively
    # Update display as thumbnails load
```

---

## 💾 **Export & Output**

### **CSV Export**
```python
def save_annotations(event=None):
    """
    Comprehensive data export:
    - Original CSV with marked column
    - Detailed annotation CSV
    - Summary statistics
    - Error handling and fallbacks
    """
```

**Output Files:**
1. **`marked_skus.csv`**: Original data with annotation column
2. **`annotations_marked.csv`**: Detailed annotation information
3. **`annotated_*.png`**: Individual plot images

### **Plot Export**
```python
def save_all_annotated_plots():
    """
    Generates PNG images for each plot:
    - High-resolution output
    - Annotation markers included
    - Consistent styling
    - Organized file naming
    """
```

### **Output Organization**
```
plotts_YYYYMMDD_HHMMSS/
├── marked_skus.csv          # Main data export
├── annotations_marked.csv   # Annotation details
├── annotated_IMG_001.png   # Plot images
├── annotated_IMG_002.png
└── ...
```

---

## 🔧 **Technical Features**

### **Z-Order Management**
```python
# Layering system for proper display
main_ax.set_zorder(1000)           # Main plot
button_axes.set_zorder(100)        # Control buttons
hover_labels.set_zorder(10000)     # Hover text (top layer)
```

### **Event Handling**
```python
def connect_events():
    """
    Comprehensive event system:
    - Mouse clicks for annotation
    - Hover events for labels
    - Button callbacks
    - Window management
    """
```

**Event Types:**
- **Button Press**: Annotation and navigation
- **Motion Notify**: Hover label display
- **Close Event**: Data saving and cleanup

### **Error Handling**
```python
try:
    # Operation code
except Exception as e:
    print(f"✗ Error: {e}")
    # Graceful fallback
    # Error logging
    # User notification
```

### **Dependency Management**
```python
def check_and_install_dependencies():
    """
    Automatic package management:
    - Checks required packages
    - Installs missing dependencies
    - Verifies installations
    - Fallback handling
    """
```

---

## 🐛 **Error Handling**

### **Comprehensive Logging**
- **Console Output**: Real-time status updates
- **Error Logs**: Detailed error information in `plotter_error.log`
- **Performance Metrics**: Device detection and optimization feedback
- **Debug Information**: Detailed operation logging

### **Graceful Degradation**
- **Missing Dependencies**: Automatic installation attempts
- **File Errors**: Fallback to alternative locations
- **Memory Issues**: Configurable cleanup and optimization
- **Display Problems**: Alternative rendering backends

### **User Feedback**
- **Progress Indicators**: Clear status messages
- **Error Notifications**: User-friendly error descriptions
- **Recovery Options**: Suggested solutions for common issues
- **Help Information**: Contextual assistance

---

## 📈 **Performance Metrics**

### **Optimization Features**
- **Thumbnail Caching**: Reduces regeneration overhead
- **Progressive Loading**: Improves initial startup time
- **Memory Monitoring**: Prevents memory exhaustion
- **Render Optimization**: Efficient matplotlib usage

### **Scalability**
- **Large Datasets**: Handles thousands of bounding boxes
- **Multiple Images**: Efficient navigation through many images
- **Memory Management**: Configurable for different device capabilities
- **Performance Profiles**: Automatic optimization based on hardware

---

## 🔮 **Future Enhancements**

### **Planned Features (v1.1.0)**
- **Batch Processing**: Multiple CSV file handling
- **Export Formats**: PNG, PDF, SVG export options
- **Keyboard Shortcuts**: Enhanced navigation controls
- **Theme Support**: Dark/light mode options

### **Long-term Goals (v2.0.0)**
- **Web Interface**: Browser-based version
- **Collaborative Features**: Multi-user annotation
- **AI Integration**: Automated bounding box detection
- **Cloud Storage**: Remote data management

---

## 📚 **API Reference**

### **Core Functions**
| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `process_csv_file()` | Main CSV processing | `file_path` | `bool` |
| `create_plotting_interface()` | UI creation | None | `bool` |
| `onclick_main()` | Click handling | `event` | None |
| `on_motion_main()` | Hover handling | `event` | None |
| `save_annotations()` | Data export | `event` | None |

### **Utility Functions**
| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `generate_thumbnail()` | Thumbnail creation | `df_selected` | `numpy.ndarray` |
| `load_image_from_url()` | Image loading | `url` | `numpy.ndarray` |
| `get_device_profile()` | Hardware detection | None | `dict` |
| `manage_memory()` | Memory optimization | None | None |

---

*This documentation covers all features and functions of the Bounding Box Plotter. For specific implementation details, refer to the source code comments and inline documentation.* 