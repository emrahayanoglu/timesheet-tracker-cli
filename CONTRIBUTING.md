# Contributing to Timesheet Tracker

Thank you for your interest in contributing to Timesheet Tracker! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/timesheet-tracker.git
   cd timesheet-tracker
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Setup

1. Install development dependencies:
   ```bash
   pip install pytest black flake8
   ```

2. Run tests (when available):
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black *.py
   ```

4. Check code style:
   ```bash
   flake8 *.py
   ```

## Making Changes

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Test your changes thoroughly
4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request

## Code Style

- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add comments for complex logic

## Reporting Issues

When reporting issues, please include:
- Your operating system
- Python version
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages

## Feature Requests

Feature requests are welcome! Please:
- Check if the feature already exists
- Describe the use case
- Explain why it would be beneficial
- Consider providing a implementation plan

## Debian Package Development

To work on the Debian package:

1. Install build dependencies:
   ```bash
   sudo apt install build-essential debhelper python3-all python3-setuptools dh-python
   ```

2. Build the package:
   ```bash
   ./build-simple.sh
   ```

3. Test the package:
   ```bash
   sudo dpkg -i timesheet-tracker_*.deb
   timesheet --help
   ```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
