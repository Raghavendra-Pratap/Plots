# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the directory containing this spec file
SPEC_DIR = Path(__file__).parent

# Block cipher for PyUpdater
block_cipher = None

# Analysis
a = Analysis(
    [SPEC_DIR / 'bounding_box_plotter.py'],
    pathex=[SPEC_DIR],
    binaries=[],
    datas=[
        (SPEC_DIR / 'version.py', '.'),
        (SPEC_DIR / 'auto_updater.py', '.'),
        (SPEC_DIR / 'README.md', '.'),
        (SPEC_DIR / 'CHANGELOG.md', '.'),
        (SPEC_DIR / 'LICENSE', '.'),
    ],
    hiddenimports=[
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.widgets',
        'matplotlib.patches',
        'matplotlib.transforms',
        'matplotlib.image',
        'matplotlib.gridspec',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.font',
        'pandas',
        'numpy',
        'requests',
        'psutil',
        'webbrowser',
        'json',
        'logging',
        'tempfile',
        'shutil',
        'subprocess',
        'threading',
        'time',
        'datetime',
        'io',
        'hashlib',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
        'profile',
        'cProfile',
        'trace',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
        'twine',
        'sphinx',
        'pytest',
        'black',
        'flake8',
        'mypy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Pyz
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BoundingBoxPlotter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for console version
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=SPEC_DIR / 'assets' / 'icon.ico' if (SPEC_DIR / 'assets' / 'icon.ico').exists() else None,
    version=SPEC_DIR / 'version_info.txt' if (SPEC_DIR / 'version_info.txt').exists() else None,
)

# Console version (optional)
exe_console = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BoundingBoxPlotter-Console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console version
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=SPEC_DIR / 'assets' / 'icon.ico' if (SPEC_DIR / 'assets' / 'icon.ico').exists() else None,
    version=SPEC_DIR / 'version_info.txt' if (SPEC_DIR / 'version_info.txt').exists() else None,
)

# Collection
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BoundingBoxPlotter',
)

# Console collection
coll_console = COLLECT(
    exe_console,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BoundingBoxPlotter-Console',
)

# Platform-specific adjustments
if sys.platform == 'win32':
    # Windows-specific settings
    exe.icon = SPEC_DIR / 'assets' / 'icon.ico' if (SPEC_DIR / 'assets' / 'icon.ico').exists() else None
    exe_console.icon = SPEC_DIR / 'assets' / 'icon.ico' if (SPEC_DIR / 'assets' / 'icon.ico').exists() else None
    
elif sys.platform == 'darwin':
    # macOS-specific settings
    exe.icon = SPEC_DIR / 'assets' / 'icon.icns' if (SPEC_DIR / 'assets' / 'icon.icns').exists() else None
    exe_console.icon = SPEC_DIR / 'assets' / 'icon.icns' if (SPEC_DIR / 'assets' / 'icon.icns').exists() else None
    
    # macOS app bundle
    app = BUNDLE(
        coll,
        name='BoundingBoxPlotter.app',
        icon=SPEC_DIR / 'assets' / 'icon.icns' if (SPEC_DIR / 'assets' / 'icon.icns').exists() else None,
        bundle_identifier='com.raghavendrapratap.boundingboxplotter',
        info_plist={
            'CFBundleName': 'Bounding Box Plotter',
            'CFBundleDisplayName': 'Bounding Box Plotter',
            'CFBundleIdentifier': 'com.raghavendrapratap.boundingboxplotter',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'LSMinimumSystemVersion': '10.13.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
    )
    
elif sys.platform.startswith('linux'):
    # Linux-specific settings
    exe.icon = SPEC_DIR / 'assets' / 'icon.png' if (SPEC_DIR / 'assets' / 'icon.png').exists() else None
    exe_console.icon = SPEC_DIR / 'assets' / 'icon.png' if (SPEC_DIR / 'assets' / 'icon.png').exists() else None

# Add PyUpdater support
if 'PyUpdater' in str(a.hiddenimports):
    # Include PyUpdater files
    a.datas += [
        (SPEC_DIR / 'updates' / '*.json', 'updates'),
        (SPEC_DIR / 'updates' / '*.py', 'updates'),
    ] 