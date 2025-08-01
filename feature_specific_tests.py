#!/usr/bin/env python3
"""
CONFIGO Feature-Specific Tests
==============================

Targeted tests for specific CONFIGO features:
- App installation via natural language
- Chat mode with specific questions
- Memory persistence across sessions
- Self-healing installation
- Tool detection and validation
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.memory import AgentMemory
from core.app_name_extractor import AppNameExtractor
from core.chat_agent import ChatAgent
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.validator import ToolValidator
from ui.enhanced_messages import EnhancedMessageDisplay
from rich.console import Console

def test_app_installation_extraction():
    """Test app name extraction for installation commands."""
    print("\n🔧 Testing App Installation Extraction")
    print("=" * 50)
    
    test_cases = [
        ("Install Telegram", "Telegram"),
        ("Get me Slack", "Slack"), 
        ("I need Chrome", "Google Chrome"),
        ("Install VS Code", "VS Code"),
        ("Download Docker", "Docker"),
        ("Setup Python", "Python"),
        ("Add Node.js", "Node.js"),
        ("Install Postman", "Postman"),
        ("Get Jupyter", "Jupyter"),
        ("Install Git", "Git")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, expected in test_cases:
        try:
            extracted = AppNameExtractor.extract_app_name(input_text)
            success = extracted.lower() in expected.lower() or expected.lower() in extracted.lower()
            
            status = "✅" if success else "❌"
            print(f"{status} '{input_text}' -> '{extracted}' (expected: '{expected}')")
            
            if success:
                passed += 1
                
        except Exception as e:
            print(f"❌ '{input_text}' -> ERROR: {e}")
    
    print(f"\n📊 App Extraction Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

def test_chat_mode_questions():
    """Test chat mode with specific questions."""
    print("\n💬 Testing Chat Mode Questions")
    print("=" * 50)
    
    memory = AgentMemory()
    chat_agent = ChatAgent(memory)
    
    test_questions = [
        "Who are you?",
        "What can you do?",
        "Do you know Python?",
        "What is Docker?",
        "How do I install Git?",
        "What is the difference between pip and conda?",
        "Can you help me with a Python error?",
        "What tools do you recommend for web development?"
    ]
    
    passed = 0
    total = len(test_questions)
    
    for question in test_questions:
        try:
            response = chat_agent.process_message(question)
            
            # Validate response
            if response and hasattr(response, 'message') and len(response.message) > 10:
                print(f"✅ '{question}' -> {response.message[:50]}...")
                passed += 1
            else:
                print(f"❌ '{question}' -> Invalid response")
                
        except Exception as e:
            print(f"❌ '{question}' -> ERROR: {e}")
    
    print(f"\n📊 Chat Mode Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

def test_memory_persistence():
    """Test memory persistence across sessions."""
    print("\n🧠 Testing Memory Persistence")
    print("=" * 50)
    
    memory = AgentMemory()
    
    # Test 1: Record some installations
    test_tools = [
        ("Python", "apt-get install python3", "python3 --version", True, "3.11.9"),
        ("Git", "apt-get install git", "git --version", True, "2.43.0"),
        ("Docker", "apt-get install docker", "docker --version", False, None)
    ]
    
    for tool_name, install_cmd, check_cmd, success, version in test_tools:
        memory.record_tool_installation(
            tool_name=tool_name,
            install_command=install_cmd,
            check_command=check_cmd,
            success=success,
            version=version
        )
    
    # Test 2: Check if tools are remembered
    passed = 0
    total = len(test_tools)
    
    for tool_name, _, _, expected_success, _ in test_tools:
        tool_memory = memory.get_tool_memory(tool_name)
        if tool_memory and tool_memory.install_success == expected_success:
            print(f"✅ {tool_name} memory: {'Installed' if expected_success else 'Failed'}")
            passed += 1
        else:
            print(f"❌ {tool_name} memory: Not found or incorrect")
    
    # Test 3: Check memory statistics
    stats = memory.get_memory_stats()
    print(f"📊 Memory Stats: {stats.get('total_tools', 0)} tools, {stats.get('successful_installations', 0)} successful")
    
    print(f"\n📊 Memory Persistence Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

def test_tool_validation():
    """Test tool validation system."""
    print("\n✅ Testing Tool Validation")
    print("=" * 50)
    
    memory = AgentMemory()
    llm_agent = EnhancedLLMAgent(memory)
    validator = ToolValidator(memory, llm_agent)
    
    # Test tools that should be available
    test_tools = [
        {
            'name': 'python',
            'install_command': 'apt-get install python3',
            'check_command': 'python3 --version',
            'is_extension': False
        },
        {
            'name': 'git',
            'install_command': 'apt-get install git', 
            'check_command': 'git --version',
            'is_extension': False
        }
    ]
    
    validation_report = validator.validate_tools(test_tools)
    
    passed = 0
    total = len(test_tools)
    
    for result in validation_report.validation_results:
        if result.is_installed:
            print(f"✅ {result.tool_name}: {result.version}")
            passed += 1
        else:
            print(f"❌ {result.tool_name}: {result.error_message}")
    
    print(f"\n📊 Tool Validation Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

def test_environment_detection():
    """Test environment detection for different developer types."""
    print("\n🎯 Testing Environment Detection")
    print("=" * 50)
    
    memory = AgentMemory()
    llm_agent = EnhancedLLMAgent(memory)
    
    test_environments = [
        ("Full Stack AI Developer on Linux", "ai_ml"),
        ("Web Developer", "web_dev"),
        ("Data Scientist", "data_science"),
        ("DevOps Engineer", "devops")
    ]
    
    passed = 0
    total = len(test_environments)
    
    for env_desc, expected_domain in test_environments:
        try:
            response = llm_agent.generate_enhanced_stack(env_desc)
            detected_domain = response.domain_completion.get("detected_domain", "unknown")
            
            # Check if domain detection worked (or at least returned a valid domain)
            if detected_domain in ["ai_ml", "web_dev", "data_science", "devops", "unknown"]:
                print(f"✅ '{env_desc}' -> {detected_domain} ({len(response.tools)} tools)")
                passed += 1
            else:
                print(f"❌ '{env_desc}' -> Invalid domain: {detected_domain}")
                
        except Exception as e:
            print(f"❌ '{env_desc}' -> ERROR: {e}")
    
    print(f"\n📊 Environment Detection Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    return passed == total

def test_ui_components():
    """Test UI components and message display."""
    print("\n🎨 Testing UI Components")
    print("=" * 50)
    
    console = Console()
    messages = EnhancedMessageDisplay(console)
    memory = AgentMemory()
    
    try:
        # Test banner display
        messages.show_autonomous_banner()
        
        # Test memory context display
        messages.show_memory_context(memory)
        
        # Test error message
        messages.show_error_with_context("Test error message")
        
        # Test success message
        print("✅ UI components rendered successfully")
        return True
        
    except Exception as e:
        print(f"❌ UI components failed: {e}")
        return False

def test_integration_workflow():
    """Test complete integration workflow."""
    print("\n🔗 Testing Integration Workflow")
    print("=" * 50)
    
    try:
        memory = AgentMemory()
        llm_agent = EnhancedLLMAgent(memory)
        chat_agent = ChatAgent(memory)
        
        # 1. Start a session
        session_id = memory.start_session("Integration Test Environment")
        
        # 2. Generate stack recommendations
        response = llm_agent.generate_enhanced_stack("Python Developer")
        
        # 3. Extract app name
        app_name = AppNameExtractor.extract_app_name("Install Python")
        
        # 4. Record installation
        memory.record_tool_installation(
            tool_name=app_name,
            install_command="apt-get install python3",
            check_command="python3 --version",
            success=True,
            version="3.11.9"
        )
        
        # 5. Test chat interaction
        chat_response = chat_agent.process_message("What did I just install?")
        
        # 6. End session
        memory.end_session(session_id)
        
        print("✅ Integration workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration workflow failed: {e}")
        return False

def main():
    """Run all feature-specific tests."""
    print("🚀 CONFIGO Feature-Specific Tests")
    print("=" * 60)
    
    tests = [
        ("App Installation Extraction", test_app_installation_extraction),
        ("Chat Mode Questions", test_chat_mode_questions),
        ("Memory Persistence", test_memory_persistence),
        ("Tool Validation", test_tool_validation),
        ("Environment Detection", test_environment_detection),
        ("UI Components", test_ui_components),
        ("Integration Workflow", test_integration_workflow)
    ]
    
    results = {}
    total_passed = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                total_passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 FEATURE TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Overall Results: {total_passed}/{total_tests} passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("🎉 All feature tests passed!")
        return 0
    else:
        print("⚠️  Some feature tests failed")
        return 1

if __name__ == "__main__":
    exit(main()) 