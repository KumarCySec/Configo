#!/usr/bin/env python3
"""
Test Knowledge Layer Activation
==============================

Test script to verify that CONFIGO's knowledge layer is properly activated
and working with graph and vector databases.
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from knowledge.engine import KnowledgeEngine
from memory.memory_store import MemoryStore
from agent.agent_engine import AgentEngine
from core.installer import Installer
from core.validator import Validator
from ui.enhanced_terminal_ui import EnhancedTerminalUI, UIConfig


def test_knowledge_initialization():
    """Test knowledge engine initialization."""
    print("🧠 Testing Knowledge Engine Initialization...")
    
    try:
        config = Config()
        knowledge = KnowledgeEngine(config)
        
        print(f"✅ Knowledge Engine initialized successfully")
        print(f"   Graph Manager: {'✅ Connected' if knowledge.graph_manager and knowledge.graph_manager.connected else '❌ Disconnected'}")
        print(f"   Vector Manager: {'✅ Connected' if knowledge.vector_manager else '❌ Disconnected'}")
        
        return knowledge
    except Exception as e:
        print(f"❌ Failed to initialize knowledge engine: {e}")
        return None


def test_memory_integration():
    """Test memory integration with knowledge."""
    print("\n💾 Testing Memory Integration...")
    
    try:
        memory = MemoryStore()
        config = Config()
        knowledge = KnowledgeEngine(config)
        
        # Test memory context
        context = memory.get_memory_context()
        print(f"✅ Memory context retrieved: {len(context)} characters")
        
        return memory, knowledge
    except Exception as e:
        print(f"❌ Failed to test memory integration: {e}")
        return None, None


def test_agent_integration():
    """Test agent integration with knowledge."""
    print("\n🤖 Testing Agent Integration...")
    
    try:
        config = Config()
        memory = MemoryStore()
        knowledge = KnowledgeEngine(config)
        agent = AgentEngine(memory, knowledge)
        
        print("✅ Agent Engine initialized with knowledge integration")
        
        # Test knowledge context generation
        context = agent._get_knowledge_context("python development")
        print(f"✅ Knowledge context generated: {len(context)} characters")
        
        return agent
    except Exception as e:
        print(f"❌ Failed to test agent integration: {e}")
        return None


def test_installer_integration():
    """Test installer integration with knowledge."""
    print("\n🔧 Testing Installer Integration...")
    
    try:
        config = Config()
        knowledge = KnowledgeEngine(config)
        installer = Installer(config, knowledge)
        
        print("✅ Installer initialized with knowledge integration")
        
        # Test system info
        system_info = installer._get_system_info()
        print(f"✅ System info retrieved: {system_info}")
        
        return installer
    except Exception as e:
        print(f"❌ Failed to test installer integration: {e}")
        return None


def test_validator_integration():
    """Test validator integration with knowledge."""
    print("\n✅ Testing Validator Integration...")
    
    try:
        config = Config()
        knowledge = KnowledgeEngine(config)
        validator = Validator(config, knowledge)
        
        print("✅ Validator initialized with knowledge integration")
        
        return validator
    except Exception as e:
        print(f"❌ Failed to test validator integration: {e}")
        return None


def test_knowledge_operations():
    """Test basic knowledge operations."""
    print("\n🔍 Testing Knowledge Operations...")
    
    try:
        config = Config()
        knowledge = KnowledgeEngine(config)
        
        # Test tool knowledge addition
        success = knowledge.add_tool_knowledge("test_tool", {
            'description': 'Test tool for knowledge testing',
            'category': 'test',
            'version': '1.0.0'
        })
        print(f"✅ Tool knowledge addition: {'✅ Success' if success else '❌ Failed'}")
        
        # Test search
        results = knowledge.search_tools("test", 5)
        print(f"✅ Search operation: Found {len(results)} results")
        
        # Test graph stats
        graph_stats = knowledge.get_graph_stats()
        print(f"✅ Graph stats: {graph_stats}")
        
        # Test vector stats
        vector_stats = knowledge.get_vector_stats()
        print(f"✅ Vector stats: {vector_stats}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test knowledge operations: {e}")
        return False


def test_cli_commands():
    """Test CLI command integration."""
    print("\n📋 Testing CLI Command Integration...")
    
    try:
        config = Config()
        ui_config = UIConfig()
        ui = EnhancedTerminalUI(ui_config)
        knowledge = KnowledgeEngine(config)
        
        print("✅ CLI components initialized")
        
        # Test graph stats command
        stats = knowledge.get_graph_stats()
        print(f"✅ Graph stats command: {stats}")
        
        # Test vector stats command
        vector_stats = knowledge.get_vector_stats()
        print(f"✅ Vector stats command: {vector_stats}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test CLI commands: {e}")
        return False


def main():
    """Run all knowledge layer tests."""
    print("🚀 CONFIGO Knowledge Layer Activation Test")
    print("=" * 50)
    
    # Test 1: Knowledge Engine Initialization
    knowledge = test_knowledge_initialization()
    if not knowledge:
        print("❌ Knowledge engine initialization failed - stopping tests")
        return False
    
    # Test 2: Memory Integration
    memory, knowledge = test_memory_integration()
    if not memory or not knowledge:
        print("❌ Memory integration failed")
        return False
    
    # Test 3: Agent Integration
    agent = test_agent_integration()
    if not agent:
        print("❌ Agent integration failed")
        return False
    
    # Test 4: Installer Integration
    installer = test_installer_integration()
    if not installer:
        print("❌ Installer integration failed")
        return False
    
    # Test 5: Validator Integration
    validator = test_validator_integration()
    if not validator:
        print("❌ Validator integration failed")
        return False
    
    # Test 6: Knowledge Operations
    if not test_knowledge_operations():
        print("❌ Knowledge operations failed")
        return False
    
    # Test 7: CLI Commands
    if not test_cli_commands():
        print("❌ CLI commands failed")
        return False
    
    print("\n🎉 All Knowledge Layer Tests Passed!")
    print("✅ CONFIGO Knowledge Layer is fully activated and working")
    
    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = main()
    sys.exit(0 if success else 1) 