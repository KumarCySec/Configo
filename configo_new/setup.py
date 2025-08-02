"""
CONFIGO Setup Script
====================

Setup script for installing CONFIGO as a Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    """Read the README file."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="configo",
    version="1.0.0",
    author="CONFIGO Team",
    author_email="support@configo.dev",
    description="Autonomous AI Setup Agent - Professional CLI agent for intelligent development environment setup",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/configo",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/configo/issues",
        "Documentation": "https://docs.configo.dev",
        "Source Code": "https://github.com/yourusername/configo",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Installation/Setup",
        "Topic :: Utilities",
    ],
    package_dir={"": "."},
    packages=find_packages(include=["core", "agent", "knowledge", "memory", "ui"]),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "configo=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="development, setup, automation, ai, cli, tools, installation",
    license="MIT",
    platforms=["linux", "unix"],
) 