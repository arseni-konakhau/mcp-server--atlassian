#!/usr/bin/env python3
"""
Simple dependency installer for MCP Atlassian testing.

This script installs the minimum required dependencies for testing
without requiring UV package manager.
"""

import subprocess
import sys
from pathlib import Path

def install_package(package: str) -> bool:
    """Install a package using pip."""
    try:
        print(f"Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_uv_available() -> bool:
    """Check if UV is available."""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ UV is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ UV is not available")
        return False

def install_with_uv() -> bool:
    """Install dependencies using UV."""
    try:
        print("Installing dependencies with UV...")
        result = subprocess.run(
            ["uv", "sync"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Dependencies installed with UV")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install with UV: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_minimal_deps() -> bool:
    """Install minimal dependencies for testing."""
    required_packages = [
        "python-dotenv",
        "click",
        "requests",
        "pydantic",
        "atlassian-python-api",
        "mcp"
    ]
    
    success = True
    for package in required_packages:
        if not install_package(package):
            success = False
    
    return success

def main():
    """Main entry point."""
    print("=== MCP Atlassian Dependency Installer ===")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Warning: pyproject.toml not found. Make sure you're in the project root directory.")
    
    # Try UV first if available
    if check_uv_available():
        if install_with_uv():
            print("\n✅ Dependencies installed successfully with UV!")
            print("You can now run: python3 simple_test.py --verbose")
            return
        else:
            print("\n⚠️  UV installation failed, falling back to pip...")
    
    # Fall back to pip
    print("\nInstalling minimal dependencies with pip...")
    if install_minimal_deps():
        print("\n✅ Minimal dependencies installed successfully!")
        print("You can now run: python3 simple_test.py --verbose")
        print("\nNote: For full functionality, consider installing UV:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
    else:
        print("\n❌ Failed to install some dependencies.")
        print("You may need to install them manually or use UV.")

if __name__ == "__main__":
    main()
