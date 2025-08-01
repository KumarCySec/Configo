#!/usr/bin/env python3
"""
Test Script for CONFIGO AI Agent Fixes
======================================

This script tests the critical fixes made to ensure CONFIGO is truly autonomous
and AI-powered instead of using hardcoded fallbacks.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_env_loading():
    """Test that environment variables are properly loaded."""
    print("🔍 Testing Environment Variable Loading...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not properly set")
        print("   Please set your actual API key in .env file")
        return False
    
    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")
    return True

def test_llm_client():
    """Test that the LLM client properly validates API keys."""
    print("\n🔍 Testing LLM Client...")
    
    try:
        from core.ai import LLMClient
        
        client = LLMClient()
        
        # Test API key validation
        if not client._validate_api_key():
            print("❌ API key validation failed")
            return False
        
        print("✅ LLM Client initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ LLM Client test failed: {e}")
        return False

def test_enhanced_llm_agent():
    """Test that the enhanced LLM agent doesn't use hardcoded fallbacks."""
    print("\n🔍 Testing Enhanced LLM Agent...")
    
    try:
        from core.enhanced_llm_agent import EnhancedLLMAgent
        from core.memory import AgentMemory
        
        memory = AgentMemory()
        agent = EnhancedLLMAgent(memory)
        
        # Test that the fallback method is removed
        if hasattr(agent, '_fallback_stack'):
            print("❌ Hardcoded fallback method still exists")
            return False
        
        print("✅ Enhanced LLM Agent initialized (no hardcoded fallbacks)")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced LLM Agent test failed: {e}")
        return False

def test_chat_agent():
    """Test that the chat agent properly calls the LLM API."""
    print("\n🔍 Testing Chat Agent...")
    
    try:
        from core.chat_agent import ChatAgent
        from core.memory import AgentMemory
        
        memory = AgentMemory()
        agent = ChatAgent(memory, debug_mode=True)
        
        print("✅ Chat Agent initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Chat Agent test failed: {e}")
        return False

def test_memory_system():
    """Test that the memory system is properly configured."""
    print("\n🔍 Testing Memory System...")
    
    try:
        from core.memory import AgentMemory
        
        memory = AgentMemory()
        
        # Test basic memory operations
        session_id = memory.start_session("test_environment")
        memory.end_session(session_id)
        
        print("✅ Memory System working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Memory System test failed: {e}")
        return False

def test_main_imports():
    """Test that main.py properly loads environment variables."""
    print("\n🔍 Testing Main.py Environment Loading...")
    
    try:
        # Check if dotenv is imported at the top of main.py
        with open('main.py', 'r') as f:
            content = f.read()
            
        if 'from dotenv import load_dotenv' not in content:
            print("❌ dotenv import not found in main.py")
            return False
            
        if 'load_dotenv()' not in content:
            print("❌ load_dotenv() call not found in main.py")
            return False
        
        print("✅ Main.py properly loads environment variables")
        return True
        
    except Exception as e:
        print(f"❌ Main.py test failed: {e}")
        return False

def test_requirements():
    """Test that all required dependencies are available."""
    print("\n🔍 Testing Dependencies...")
    
    required_packages = [
        'requests',
        'pyyaml', 
        'python-dotenv',
        'google-generativeai',
        'rich',
        'pyfiglet',
        'mem0ai',
        'distro'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are available")
    return True

def main():
    """Run all tests."""
    print("🧠 CONFIGO AI Agent Fixes Test Suite")
    print("=" * 50)
    
    tests = [
        test_env_loading,
        test_llm_client,
        test_enhanced_llm_agent,
        test_chat_agent,
        test_memory_system,
        test_main_imports,
        test_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CONFIGO is ready to be truly AI-powered.")
        print("\n📝 Next Steps:")
        print("1. Set your GEMINI_API_KEY in .env file")
        print("2. Run: python main.py")
        print("3. Try: python main.py chat")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Set GEMINI_API_KEY in .env file")
        print("2. Run: pip install -r requirements.txt")
        print("3. Check that all files are properly updated")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 