#!/usr/bin/env python3
"""
Simple test script to verify the build process works locally
"""
import sys
import os
import subprocess


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import pandas

        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False

    try:
        import matplotlib

        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False

    try:
        import numpy

        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False

    try:
        from PIL import Image

        print("✓ PIL imported successfully")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        return False

    return True


def test_version_module():
    """Test the version module"""
    print("\nTesting version module...")
    try:
        from version import get_version_info, get_version_string

        version_info = get_version_info()
        version_string = get_version_string()
        print(f"✓ Version info: {version_info['version']}")
        print(f"✓ Version string: {version_string}")
        return True
    except Exception as e:
        print(f"✗ Version module test failed: {e}")
        return False


def test_main_module():
    """Test that the main module can be imported (without running GUI)"""
    print("\nTesting main module import...")
    try:
        # Import the main script directly
        import unified_plotter

        print("✓ Main module imported successfully")
        return True
    except ImportError:
        # Try importing the script file directly
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "unified_plotter", "unified-plotter.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✓ Main script loaded successfully")
            return True
        except Exception as e:
            print(f"✗ Main module import failed: {e}")
            return False
    except Exception as e:
        print(f"✗ Main module import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Running local build tests...\n")

    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_version_module()
    all_passed &= test_main_module()

    print(f"\n{'='*50}")
    if all_passed:
        print("✓ All tests passed! Build should work in CI.")
    else:
        print("✗ Some tests failed. Check the errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
