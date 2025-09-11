# Unified Plotter

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/Raghavendra-Pratap/Plotter/workflows/CI/badge.svg)](https://github.com/Raghavendra-Pratap/Plotter/actions)
[![Downloads](https://img.shields.io/github/downloads/Raghavendra-Pratap/Plotter/total.svg)](https://github.com/Raghavendra-Pratap/Plotter/releases)

Professional tool for visualizing and annotating bounding box data from CSV files with enterprise-grade features.

## Features

- 🎯 **Real-time Bounding Box Visualization** - Interactive plotting with matplotlib
- 📊 **CSV Data Processing** - Direct import from CSV files with validation
- ⚙️ **Performance Profiles** - Optimized for different hardware configurations
- 🎨 **Feature Toggles** - Customizable UI and performance settings
- 💾 **Memory Management** - Efficient handling of large datasets
- 🔄 **Auto-update System** - Built-in update checking and delivery
- 🌐 **Cross-platform** - Works on Windows, macOS, and Linux
- 📱 **Modern GUI** - Professional dark theme interface

## Requirements

- Python 3.8 or higher
- 512MB RAM minimum (2GB recommended)
- CSV files with required columns: `image_id`, `x_min`, `x_max`, `y_min`, `y_max`

## Installation

### From Source
```bash
git clone https://github.com/Raghavendra-Pratap/Plotter.git
cd Plotter/unified_plotter
pip install -r requirements.txt
python unified_plotter.py
```

### Using pip (when published)
```bash
pip install unified-plotter
unified-plotter
```

## Usage

1. **Launch the Application**
   ```bash
   python unified_plotter.py
   ```

2. **Select CSV File**
   - Click "Select CSV File" button
   - Choose a CSV file with bounding box data
   - Required columns: `image_id`, `x_min`, `x_max`, `y_min`, `y_max`

3. **Configure Settings**
   - Click "Settings" to access performance profiles
   - Adjust feature toggles based on your hardware
   - Save settings for future use

4. **Visualize Data**
   - Interactive plot window opens automatically
   - Navigate through images using controls
   - Export annotated plots as needed

## CSV Format

Your CSV file should contain the following columns:

| Column | Description | Required |
|--------|-------------|----------|
| `image_id` | Unique identifier for each image | ✅ |
| `x_min` | Left boundary of bounding box | ✅ |
| `x_max` | Right boundary of bounding box | ✅ |
| `y_min` | Top boundary of bounding box | ✅ |
| `y_max` | Bottom boundary of bounding box | ✅ |
| `label_*` | Optional label columns | ❌ |
| `image_url` | Optional image URL column | ❌ |

## Performance Profiles

- **High Performance** - All features enabled, recommended for powerful systems
- **Balanced** - Optimized for average hardware (default)
- **Low-End Optimized** - Minimal features for older systems
- **Custom** - Manual configuration of individual features

## Development

### Setting up Development Environment
```bash
git clone https://github.com/Raghavendra-Pratap/Plotter.git
cd Plotter/unified_plotter
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
pytest tests/
```

### Building Executables
```bash
# Using PyInstaller
pyinstaller --onefile --windowed unified_plotter.py

# Using cx_Freeze
python setup.py build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: contact@raghavendrapratap.com
- 🐛 Issues: [GitHub Issues](https://github.com/Raghavendra-Pratap/Plotter/issues)
- 📖 Documentation: [Wiki](https://github.com/Raghavendra-Pratap/Plotter/wiki)

## Changelog

### Version 2.1.0
- ✅ Fixed settings page navigation issues
- ✅ Improved logo positioning and layout
- ✅ Added proper version management system
- ✅ Enhanced cross-platform compatibility
- ✅ Optimized memory management
- ✅ Added auto-update functionality

### Version 2.0.0
- 🎉 Initial release with core functionality
- 🎯 Real-time bounding box visualization
- ⚙️ Performance profiles and settings
- 🎨 Modern dark theme interface

## Acknowledgments

- Built with [matplotlib](https://matplotlib.org/) for visualization
- Powered by [pandas](https://pandas.pydata.org/) for data processing
- GUI created with [tkinter](https://docs.python.org/3/library/tkinter.html)
