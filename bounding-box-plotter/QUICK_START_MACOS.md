# 🚀 Quick Start Guide for macOS

This guide will help you build and test the Bounding Box Plotter on your MacBook.

## Prerequisites

1. **Python 3.9+** (recommended: Python 3.11)
2. **Homebrew** (for installing system dependencies)
3. **Git** (for version control)

## Step 1: Install System Dependencies

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and tkinter
brew install python-tk

# Verify Python installation
python3 --version
```

## Step 2: Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd bounding-box-plotter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install pyinstaller
```

## Step 3: Test the Build Environment

```bash
# Run the test script to verify everything works
python3 test_build.py
```

You should see all tests pass. If any fail, fix the issues before proceeding.

## Step 4: Build the Application

```bash
# Clean any previous builds
python3 build.py --clean

# Build the executable
python3 build.py

# Or use PyInstaller directly
pyinstaller bounding_box_plotter.spec
```

## Step 5: Test the Built Application

```bash
# Check what was created
ls -la dist/

# For macOS, you should see:
# - BoundingBoxPlotter.app (macOS app bundle)
# - BoundingBoxPlotter-Console (console version)

# Test the app bundle
open dist/BoundingBoxPlotter.app

# Or test from command line
./dist/BoundingBoxPlotter-Console/BoundingBoxPlotter-Console
```

## Step 6: Create Distribution Package

```bash
# Create installer package
python3 build.py --installer

# Or package for distribution
python3 build.py --all
```

## Troubleshooting

### Common Issues

1. **"No module named 'tkinter'"**
   ```bash
   brew install python-tk
   ```

2. **Matplotlib backend issues**
   ```bash
   pip install --upgrade matplotlib
   ```

3. **Permission denied errors**
   ```bash
   chmod +x build.py
   chmod +x test_build.py
   ```

4. **PyInstaller not found**
   ```bash
   pip install pyinstaller
   ```

### Build Verification

After building, verify the app bundle structure:

```bash
# Check app bundle contents
ls -la "dist/BoundingBoxPlotter.app/Contents/"

# Should contain:
# - MacOS/ (executable)
# - Resources/ (assets)
# - Info.plist (metadata)
```

### Testing the Built App

1. **Double-click** the `.app` file in Finder
2. **Right-click** → "Open" if you get a security warning
3. **Go to System Preferences** → Security & Privacy → Allow apps from identified developers

## Next Steps

1. **Test with real data**: Load a CSV file with bounding box data
2. **Customize icons**: Replace placeholder icons in `assets/` folder
3. **Set up auto-updates**: Configure PyUpdater for distribution
4. **Create GitHub release**: Tag your version and let GitHub Actions build for all platforms

## GitHub Actions (Optional)

If you want automated builds:

1. Push your code to GitHub
2. Create a tag: `git tag v2.0.0 && git push origin v2.0.0`
3. GitHub Actions will automatically build for macOS, Windows, and Linux
4. Download the built executables from the releases page

## Support

If you encounter issues:

1. Check the test output: `python3 test_build.py`
2. Review the build logs in the `build/` directory
3. Check PyInstaller documentation for your specific error
4. Open an issue on GitHub with detailed error information

---

**Happy Building! 🎉** 