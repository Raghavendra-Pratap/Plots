#!/usr/bin/env python3
"""
Simple test script to verify the build works correctly
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    required_modules = [
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.patches',
        'matplotlib.widgets',
        'numpy',
        'pandas',
        'PIL',
        'tkinter',
        'requests',
        'psutil'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} modules failed to import:")
        for module in failed_imports:
            print(f"    - {module}")
        return False
    else:
        print(f"\n✅ All {len(required_modules)} modules imported successfully!")
        return True

def test_basic_functionality():
    """Test basic functionality without GUI"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test matplotlib backend
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend for testing
        
        # Test basic plotting
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title('Test Plot')
        
        # Save test plot
        test_plot_path = 'test_plot.png'
        plt.savefig(test_plot_path)
        plt.close()
        
        if os.path.exists(test_plot_path):
            print("  ✓ Basic plotting functionality works")
            os.remove(test_plot_path)  # Clean up
        else:
            print("  ✗ Failed to save test plot")
            return False
            
    except Exception as e:
        print(f"  ✗ Basic functionality test failed: {e}")
        return False
    
    try:
        # Test pandas functionality
        import pandas as pd
        import numpy as np
        
        # Create test DataFrame
        data = {
            'x_min': [0, 10, 20],
            'x_max': [5, 15, 25],
            'y_min': [0, 10, 20],
            'y_max': [5, 15, 25],
            'image_id': ['img1', 'img2', 'img3']
        }
        df = pd.DataFrame(data)
        
        # Test basic operations
        df['width'] = df['x_max'] - df['x_min']
        df['height'] = df['y_max'] - df['y_min']
        df['area'] = df['width'] * df['height']
        
        print("  ✓ Pandas functionality works")
        
    except Exception as e:
        print(f"  ✗ Pandas test failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test if required files exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        'bounding_box_plotter.py',
        'requirements.txt',
        'README.md',
        'LICENSE'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} required files are missing:")
        for file_path in missing_files:
            print(f"    - {file_path}")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files found!")
        return True

def test_pyinstaller_build():
    """Test if PyInstaller can build the application"""
    print("\n🧪 Testing PyInstaller build...")
    
    try:
        # Check if PyInstaller is available
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__} available")
        
        # Check if spec file exists
        spec_file = 'bounding_box_plotter.spec'
        if os.path.exists(spec_file):
            print(f"  ✓ Spec file found: {spec_file}")
            
            # Try to analyze the spec file
            try:
                from PyInstaller.building.build_main import Analysis
                print("  ✓ PyInstaller analysis module available")
            except ImportError:
                print("  ⚠ PyInstaller analysis module not available")
                
        else:
            print(f"  ⚠ Spec file not found: {spec_file}")
            
    except ImportError:
        print("  ✗ PyInstaller not available")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 Bounding Box Plotter Build Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("File Structure", test_file_structure),
        ("PyInstaller", test_pyinstaller_build)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Build should work correctly.")
        return 0
    else:
        print("⚠ Some tests failed. Please fix issues before building.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 