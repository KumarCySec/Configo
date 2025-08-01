#!/usr/bin/env python3
"""
Test Script for LLM API Integration
===================================

This script tests the Gemini API integration to diagnose authentication issues.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_loading():
    """Test that environment variables are properly loaded."""
    print("🔍 Testing Environment Variable Loading...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Creating .env.example for reference...")
        return False
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not properly set")
        print("   Please set your actual API key in .env file")
        return False
    
    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")
    return True

def test_gemini_api_call():
    """Test actual Gemini API call."""
    print("\n🧪 Testing Gemini API Call...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key available for testing")
        return False
    
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": "Hello! Please respond with 'API test successful' if you can see this message."
            }]
        }]
    }
    
    try:
        print("📡 Making API request...")
        response = requests.post(
            f"{api_url}?key={api_key}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and result['candidates']:
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API test successful!")
                print(f"📝 Response: {response_text[:100]}...")
                return True
            else:
                print("❌ Unexpected response format from Gemini API")
                print(f"📄 Response: {result}")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False

def create_env_example():
    """Create .env.example file if it doesn't exist."""
    if not os.path.exists('.env.example'):
        print("\n📝 Creating .env.example file...")
        with open('.env.example', 'w') as f:
            f.write("""# CONFIGO Environment Configuration
# ======================================

# Required: Google Gemini API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Alternative Google API Key (fallback)
# GOOGLE_API_KEY=your_google_api_key_here

# Optional: mem0 API Key for enhanced memory
# Get your API key from: https://mem0.ai
# MEM0_API_KEY=your_mem0_api_key_here

# Optional: Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Optional: LLM timeout in seconds
LLM_TIMEOUT=30

# Optional: Custom Gemini API URL (usually not needed)
# GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent

# Optional: Custom Gemini model (usually not needed)
# GEMINI_MODEL=gemini-2.0-flash-exp
""")
        print("✅ .env.example created")

def main():
    """Run all tests."""
    print("🧠 CONFIGO LLM API Integration Test")
    print("=" * 50)
    
    # Create .env.example if it doesn't exist
    create_env_example()
    
    # Test environment loading
    env_ok = test_env_loading()
    
    if not env_ok:
        print("\n🔧 Setup Instructions:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("2. Edit .env and add your GEMINI_API_KEY:")
        print("   GEMINI_API_KEY=your_actual_key_here")
        print("3. Run this test again:")
        print("   python scripts/test_llm_api.py")
        return False
    
    # Test API call
    api_ok = test_gemini_api_call()
    
    print("\n" + "=" * 50)
    if env_ok and api_ok:
        print("🎉 All tests passed! LLM API integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 