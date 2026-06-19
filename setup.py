#!/usr/bin/env python3
import os
import sys

def create_structure():
    """Create project structure"""
    print("📁 Creating project structure...")
    
    directories = [
        'backend/api',
        'backend/services',
        'ml/preprocessing',
        'ml/training',
        'ml/models',
        'frontend/js',
        'config',
        'data/raw'
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}")
    
    # Create __init__.py files
    init_files = [
        'backend/__init__.py',
        'backend/api/__init__.py',
        'backend/services/__init__.py',
        'ml/__init__.py',
        'ml/preprocessing/__init__.py',
        'ml/training/__init__.py'
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('')
        print(f"  Created: {init_file}")
    
    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Place your training.csv and testing.csv in data/raw/")
    print("2. Run: python run.py")
    print("3. Open: http://localhost:8000/dashboard.html")

if __name__ == "__main__":
    create_structure()