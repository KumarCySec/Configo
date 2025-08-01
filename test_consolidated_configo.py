#!/usr/bin/env python3
"""
Test script for the consolidated CONFIGO application.
"""

import subprocess
import sys
import os

def test_configo_help():
    """Test that configo.py --help works."""
    try:
        result = subprocess.run([sys.executable, 'configo.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ configo.py --help works correctly")
            return True
        else:
            print(f"❌ configo.py --help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing configo.py --help: {e}")
        return False

def test_configo_scan():
    """Test that configo.py scan works."""
    try:
        result = subprocess.run([sys.executable, 'configo.py', 'scan'], 
                              capture_output=True, text=True, timeout=30)
        # Scan should work even if no project is found
        if result.returncode == 0 or "No project found" in result.stdout:
            print("✅ configo.py scan works correctly")
            return True
        else:
            print(f"❌ configo.py scan failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing configo.py scan: {e}")
        return False

def test_configo_diagnostics():
    """Test that configo.py diagnostics works."""
    try:
        result = subprocess.run([sys.executable, 'configo.py', 'diagnostics'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ configo.py diagnostics works correctly")
            return True
        else:
            print(f"❌ configo.py diagnostics failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing configo.py diagnostics: {e}")
        return False

def test_configo_executable():
    """Test that configo.py is executable."""
    try:
        if os.access('configo.py', os.X_OK):
            print("✅ configo.py is executable")
            return True
        else:
            print("❌ configo.py is not executable")
            return False
    except Exception as e:
        print(f"❌ Error checking configo.py executable: {e}")
        return False

def test_symlink():
    """Test that the symlink was created."""
    try:
        symlink_path = os.path.expanduser("~/.local/bin/configo")
        if os.path.islink(symlink_path):
            print("✅ configo symlink created successfully")
            return True
        else:
            print("❌ configo symlink not found")
            return False
    except Exception as e:
        print(f"❌ Error checking symlink: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Consolidated CONFIGO Application")
    print("=" * 50)
    
    tests = [
        ("Executable Check", test_configo_executable),
        ("Help Command", test_configo_help),
        ("Scan Command", test_configo_scan),
        ("Diagnostics Command", test_configo_diagnostics),
        ("Symlink Check", test_symlink),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CONFIGO is ready to use.")
        print("\n🚀 Try these commands:")
        print("  configo                    # Interactive mode")
        print("  configo setup             # Full setup")
        print("  configo chat              # AI chat")
        print("  configo scan              # Project analysis")
        print("  configo install vscode    # App installation")
        print("  configo diagnostics       # System check")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 