#!/usr/bin/env python3
"""
Demo script for enhanced environment intelligence.

This script demonstrates how CONFIGO now provides comprehensive,
domain-specific tech stacks instead of minimal base tools.
"""

import os
import sys
import logging

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from enhanced_llm_agent import EnhancedLLMAgent
from core.memory import AgentMemory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_environment_intelligence():
    """Demonstrate the enhanced environment intelligence."""
    
    print("🚀 CONFIGO Enhanced Environment Intelligence Demo")
    print("=" * 60)
    print()
    
    # Initialize the enhanced LLM agent
    memory = AgentMemory()
    llm_agent = EnhancedLLMAgent(memory)
    
    # Test environments
    test_environments = [
        "Full Stack AI Developer",
        "Web Developer (React)",
        "Data Scientist",
        "Cloud DevOps Engineer"
    ]
    
    for environment in test_environments:
        print(f"🧠 Testing Environment: '{environment}'")
        print("-" * 50)
        
        # Detect domain
        detected_domain = llm_agent._detect_domain(environment)
        print(f"🎯 Detected Domain: {detected_domain.upper()}")
        
        # Test domain completion with empty response
        empty_response = {
            'tools': [],
            'login_portals': [],
            'reasoning': 'Test response',
            'domain_completion': {}
        }
        
        # Apply domain completion
        completed_response = llm_agent._apply_domain_completion(empty_response, environment)
        
        # Show results
        total_tools = len(completed_response['tools'])
        extensions = [tool for tool in completed_response['tools'] if tool.is_extension]
        login_portals = len(completed_response['login_portals'])
        
        print(f"📦 Total Tools Generated: {total_tools}")
        print(f"🔌 Extensions: {len(extensions)}")
        print(f"🌐 Login Portals: {login_portals}")
        print(f"✅ Target Met (8+ tools): {total_tools >= 8}")
        
        # Show some example tools
        print(f"\n🛠️ Example Tools:")
        for i, tool in enumerate(completed_response['tools'][:5]):
            print(f"  {i+1}. {tool.name} (Priority: {tool.priority}, Confidence: {tool.confidence_score:.2f})")
        
        if total_tools > 5:
            print(f"  ... and {total_tools - 5} more tools")
        
        # Show login portals
        print(f"\n🌐 Login Portals:")
        for portal in completed_response['login_portals'][:3]:
            print(f"  • {portal['name']}: {portal['url']}")
        
        if login_portals > 3:
            print(f"  ... and {login_portals - 3} more portals")
        
        print(f"\n💡 Domain Completion Info:")
        domain_info = completed_response['domain_completion']
        print(f"  Detected Domain: {domain_info.get('detected_domain', 'Unknown')}")
        print(f"  Total Tools: {domain_info.get('total_tools', 0)}")
        print(f"  Target Met: {domain_info.get('target_met', False)}")
        
        print("\n" + "="*60 + "\n")
    
    print("🎉 Demo completed!")
    print("\n✅ Key Improvements:")
    print("  • Domain-aware tool selection")
    print("  • Comprehensive tool stacks (8-12+ tools)")
    print("  • Domain-specific extensions and portals")
    print("  • Quality validation and retry logic")
    print("  • Enhanced prompt engineering")
    print("  • Memory-aware recommendations")

if __name__ == "__main__":
    demo_environment_intelligence() 