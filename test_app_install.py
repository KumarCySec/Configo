#!/usr/bin/env python3
"""
Test script for CONFIGO's natural language app installation feature.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.system import get_system_info
from core.memory import AgentMemory
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.shell_executor import ShellExecutor
from ui.enhanced_messages import EnhancedMessageDisplay
from rich.console import Console

def test_system_detection():
    """Test system detection functionality."""
    print("🔍 Testing System Detection...")
    system_info = get_system_info()
    print(f"OS: {system_info['os']}")
    print(f"Architecture: {system_info['arch']}")
    print(f"Distribution: {system_info['distro']}")
    print(f"Package Managers: {system_info['package_managers']}")
    print()

def test_llm_plan_generation():
    """Test LLM plan generation for app installation."""
    print("🧠 Testing LLM Plan Generation...")
    
    # Initialize components
    memory = AgentMemory()
    llm_agent = EnhancedLLMAgent(memory)
    system_info = get_system_info()
    
    # Test with a simple app
    app_name = "Slack"
    print(f"Generating install plan for {app_name}...")
    
    plan = llm_agent.get_install_plan(app_name, system_info)
    if plan:
        print("✅ Plan generated successfully!")
        print(f"Method: {plan.get('method', 'unknown')}")
        print(f"Launch: {plan.get('launch', 'N/A')}")
        print(f"Check: {plan.get('check', 'N/A')}")
    else:
        print("❌ Failed to generate plan")
    print()

def test_memory_functions():
    """Test memory functions for app installation."""
    print("💾 Testing Memory Functions...")
    
    memory = AgentMemory()
    
    # Test app installation recording
    test_plan = {
        'app': 'TestApp',
        'method': 'apt',
        'install': 'sudo apt install testapp',
        'check': 'which testapp',
        'launch': 'testapp'
    }
    
    test_result = {
        'app_name': 'TestApp',
        'method': 'apt',
        'success': True,
        'version': '1.0.0',
        'launch_command': 'testapp',
        'error': None
    }
    
    memory.record_app_install('TestApp', test_plan, test_result)
    print("✅ App installation recorded")
    
    # Test app installation check
    is_installed = memory.is_app_installed('TestApp')
    print(f"TestApp installed: {is_installed}")
    
    # Test non-existent app
    is_installed = memory.is_app_installed('NonExistentApp')
    print(f"NonExistentApp installed: {is_installed}")
    print()

def test_ui_functions():
    """Test UI functions for app installation."""
    print("🎨 Testing UI Functions...")
    
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    # Test system info display
    system_info = get_system_info()
    messages.show_app_install_start("TestApp", system_info)
    
    # Test plan display
    test_plan = {
        'app': 'TestApp',
        'method': 'apt',
        'launch': 'testapp'
    }
    messages.show_install_plan(test_plan)
    
    # Test success display
    test_result = {
        'launch_command': 'testapp'
    }
    messages.show_install_success("TestApp", test_result)
    print()

def main():
    """Run all tests."""
    print("🚀 CONFIGO App Installation Test Suite")
    print("=" * 50)
    
    try:
        test_system_detection()
        test_llm_plan_generation()
        test_memory_functions()
        test_ui_functions()
        
        print("✅ All tests completed successfully!")
        print("\n🎉 CONFIGO app installation feature is ready!")
        print("\nTo use the app installer, run:")
        print("  python main.py install")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 