#!/usr/bin/env python3
"""
Test script for CONFIGO's app name extraction functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app_name_extractor import AppNameExtractor

def test_app_name_extraction():
    """Test app name extraction with various input patterns."""
    
    test_cases = [
        # Basic cases
        ("install telegram", "Telegram"),
        ("get me discord", "Discord"),
        ("i need chrome", "Google Chrome"),
        ("download firefox", "Firefox"),
        ("add slack", "Slack"),
        ("setup zoom", "Zoom"),
        
        # With "me" in the middle
        ("get me telegram", "Telegram"),
        ("install me discord", "Discord"),
        ("need me chrome", "Google Chrome"),
        ("want me firefox", "Firefox"),
        
        # With please
        ("please install telegram", "Telegram"),
        ("install telegram please", "Telegram"),
        ("please get me discord", "Discord"),
        
        # Complex phrases
        ("can you install telegram for me", "Telegram"),
        ("i would like to install discord", "Discord"),
        ("could you get me chrome", "Google Chrome"),
        ("show me how to install firefox", "Firefox"),
        ("help me install slack", "Slack"),
        ("i want to download zoom", "Zoom"),
        
        # Edge cases
        ("telegram", "Telegram"),
        ("TELEGRAM", "Telegram"),
        ("Telegram", "Telegram"),
        ("  telegram  ", "Telegram"),
        ("", ""),
        ("   ", ""),
        
        # Special app names
        ("install vscode", "VS Code"),
        ("get me visual studio code", "VS Code"),
        ("install code", "VS Code"),
        ("install google chrome", "Google Chrome"),
        ("install mozilla firefox", "Firefox"),
        ("install microsoft teams", "Microsoft Teams"),
        
        # Problematic cases that should be fixed
        ("get me telegram", "Telegram"),  # This was the original issue
        ("install me telegram", "Telegram"),
        ("need me telegram", "Telegram"),
    ]
    
    print("🧪 Testing App Name Extraction")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for input_text, expected_output in test_cases:
        try:
            result = AppNameExtractor.extract_app_name(input_text)
            is_valid = AppNameExtractor.validate_app_name(result)
            
            if result == expected_output and is_valid:
                print(f"✅ '{input_text}' → '{result}'")
                passed += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected: '{expected_output}')")
                if not is_valid:
                    print(f"   ⚠️  Validation failed for: '{result}'")
                failed += 1
                
        except Exception as e:
            print(f"💥 '{input_text}' → Error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! App name extraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return failed == 0

def test_specific_issue():
    """Test the specific issue mentioned: 'get me telegram'"""
    print("\n🔍 Testing Specific Issue: 'get me telegram'")
    print("-" * 40)
    
    test_input = "get me telegram"
    result = AppNameExtractor.extract_app_name(test_input)
    is_valid = AppNameExtractor.validate_app_name(result)
    
    print(f"Input: '{test_input}'")
    print(f"Extracted: '{result}'")
    print(f"Valid: {is_valid}")
    print(f"Expected: 'Telegram'")
    
    if result == "Telegram" and is_valid:
        print("✅ Issue fixed! 'get me telegram' now correctly extracts 'Telegram'")
        return True
    else:
        print("❌ Issue still exists")
        return False

def main():
    """Run all tests."""
    print("🚀 CONFIGO App Name Extraction Test Suite")
    print("=" * 60)
    
    try:
        # Test general extraction
        general_success = test_app_name_extraction()
        
        # Test specific issue
        specific_success = test_specific_issue()
        
        if general_success and specific_success:
            print("\n🎉 All tests passed! The app name extraction is working correctly.")
            print("\nThe issue with 'get me telegram' has been fixed!")
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 