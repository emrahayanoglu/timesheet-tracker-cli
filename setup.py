#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="timesheet-tracker",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple CLI tool for tracking working time and generating PDF reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/timesheet-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "click>=8.0.0",
        "reportlab>=3.6.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "timesheet-tracker=cli:cli",
        ],
    },
    include_package_data=True,
)
