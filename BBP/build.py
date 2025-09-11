#!/usr/bin/env python3
"""
Build script for Bounding Box Plotter
Automates the build process for different platforms
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import argparse

def run_command(command, cwd=None, shell=False):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pyinstaller', 'setuptools', 'wheel']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        run_command([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    
    return True

def clean_build():
    """Clean build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec', '*.log']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Cleaned {dir_name}")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            file_path.unlink()
            print(f"✓ Cleaned {file_path}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Use the spec file if it exists
    spec_file = 'bounding_box_plotter.spec'
    if os.path.exists(spec_file):
        result = run_command(['pyinstaller', spec_file, '--clean'])
    else:
        # Fallback to basic PyInstaller command
        result = run_command([
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name=BoundingBoxPlotter',
            'bounding_box_plotter.py'
        ])
    
    if result is not None:
        print("✓ Executable built successfully")
        return True
    else:
        print("✗ Failed to build executable")
        return False

def create_installer():
    """Create installer for the application"""
    system = platform.system().lower()
    
    if system == 'windows':
        return create_windows_installer()
    elif system == 'darwin':
        return create_macos_installer()
    elif system == 'linux':
        return create_linux_installer()
    else:
        print(f"⚠ Unsupported platform: {system}")
        return False

def create_windows_installer():
    """Create Windows installer using NSIS"""
    print("🔨 Creating Windows installer...")
    
    # Check if NSIS is available
    nsis_path = shutil.which('makensis')
    if not nsis_path:
        print("⚠ NSIS not found. Installer creation skipped.")
        return False
    
    # Create NSIS script
    nsis_script = create_nsis_script()
    
    # Run NSIS
    result = run_command(['makensis', nsis_script])
    if result:
        print("✓ Windows installer created successfully")
        return True
    else:
        print("✗ Failed to create Windows installer")
        return False

def create_nsis_script():
    """Create NSIS installer script"""
    script_content = """
!include "MUI2.nsh"

Name "Bounding Box Plotter"
OutFile "BoundingBoxPlotter-Setup.exe"
InstallDir "$PROGRAMFILES\\BoundingBoxPlotter"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\\BoundingBoxPlotter\\*.*"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\BoundingBoxPlotter"
    CreateShortCut "$SMPROGRAMS\\BoundingBoxPlotter\\BoundingBoxPlotter.lnk" "$INSTDIR\\BoundingBoxPlotter.exe"
    CreateShortCut "$SMPROGRAMS\\BoundingBoxPlotter\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BoundingBoxPlotter" "DisplayName" "Bounding Box Plotter"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BoundingBoxPlotter" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir /r "$INSTDIR"
    
    Delete "$SMPROGRAMS\\BoundingBoxPlotter\\BoundingBoxPlotter.lnk"
    Delete "$SMPROGRAMS\\BoundingBoxPlotter\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\BoundingBoxPlotter"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BoundingBoxPlotter"
SectionEnd
"""
    
    with open('installer.nsi', 'w') as f:
        f.write(script_content)
    
    return 'installer.nsi'

def create_macos_installer():
    """Create macOS installer using pkgbuild"""
    print("🔨 Creating macOS installer...")
    
    # Check if pkgbuild is available
    if not shutil.which('pkgbuild'):
        print("⚠ pkgbuild not found. Installer creation skipped.")
        return False
    
    # Create package
    result = run_command([
        'pkgbuild',
        '--root', 'dist/BoundingBoxPlotter.app',
        '--identifier', 'com.raghavendrapratap.boundingboxplotter',
        '--version', '2.0.0',
        '--install-location', '/Applications',
        'BoundingBoxPlotter.pkg'
    ])
    
    if result:
        print("✓ macOS installer created successfully")
        return True
    else:
        print("✗ Failed to create macOS installer")
        return False

def create_linux_installer():
    """Create Linux installer using AppImage"""
    print("🔨 Creating Linux AppImage...")
    
    # Check if appimagetool is available
    if not shutil.which('appimagetool'):
        print("⚠ appimagetool not found. AppImage creation skipped.")
        return False
    
    # Create AppDir structure
    appdir = Path('AppDir')
    appdir.mkdir(exist_ok=True)
    
    # Copy executable and dependencies
    shutil.copytree('dist/BoundingBoxPlotter', appdir / 'usr' / 'bin', dirs_exist_ok=True)
    
    # Create desktop file
    desktop_content = """[Desktop Entry]
Name=Bounding Box Plotter
Comment=Professional tool for visualizing and annotating bounding box data
Exec=BoundingBoxPlotter
Icon=BoundingBoxPlotter
Terminal=false
Type=Application
Categories=Graphics;Science;Education;
"""
    
    (appdir / 'usr' / 'share' / 'applications').mkdir(parents=True, exist_ok=True)
    with open(appdir / 'usr' / 'share' / 'applications' / 'bounding-box-plotter.desktop', 'w') as f:
        f.write(desktop_content)
    
    # Create AppImage
    result = run_command(['appimagetool', 'AppDir', 'BoundingBoxPlotter-x86_64.AppImage'])
    
    if result:
        print("✓ Linux AppImage created successfully")
        return True
    else:
        print("✗ Failed to create Linux AppImage")
        return False

def package_for_distribution():
    """Package the application for distribution"""
    print("📦 Packaging for distribution...")
    
    system = platform.system().lower()
    version = "2.0.0"  # Get from version.py
    
    if system == 'windows':
        # Create ZIP archive
        shutil.make_archive(f'BoundingBoxPlotter-Windows-{version}', 'zip', 'dist', 'BoundingBoxPlotter')
        print("✓ Windows package created")
        
    elif system == 'darwin':
        # Create ZIP archive
        shutil.make_archive(f'BoundingBoxPlotter-macOS-{version}', 'zip', 'dist', 'BoundingBoxPlotter.app')
        print("✓ macOS package created")
        
    elif system == 'linux':
        # Create tar.gz archive
        shutil.make_archive(f'BoundingBoxPlotter-Linux-{version}', 'gztar', 'dist', 'BoundingBoxPlotter')
        print("✓ Linux package created")

def build_python_package():
    """Build Python package for PyPI"""
    print("🐍 Building Python package...")
    
    # Clean previous builds
    for pattern in ['dist/*', 'build/*', '*.egg-info']:
        for path in Path('.').glob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    
    # Build package
    result = run_command([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'])
    
    if result:
        print("✓ Python package built successfully")
        return True
    else:
        print("✗ Failed to build Python package")
        return False

def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description='Build Bounding Box Plotter')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument('--package', action='store_true', help='Build Python package')
    parser.add_argument('--installer', action='store_true', help='Create installer')
    parser.add_argument('--all', action='store_true', help='Build everything')
    
    args = parser.parse_args()
    
    print("🚀 Bounding Box Plotter Build Script")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("✗ Failed to check dependencies")
        return 1
    
    # Clean if requested
    if args.clean or args.all:
        clean_build()
    
    # Build executable
    if not build_executable():
        return 1
    
    # Create installer if requested
    if args.installer or args.all:
        create_installer()
    
    # Package for distribution
    package_for_distribution()
    
    # Build Python package if requested
    if args.package or args.all:
        build_python_package()
    
    print("\n🎉 Build completed successfully!")
    print("📁 Output files are in the 'dist' directory")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 