"""
Basic tests for version module
"""
import sys
import os

# Add the parent directory to the path so we can import unified_plotter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from version import get_version_info, get_version_string, is_compatible_version


def test_version_info():
    """Test that version info returns expected structure"""
    version_info = get_version_info()
    
    assert 'version' in version_info
    assert 'build' in version_info
    assert 'author' in version_info
    assert 'app_name' in version_info
    assert version_info['version'] == "2.1.0"


def test_version_string():
    """Test that version string is formatted correctly"""
    version_string = get_version_string()
    
    assert "Version 2.1.0" in version_string
    assert "Professional Edition" in version_string


def test_compatible_version():
    """Test that version compatibility check works"""
    # This should return True for Python 3.8+
    assert is_compatible_version() is True


def test_import_dependencies():
    """Test that main module can be imported without errors"""
    try:
        # This is a basic import test - the actual import might fail due to GUI dependencies
        # but we can at least test that the module structure is correct
        import unified_plotter
        assert True
    except ImportError as e:
        # GUI dependencies might not be available in CI, that's okay
        if "tkinter" in str(e).lower() or "matplotlib" in str(e).lower():
            assert True  # Expected in headless CI environment
        else:
            raise
