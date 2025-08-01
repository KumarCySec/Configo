#!/usr/bin/env python3
"""
Integration test for enhanced environment intelligence.

This script tests that the enhanced LLM agent integrates properly
with the main CONFIGO application.
"""

import os
import sys
import logging

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from ai import suggest_stack

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_integration():
    """Test the integration of enhanced environment intelligence."""
    
    print("🔗 Testing CONFIGO Integration")
    print("=" * 50)
    
    # Test environments
    test_environments = [
        "Full Stack AI Developer",
        "Web Developer (React)",
        "Data Scientist",
        "Cloud DevOps Engineer"
    ]
    
    for environment in test_environments:
        print(f"\n🧠 Testing: '{environment}'")
        print("-" * 40)
        
        try:
            # Use the suggest_stack function (which now uses enhanced LLM agent)
            tools, login_portals = suggest_stack(environment)
            
            print(f"📦 Tools Generated: {len(tools)}")
            print(f"🌐 Login Portals: {len(login_portals)}")
            print(f"✅ Target Met (8+ tools): {len(tools) >= 8}")
            
            # Show some example tools
            print(f"\n🛠️ Example Tools:")
            for i, tool in enumerate(tools[:5]):
                print(f"  {i+1}. {tool['name']}")
            
            if len(tools) > 5:
                print(f"  ... and {len(tools) - 5} more tools")
            
            # Show login portals
            print(f"\n🌐 Login Portals:")
            for portal in login_portals[:3]:
                print(f"  • {portal['name']}: {portal['url']}")
            
            if len(login_portals) > 3:
                print(f"  ... and {len(login_portals) - 3} more portals")
            
            print("✅ Integration successful!")
            
        except Exception as e:
            print(f"❌ Integration failed: {e}")
            logger.error(f"Failed to test integration for '{environment}': {e}")
        
        print("-" * 40)
    
    print("\n🎉 Integration test completed!")

if __name__ == "__main__":
    test_integration() 