#!/usr/bin/env python3
"""
Installation script for Python 3.13 compatibility
"""
import subprocess
import sys

def install_packages():
    """Install packages with Python 3.13 compatibility"""
    packages = [
        "flask==2.3.3",
        "gunicorn==21.2.0", 
        "requests==2.31.0",
        "pytesseract==0.3.10",
        "pdf2image==1.16.3",
        "pypdf2==3.0.1",
        "regex==2023.12.25",
        "python-multipart==0.0.6"
    ]
    
    # Try to install Pillow separately
    try:
        print("Installing Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow==10.2.0"])
        print("✓ Pillow installed successfully")
    except subprocess.CalledProcessError:
        print("⚠ Pillow installation failed, continuing without it...")
    
    # Install other packages
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")

if __name__ == "__main__":
    install_packages()