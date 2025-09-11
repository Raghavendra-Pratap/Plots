"""
Setup script for Unified Plotter
"""
from setuptools import setup, find_packages
import os

# Read version from version.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'version.py')
    with open(version_file, 'r') as f:
        exec(f.read())
    return locals()['__version__']

# Read README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Professional tool for visualizing and annotating bounding box data from CSV files"

# Read requirements
def get_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="unified-plotter",
    version=get_version(),
    author="Raghavendra Pratap",
    author_email="contact@raghavendrapratap.com",
    description="Professional tool for visualizing and annotating bounding box data from CSV files",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Raghavendra-Pratap/Plotter",
    project_urls={
        "Bug Reports": "https://github.com/Raghavendra-Pratap/Plotter/issues",
        "Source": "https://github.com/Raghavendra-Pratap/Plotter",
        "Documentation": "https://github.com/Raghavendra-Pratap/Plotter/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "unified-plotter=unified_plotter.unified_plotter:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="bounding box, annotation, computer vision, data visualization, CSV, matplotlib",
)
