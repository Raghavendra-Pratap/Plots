"""
Basic tests that should work in CI environment
"""
import sys
import os

# Add the parent directory to the path so we can import unified_plotter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_python_version():
    """Test that we're running on a supported Python version"""
    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"


def test_required_modules():
    """Test that required modules can be imported"""
    try:
        import pandas
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        raise
    
    try:
        import matplotlib
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        raise
    
    try:
        import numpy
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        raise
    
    try:
        from PIL import Image
        print("✓ PIL imported successfully")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        raise


def test_tkinter_availability():
    """Test tkinter availability (may not be available in headless CI)"""
    try:
        import tkinter
        print("✓ tkinter available")
        return True
    except ImportError:
        print("⚠ tkinter not available (expected in headless CI)")
        return False


def test_version_module():
    """Test version module works"""
    try:
        from version import get_version_info, get_version_string
        version_info = get_version_info()
        version_string = get_version_string()
        
        assert 'version' in version_info
        assert 'build' in version_info
        assert version_info['version'] == "2.1.0"
        
        print(f"✓ Version info: {version_info['version']}")
        print(f"✓ Version string: {version_string}")
        return True
    except Exception as e:
        print(f"✗ Version module test failed: {e}")
        raise


def test_file_structure():
    """Test that required files exist"""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    required_files = [
        'unified-plotter.py',
        'version.py',
        'requirements.txt',
        'setup.py',
        'README.md'
    ]
    
    for file_name in required_files:
        file_path = os.path.join(base_dir, file_name)
        assert os.path.exists(file_path), f"Required file {file_name} not found"
        print(f"✓ {file_name} exists")
    
    return True
