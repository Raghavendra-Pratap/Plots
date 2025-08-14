# Bounding Box Plotter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/Raghavendra-Pratap/Plots/workflows/Build%20and%20Release/badge.svg)](https://github.com/Raghavendra-Pratap/Plots/actions)
[![PyPI version](https://badge.fury.io/py/bounding-box-plotter.svg)](https://badge.fury.io/py/bounding-box-plotter)
[![Downloads](https://pepy.tech/badge/bounding-box-plotter)](https://pepy.tech/project/bounding-box-plotter)

**Professional tool for visualizing and annotating bounding box data from CSV files**

## 🚀 Features

- **📊 Interactive Visualization**: Real-time bounding box plotting with matplotlib
- **🏷️ Smart Annotations**: Support for both X marks and numbered annotations
- **🖼️ Background Images**: Optional background image support for context
- **📱 Performance Profiles**: Adaptive performance settings for different hardware
- **🔄 Auto-Updates**: Built-in update system using PyUpdater
- **⌨️ Keyboard Shortcuts**: Professional keyboard navigation and shortcuts
- **💾 Multiple Export Formats**: Save as CSV, PNG, or JSON
- **🌐 Cross-Platform**: Windows, macOS, and Linux support
- **🔧 Professional Settings**: Comprehensive configuration options
- **📝 Comprehensive Logging**: Built-in logging and debugging tools

## 📋 Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 512MB RAM (2GB recommended)
- **Storage**: 100MB free space
- **OS**: Windows 10+, macOS 10.13+, or Linux (Ubuntu 18.04+)

## 🛠️ Installation

### Option 1: PyPI (Recommended)

```bash
pip install bounding-box-plotter
```

### Option 2: From Source

```bash
git clone https://github.com/Raghavendra-Pratap/Plots.git
cd Plots/bounding-box-plotter
pip install -r requirements.txt
python setup.py install
```

### Option 3: Pre-built Executables

Download the latest release from [GitHub Releases](https://github.com/Raghavendra-Pratap/Plots/releases)

## 🚀 Quick Start

### Basic Usage

```python
from bounding_box_plotter import main

# Run the application
main()
```

### Command Line

```bash
# Run the GUI version
bounding-box-plotter

# Run the console version
bounding-box-plotter --console

# Check for updates
bounding-box-plotter --check-updates
```

### CSV Format

Your CSV file must include these columns:
- `image_id`: Unique identifier for each image
- `x_min`, `x_max`, `y_min`, `y_max`: Bounding box coordinates

Optional columns:
- `label_*`: Any column starting with "label_" will be displayed on hover
- `marked`: Existing annotations (will be preserved)

Example CSV:
```csv
image_id,x_min,x_max,y_min,y_max,label_class,label_confidence
img001,100,200,150,250,car,0.95
img001,300,400,200,300,person,0.87
img002,50,150,100,200,bicycle,0.92
```

## 🔧 Configuration

### Performance Profiles

The application automatically detects your hardware and suggests optimal settings:

- **High Performance**: All features enabled (8+ cores, 16GB+ RAM)
- **Balanced**: Recommended for most users (4+ cores, 8GB+ RAM)
- **Low-End Optimized**: Performance-focused (2+ cores, 4GB+ RAM)

### Settings

Access settings through the welcome screen:
- Background image display
- Thumbnail quality
- Real-time hover labels
- Smooth animations
- Anti-aliasing
- Memory management
- Log retention

## ⌨️ Keyboard Shortcuts

### Navigation
- `←/→` or `A/D`: Navigate between images
- `Home/End`: Jump to first/last image
- `PageUp/PageDown`: Jump ±10 images
- `1-9`: Quick jump to specific image

### Actions
- `R`: Reset annotation counter
- `S`: Save annotations and data
- `L`: Toggle hover labels
- `F`: Flip Y-axis orientation
- `B`: Toggle background image
- `O` or `Enter`: Open image in browser
- `H`, `?`, or `F1`: Show help

### Native OS Shortcuts
- `Ctrl+Z` / `Cmd+Z`: Undo
- `Ctrl+Y` / `Cmd+Y`: Redo
- `Ctrl+S` / `Cmd+S`: Save

## 🔄 Auto-Updates

The application includes an automatic update system:

- **Automatic Checks**: Daily update checks (configurable)
- **Background Updates**: Non-intrusive update notifications
- **Multiple Channels**: Stable, beta, and alpha release channels
- **Fallback Support**: GitHub API fallback if PyUpdater unavailable

### Update Channels

- **Stable**: Production-ready releases (default)
- **Beta**: Pre-release testing versions
- **Alpha**: Early development versions

## 🏗️ Building from Source

### Prerequisites

```bash
pip install -r requirements.txt[dev]
pip install pyinstaller
```

### Build Commands

```bash
# Build executable only
python build.py

# Build everything (executable + installer + package)
python build.py --all

# Clean build artifacts
python build.py --clean

# Build Python package
python build.py --package

# Create installer
python build.py --installer
```

### Platform-Specific Builds

#### Windows
```bash
pyinstaller bounding_box_plotter.spec
```

#### macOS
```bash
pyinstaller bounding_box_plotter.spec
```

#### Linux
```bash
pyinstaller bounding_box_plotter.spec
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=bounding_box_plotter --cov-report=html

# Run specific test file
pytest tests/test_auto_updater.py -v
```

## 📦 Distribution

### GitHub Actions

The project includes automated CI/CD:
- **Automated Testing**: Multi-platform testing on push/PR
- **Automated Builds**: Cross-platform executable builds
- **Automated Releases**: GitHub releases on tag push
- **PyPI Publishing**: Automatic PyPI package publishing

### Release Process

1. **Version Update**: Update version in `version.py`
2. **Tag Release**: Create and push a version tag
3. **Automated Build**: GitHub Actions builds all platforms
4. **Release Creation**: GitHub release with assets
5. **PyPI Publishing**: Package published to PyPI

```bash
# Update version
git add version.py
git commit -m "Bump version to 2.0.1"
git tag v2.0.1
git push origin main --tags
```

## 🏗️ Project Structure

```
bounding-box-plotter/
├── bounding_box_plotter.py    # Main application
├── auto_updater.py            # Auto-update system
├── version.py                 # Version information
├── setup.py                   # Package setup
├── requirements.txt           # Dependencies
├── bounding_box_plotter.spec  # PyInstaller spec
├── pyupdater.yml             # PyUpdater config
├── build.py                   # Build script
├── .github/                   # GitHub Actions
│   └── workflows/
│       └── build.yml
├── tests/                     # Test suite
├── docs/                      # Documentation
└── assets/                    # Icons and resources
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/Raghavendra-Pratap/Plots.git
cd bounding-box-plotter
pip install -r requirements.txt[dev]
pre-commit install
```

### Code Style

- **Formatting**: Black
- **Linting**: Flake8
- **Type Checking**: MyPy
- **Testing**: Pytest

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Matplotlib**: For powerful plotting capabilities
- **Pandas**: For efficient data handling
- **PyUpdater**: For automatic update functionality
- **Tkinter**: For cross-platform GUI
- **PyInstaller**: For executable packaging

## 📞 Support

- **Documentation**: [https://raghavendrapratap.com/bounding-box-plotter/docs](https://raghavendrapratap.com/bounding-box-plotter/docs)
- **Issues**: [GitHub Issues](https://github.com/Raghavendra-Pratap/Plots/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Raghavendra-Pratap/Plots/discussions)
- **Email**: contact@raghavendrapratap.com
- **Website**: [https://raghavendrapratap.com](https://raghavendrapratap.com)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete history of changes.

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/Raghavendra-Pratap/Plots)
![GitHub forks](https://img.shields.io/github/forks/Raghavendra-Pratap/Plots)
![GitHub issues](https://img.shields.io/github/issues/Raghavendra-Pratap/Plots)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Raghavendra-Pratap/Plots)

---

**Made with ❤️ by [Raghavendra Pratap](https://raghavendrapratap.com)**

*If you find this project helpful, please consider giving it a ⭐ star on GitHub!* 