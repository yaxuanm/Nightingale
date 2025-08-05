#!/usr/bin/env python3
"""
Dependency Check Script for Nightingale Project
This script verifies that all required dependencies are properly installed.
"""

import sys
import importlib
import subprocess
import os

def check_package(package_name, version=None):
    """Check if a package is installed and optionally verify version"""
    try:
        module = importlib.import_module(package_name)
        if version:
            # Try to get version from module
            if hasattr(module, '__version__'):
                installed_version = module.__version__
                print(f"✓ {package_name} {installed_version}")
                return True
            else:
                print(f"✓ {package_name} (version unknown)")
                return True
        else:
            print(f"✓ {package_name}")
            return True
    except ImportError:
        print(f"✗ {package_name} - NOT FOUND")
        return False

def check_critical_packages():
    """Check critical packages for the project"""
    print("=== Checking Critical Dependencies ===")
    
    critical_packages = [
        # Core Framework
        ("fastapi", "0.116.0"),
        ("uvicorn", "0.35.0"),
        
        # AI/ML Libraries
        ("torch", "2.7.1"),
        ("torchaudio", "2.7.1"),
        ("transformers", "4.53.1"),
        
        # Audio Processing
        ("pydub", "0.25.1"),
        ("librosa", "0.11.0"),
        ("stable_audio_tools", "0.0.19"),
        
        # Google AI
        ("google.genai", "1.27.0"),
        
        # Database
        ("supabase", "2.16.0"),
        
        # Utilities
        ("python_dotenv", "1.1.1"),
        ("requests", "2.32.4"),
        ("pillow", "11.3.0"),
        ("numpy", "1.23.5"),
    ]
    
    all_found = True
    for package, version in critical_packages:
        if not check_package(package, version):
            all_found = False
    
    return all_found

def check_optional_packages():
    """Check optional packages"""
    print("\n=== Checking Optional Dependencies ===")
    
    optional_packages = [
        "edge_tts",
        "soundfile",
        "noisereduce",
        "torchlibrosa",
        "accelerate",
        "huggingface_hub",
    ]
    
    for package in optional_packages:
        check_package(package)

def check_python_version():
    """Check Python version"""
    print("\n=== Python Version ===")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 11:
        print("✓ Python 3.11 - Compatible")
        return True
    else:
        print(f"⚠ Python {version.major}.{version.minor} - May have compatibility issues")
        print("   Recommended: Python 3.11")
        return False

def check_ffmpeg():
    """Check if FFmpeg is available"""
    print("\n=== FFmpeg Check ===")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg is available")
            return True
        else:
            print("✗ FFmpeg not found or not working")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ FFmpeg not found in PATH")
        print("   Please install FFmpeg and add it to your PATH")
        return False

def main():
    """Main dependency check function"""
    print("Nightingale Dependency Checker")
    print("=" * 40)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check critical packages
    packages_ok = check_critical_packages()
    
    # Check optional packages
    check_optional_packages()
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print(f"Python Version: {'✓' if python_ok else '✗'}")
    print(f"Critical Packages: {'✓' if packages_ok else '✗'}")
    print(f"FFmpeg: {'✓' if ffmpeg_ok else '✗'}")
    
    if python_ok and packages_ok and ffmpeg_ok:
        print("\n🎉 All dependencies are properly installed!")
        return 0
    else:
        print("\n⚠ Some dependencies are missing or incompatible.")
        print("Please install missing dependencies and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 