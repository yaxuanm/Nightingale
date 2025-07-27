#!/usr/bin/env python3
"""
Test script to verify path resolution fixes
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import get_audio_output_path

def test_path_resolution():
    """Test the path resolution function"""
    print("Testing path resolution...")
    
    # Test with a simple filename
    test_filename = "test_audio.wav"
    result_path = get_audio_output_path(test_filename)
    
    print(f"Test filename: {test_filename}")
    print(f"Result path: {result_path}")
    print(f"Path exists: {os.path.exists(result_path)}")
    print(f"Directory exists: {os.path.exists(os.path.dirname(result_path))}")
    
    # Test with a more complex filename
    test_filename2 = "stable_long_test_1234567890abcdef.wav"
    result_path2 = get_audio_output_path(test_filename2)
    
    print(f"\nTest filename 2: {test_filename2}")
    print(f"Result path 2: {result_path2}")
    print(f"Path exists: {os.path.exists(result_path2)}")
    print(f"Directory exists: {os.path.exists(os.path.dirname(result_path2))}")
    
    # Test current working directory
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

if __name__ == "__main__":
    test_path_resolution() 