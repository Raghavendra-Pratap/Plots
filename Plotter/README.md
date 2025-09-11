# Unified Plotter - Professional Bounding Box Visualization Tool

A modular, professional-grade application for visualizing and annotating bounding box data from CSV files with enterprise-grade features.

## Features

- **Professional UI**: Modern, dark-themed interface with consistent styling
- **Intelligent Settings**: Device detection and performance profiling with smart recommendations
- **Modular Architecture**: Clean, organized codebase with separate modules for different functionality
- **Enterprise-Grade**: Robust error handling, logging, and user feedback
- **Performance Optimization**: Multiple performance profiles for different hardware configurations

## Module Structure

```
plotter/
├── __init__.py          # Package initialization and exports
├── main.py              # Main application entry point
├── launcher.py          # Simple launcher script
├── ui_manager.py        # Unified screen management and UI components
├── settings.py          # Settings page and configuration management
├── plotter.py           # Core plotting and visualization functionality
├── dependencies.py      # Dependency management and installation
└── README.md           # This file
```

## Quick Start

### Option 1: Using the Launcher
```bash
python plotter/launcher.py
```

### Option 2: Direct Import
```python
from plotter import main
main()
```

### Option 3: Module Execution
```bash
python -m plotter.main
```

## Dependencies

The application automatically checks and installs required dependencies:

- **matplotlib**: For plotting and visualization
- **pandas**: For CSV data processing
- **numpy**: For numerical operations
- **Pillow**: For image processing
- **psutil**: For device hardware detection
- **requests**: For web functionality

## Usage

1. **Launch the Application**: Run the launcher script
2. **Select CSV File**: Choose a CSV file with bounding box data
3. **Configure Settings**: Adjust performance settings based on your hardware
4. **Visualize Data**: View and annotate bounding box data
5. **Save Results**: Export annotated data and plots

## CSV Format Requirements

Your CSV file must include these required columns:
- `image_id`: Unique identifier for each image
- `x_min`, `x_max`: Bounding box horizontal coordinates
- `y_min`, `y_max`: Bounding box vertical coordinates

Optional columns:
- `label_*`: Any columns starting with "label_" for annotations
- `*url*`: Any columns containing "url" for image URLs

## Performance Profiles

The application automatically detects your hardware and recommends optimal settings:

- **High Performance**: All features enabled for powerful systems
- **Balanced**: Recommended settings for most systems
- **Low-End Optimized**: Optimized for older or less powerful hardware
- **Custom**: Manual configuration of all settings

## Development

### Adding New Features

1. **UI Components**: Add to `ui_manager.py`
2. **Settings**: Extend `settings.py`
3. **Plotting**: Enhance `plotter.py`
4. **Dependencies**: Update `dependencies.py`

### Code Organization

- Each module has a specific responsibility
- Clear separation of concerns
- Consistent error handling and logging
- Professional code documentation

## License

Professional Edition - All rights reserved.

## Support

For technical support or feature requests, please contact the development team.
