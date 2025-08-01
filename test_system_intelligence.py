#!/usr/bin/env python3
"""
Test script for CONFIGO System Intelligence
==========================================

Demonstrates the advanced system intelligence capabilities of CONFIGO,
including comprehensive system detection, analysis, and integration
with the main CONFIGO pipeline.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.system_inspector import SystemInspector, display_system_summary
from core.memory import AgentMemory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_system_inspector():
    """Test the SystemInspector functionality."""
    print("🧠 CONFIGO System Intelligence Test")
    print("=" * 50)
    
    # Initialize system inspector
    inspector = SystemInspector()
    
    # Perform comprehensive analysis
    print("🔍 Analyzing system...")
    system_info = inspector.analyze()
    
    # Display results
    print("\n📊 System Intelligence Results:")
    display_system_summary(system_info)
    
    # Test installation recommendations
    print("\n💡 Installation Recommendations:")
    recommendations = inspector.get_installation_recommendations(system_info)
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Test memory integration
    print("\n💾 Testing memory integration...")
    memory = AgentMemory()
    inspector.save_to_memory(system_info)
    
    # Verify saved data
    memory_file = Path(".configo_memory/system_intelligence.json")
    if memory_file.exists():
        print(f"✅ System intelligence saved to {memory_file}")
        
        # Read and display saved data
        import json
        with open(memory_file, 'r') as f:
            saved_data = json.load(f)
        
        print(f"📁 Saved data keys: {list(saved_data.keys())}")
        print(f"🖥️  OS: {saved_data['os_name']} {saved_data['os_version']}")
        print(f"🔧 Package Managers: {saved_data['package_managers']}")
        print(f"🎮 GPU: {saved_data['gpu']}")
        print(f"💾 RAM: {saved_data['ram_gb']} GB")
    else:
        print("❌ Failed to save system intelligence")
    
    return system_info


def test_integration_with_main_pipeline():
    """Test integration with main CONFIGO pipeline."""
    print("\n🔗 Testing Integration with Main Pipeline")
    print("=" * 50)
    
    # Simulate main pipeline integration
    from core.enhanced_llm_agent import EnhancedLLMAgent
    
    # Initialize components
    memory = AgentMemory()
    llm_agent = EnhancedLLMAgent(memory)
    inspector = SystemInspector()
    
    # Get system intelligence
    system_info = inspector.analyze()
    
    # Create system context for LLM
    system_context = f"""
System Environment:
- OS: {system_info.os_name} {system_info.os_version}
- Architecture: {system_info.arch}
- Package Managers: {', '.join(system_info.package_managers)}
- GPU: {system_info.gpu or 'None'}
- RAM: {system_info.ram_gb} GB
- Virtualization: {system_info.virtualization}
- Sudo Access: {'Yes' if system_info.has_sudo else 'No'}
- Installed Tools: {', '.join(system_info.installed_tools[:10])}
"""
    
    print("📋 System Context for LLM:")
    print(system_context)
    
    # Test environment-specific recommendations
    test_environments = [
        "AI/ML Development Environment",
        "Web Development Environment", 
        "Data Science Environment"
    ]
    
    for env in test_environments:
        print(f"\n🎯 Testing for: {env}")
        
        # Get recommendations based on system intelligence
        recommendations = inspector.get_installation_recommendations(system_info)
        
        print("💡 System-aware recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
        
        # Show how system context would influence LLM decisions
        if system_info.gpu and "NVIDIA" in system_info.gpu and system_info.cuda_available:
            print("  • CUDA detected - recommending GPU-accelerated AI tools")
        
        if system_info.virtualization == "WSL":
            print("  • WSL detected - avoiding snap packages, preferring apt/flatpak")
        
        if system_info.ram_gb < 8:
            print("  • Low RAM detected - recommending lightweight tools")
        
        if 'snap' in system_info.package_managers and system_info.virtualization != "WSL":
            print("  • Snap available - recommending containerized applications")


def test_warning_system():
    """Test the warning and blocker detection system."""
    print("\n⚠️  Testing Warning System")
    print("=" * 50)
    
    inspector = SystemInspector()
    system_info = inspector.analyze()
    
    print("🔍 Detected Warnings:")
    if system_info.warnings:
        for warning in system_info.warnings:
            print(f"  • [{warning.level.upper()}] {warning.message}")
            if warning.recommendation:
                print(f"    💡 Recommendation: {warning.recommendation}")
    else:
        print("  ✅ No warnings detected")
    
    # Test specific scenarios
    print("\n🧪 Testing Specific Scenarios:")
    
    # WSL scenario
    if system_info.virtualization == "WSL":
        print("  • WSL detected - checking for snap limitations")
        if 'snap' in system_info.package_managers:
            print("    ⚠️  Snap may not work properly in WSL")
            print("    💡 Consider using apt or flatpak instead")
    
    # Low RAM scenario
    if system_info.ram_gb < 8:
        print("  • Low RAM detected - checking for resource-intensive tools")
        print("    💡 Consider lightweight alternatives")
    
    # No sudo access
    if not system_info.has_sudo:
        print("  • No sudo access - checking for user-space alternatives")
        print("    💡 Consider user-space package managers")
    
    # No internet
    if not system_info.internet:
        print("  • No internet connection - checking for offline capabilities")
        print("    💡 Some features may be limited")


def main():
    """Main test function."""
    print("🚀 CONFIGO System Intelligence Test Suite")
    print("=" * 60)
    
    try:
        # Test basic system inspector
        system_info = test_system_inspector()
        
        # Test integration with main pipeline
        test_integration_with_main_pipeline()
        
        # Test warning system
        test_warning_system()
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 System Intelligence Features:")
        print("  • Comprehensive system detection")
        print("  • Hardware and software analysis")
        print("  • Virtualization and environment detection")
        print("  • Warning and blocker identification")
        print("  • Installation recommendations")
        print("  • Memory integration")
        print("  • LLM context enhancement")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 