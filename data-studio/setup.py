#!/usr/bin/env python3
"""
Setup script for Unified Data Studio
Python PySide6 desktop application
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Unified Data Studio - Python PySide6 Version"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="unified-data-studio",
    version="1.0.0",
    description="Unified Data Studio - Cross-platform desktop application for data processing and analytics",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Unified Data Studio Team",
    author_email="team@unifieddatastudio.com",
    url="https://github.com/unifieddatastudio/unified-data-studio",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Office/Business",
    ],
    entry_points={
        'console_scripts': [
            'unified-data-studio=main:main',
        ],
    },
    keywords="data-science analytics workflow database duckdb sqlite",
    project_urls={
        "Bug Reports": "https://github.com/unifieddatastudio/unified-data-studio/issues",
        "Source": "https://github.com/unifieddatastudio/unified-data-studio",
        "Documentation": "https://unifieddatastudio.readthedocs.io/",
    },
)
