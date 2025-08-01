#!/usr/bin/env python3
"""
CONFIGO Enhanced UI Test Script
===============================

Test script to demonstrate the enhanced terminal UI features.
"""

import time
from ui.enhanced_terminal_ui import EnhancedTerminalUI, UIConfig

def test_enhanced_ui():
    """Test the enhanced terminal UI features."""
    
    # Initialize enhanced UI
    ui = EnhancedTerminalUI()
    
    # Test banner
    print("=== Testing Banner ===")
    ui.show_banner()
    time.sleep(1)
    
    # Test AI reasoning
    print("\n=== Testing AI Reasoning ===")
    ui.show_ai_reasoning(
        "Project Analysis: Python Web Development",
        "Based on the project structure and dependencies, CONFIGO detected this as a Python web development project.\n\n"
        "Key indicators:\n"
        "• requirements.txt file present\n"
        "• Flask/Django imports detected\n"
        "• HTML templates directory found\n"
        "• Database configuration files present",
        0.95
    )
    time.sleep(1)
    
    # Test tool detection table
    print("\n=== Testing Tool Detection Table ===")
    tools = [
        {'name': 'Python', 'installed': True, 'version': '3.11.0', 'path': '/usr/bin/python3'},
        {'name': 'Git', 'installed': True, 'version': '2.34.0', 'path': '/usr/bin/git'},
        {'name': 'Docker', 'installed': False, 'version': 'N/A', 'path': 'N/A'},
        {'name': 'Node.js', 'installed': True, 'version': '18.17.0', 'path': '/usr/bin/node'}
    ]
    ui.show_tool_detection_table(tools)
    time.sleep(1)
    
    # Test planning steps
    print("\n=== Testing Planning Steps ===")
    steps = [
        {
            'name': 'Install Python Dependencies',
            'description': 'Install required Python packages',
            'sub_steps': ['pip install flask', 'pip install sqlalchemy']
        },
        {
            'name': 'Setup Database',
            'description': 'Configure and initialize database',
            'sub_steps': ['Create database', 'Run migrations']
        },
        {
            'name': 'Configure Web Server',
            'description': 'Setup web server configuration',
            'sub_steps': ['Nginx config', 'SSL certificates']
        }
    ]
    ui.show_planning_steps(steps)
    time.sleep(1)
    
    # Test success message
    print("\n=== Testing Success Message ===")
    ui.show_success_message("Setup completed successfully!", "All tools installed and configured")
    time.sleep(1)
    
    # Test error message
    print("\n=== Testing Error Message ===")
    ui.show_error_message("Failed to install Docker", "Check if Docker is available in your package manager", "Try: sudo apt install docker.io")
    time.sleep(1)
    
    # Test info message
    print("\n=== Testing Info Message ===")
    ui.show_info_message("Starting installation process...", "🚀")
    time.sleep(1)
    
    # Test validation results
    print("\n=== Testing Validation Results ===")
    validation_results = [
        {'name': 'Python', 'valid': True, 'version': '3.11.0', 'details': ''},
        {'name': 'Git', 'valid': True, 'version': '2.34.0', 'details': ''},
        {'name': 'Docker', 'valid': False, 'version': 'N/A', 'details': 'Not installed'},
        {'name': 'Node.js', 'valid': True, 'version': '18.17.0', 'details': ''}
    ]
    ui.show_validation_results(validation_results)
    time.sleep(1)
    
    # Test memory context
    print("\n=== Testing Memory Context ===")
    memory_stats = {
        'total_tools': 15,
        'successful_installations': 12,
        'failed_installations': 3,
        'success_rate': 80.0,
        'recent_tools': ['Python', 'Git', 'Docker', 'Node.js', 'PostgreSQL']
    }
    ui.show_memory_context(memory_stats)
    time.sleep(1)
    
    # Test login portal prompt
    print("\n=== Testing Login Portal Prompt ===")
    ui.show_login_portal_prompt(
        "GitHub",
        "https://github.com/login",
        "Please log in to GitHub to enable repository access and API features."
    )
    time.sleep(1)
    
    # Test completion summary
    print("\n=== Testing Completion Summary ===")
    summary = {
        'tools_installed': 8,
        'validations_passed': 7,
        'portals_opened': 2,
        'total_time': '2m 34s',
        'suggestions': [
            'Consider installing Docker for containerization',
            'Setup SSL certificates for production deployment',
            'Configure automated backups for your database'
        ]
    }
    ui.show_completion_summary(summary)
    time.sleep(1)
    
    # Test chat interface
    print("\n=== Testing Chat Interface ===")
    ui.show_chat_interface("Chat with CONFIGO - Ask me anything!")
    time.sleep(1)
    
    # Test chat responses
    print("\n=== Testing Chat Responses ===")
    ui.show_chat_response("Hello! I'm CONFIGO, your AI development assistant. How can I help you today?", is_ai=True)
    time.sleep(1)
    
    ui.show_chat_response("I need help installing Python packages", is_ai=False)
    time.sleep(1)
    
    ui.show_chat_response("I can help you with that! Let me show you the best practices for Python package management.", is_ai=True)
    time.sleep(1)
    
    # Test separators
    print("\n=== Testing Separators ===")
    ui.show_separator("End of Demo")
    
    print("\n🎉 Enhanced UI Test Complete!")
    print("The enhanced terminal UI provides a modern, stylish, and professional interface for CONFIGO.")

if __name__ == "__main__":
    test_enhanced_ui() 