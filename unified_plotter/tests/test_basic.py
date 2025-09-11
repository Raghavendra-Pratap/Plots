"""
Basic tests that should work in CI environment
"""
import sys
import os

# Add the parent directory to the path so we can import unified_plotter
if '__file__' in globals():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
else:
    sys.path.insert(0, '..')


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


def main():
    """Run all basic tests"""
    print("Running basic tests...\n")
    
    try:
        test_python_version()
        print("✓ Python version check passed")
        
        test_required_modules()
        print("✓ Required modules test passed")
        
        test_tkinter_availability()
        print("✓ Tkinter availability check passed")
        
        test_version_module()
        print("✓ Version module test passed")
        
        test_file_structure()
        print("✓ File structure test passed")
        
        print("\n✅ All basic tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
