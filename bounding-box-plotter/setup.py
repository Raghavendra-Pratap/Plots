"""
Setup script for Bounding Box Plotter
"""

from setuptools import setup, find_packages
import os
import sys

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Professional tool for visualizing and annotating bounding box data from CSV files"

# Read version from version.py
def get_version():
    version_path = os.path.join(os.path.dirname(__file__), "version.py")
    if os.path.exists(version_path):
        with open(version_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"\'')
    return "2.0.0"

# Platform-specific dependencies
def get_platform_dependencies():
    if sys.platform == "win32":
        return ["pywin32>=300"]
    elif sys.platform == "darwin":
        return ["pyobjc-framework-Cocoa>=8.0"]
    elif sys.platform.startswith("linux"):
        return ["python-xlib>=0.29"]
    return []

setup(
    name="bounding-box-plotter",
    version=get_version(),
    author="Raghavendra Pratap",
    author_email="contact@raghavendrapratap.com",
    description="Professional tool for visualizing and annotating bounding box data from CSV files",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Raghavendra-Pratap/Plots",
    project_urls={
        "Bug Reports": "https://github.com/Raghavendra-Pratap/Plots/issues",
        "Source": "https://github.com/Raghavendra-Pratap/Plots",
        "Documentation": "https://raghavendrapratap.com/plots/docs",
        "Website": "https://raghavendrapratap.com/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: X11 Applications :: GTK",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "Pillow>=8.3.0",
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "PyUpdater>=4.0.0",
    ] + get_platform_dependencies(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "build": [
            "setuptools>=45.0.0",
            "wheel>=0.37.0",
            "twine>=3.4.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "icons": [
            "fontawesome>=0.0.1",
            "material-icons>=0.0.1",
            "feather-icons>=0.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "bounding-box-plotter=bounding_box_plotter:main",
            "bbp=bounding_box_plotter:main",
        ],
        "gui_scripts": [
            "bounding-box-plotter-gui=bounding_box_plotter:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
    },
    zip_safe=False,
    keywords=[
        "bounding box",
        "annotation",
        "computer vision",
        "data visualization",
        "CSV",
        "image processing",
        "machine learning",
        "data science",
        "GUI",
        "tkinter",
        "matplotlib",
        "pandas",
    ],
    platforms=[
        "Windows",
        "Linux",
        "macOS",
    ],
) 