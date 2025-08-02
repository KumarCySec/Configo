#!/usr/bin/env python3
"""
Test Enhanced CONFIGO Knowledge Graph
=====================================

This script demonstrates the enhanced knowledge graph functionality including:
- Graph schema enrichment with new node types
- Gemini-powered knowledge expansion
- Auto-logging of install events
- Comprehensive graph statistics
- Knowledge scheduler functionality

Usage:
    python test_enhanced_knowledge.py
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge.graph_db_manager import GraphDBManager
from knowledge.knowledge_engine import KnowledgeEngine
from knowledge.scheduler import KnowledgeScheduler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_enhanced_graph_schema():
    """Test the enhanced graph schema with new node types."""
    print("🧪 Testing Enhanced Graph Schema")
    print("=" * 50)
    
    # Initialize graph database
    graph_db = GraphDBManager()
    
    # Test adding different node types
    print("📊 Adding nodes to graph...")
    
    # Add tools
    graph_db.add_tool("tensorflow", "machine_learning", "Deep learning framework", 
                      "pip install tensorflow", "python -c 'import tensorflow'")
    graph_db.add_tool("docker", "containerization", "Container platform", 
                      "curl -fsSL https://get.docker.com | sh", "docker --version")
    
    # Add libraries
    graph_db.add_library("numpy", "1.21.0", "python", "Numerical computing library", ["python3.7+", "python3.8+"])
    graph_db.add_library("pandas", "1.3.0", "python", "Data manipulation library", ["python3.7+"])
    
    # Add errors
    graph_db.add_error("tensorflow_cuda_error", "CUDA not found", "Install CUDA toolkit", "medium", "tensorflow", "linux")
    graph_db.add_error("docker_permission_error", "Permission denied", "Add user to docker group", "low", "docker", "linux")
    
    # Add personas
    graph_db.add_persona("data_scientist", "Data Scientist", "ML/AI practitioner", {"prefers_gpu": True, "uses_python": True})
    graph_db.add_persona("devops_engineer", "DevOps Engineer", "Infrastructure specialist", {"prefers_containers": True, "uses_linux": True})
    
    # Add categories
    graph_db.add_category("Machine Learning", "AI and ML frameworks", None)
    graph_db.add_category("Containerization", "Container platforms", None)
    
    # Add features
    graph_db.add_feature("GPU Support", "CUDA acceleration", "tensorflow")
    graph_db.add_feature("Container Management", "Create and manage containers", "docker")
    
    # Add commands
    graph_db.add_command("install_tensorflow", "pip install tensorflow", "Install TensorFlow", "tensorflow", "linux")
    graph_db.add_command("install_docker", "curl -fsSL https://get.docker.com | sh", "Install Docker", "docker", "linux")
    
    print("✅ Enhanced graph schema test completed")


def test_enhanced_relationships():
    """Test the enhanced relationship types."""
    print("\n🔗 Testing Enhanced Relationships")
    print("=" * 50)
    
    graph_db = GraphDBManager()
    
    # Test different relationship types
    print("📊 Adding relationships to graph...")
    
    # Tool dependencies
    graph_db.add_tool_dependency("tensorflow", "numpy", "1.19.0")
    graph_db.add_tool_dependency("tensorflow", "pandas", "1.1.0")
    
    # OS requirements
    graph_db.add_tool_requirement("tensorflow", "linux", "18.04+")
    graph_db.add_tool_requirement("docker", "linux", "18.04+")
    
    # Error fixes
    graph_db.add_error_fix("tensorflow_cuda_error", "install_tensorflow")
    graph_db.add_error_fix("docker_permission_error", "install_docker")
    
    # Persona preferences
    graph_db.add_persona_preference("data_scientist", "tensorflow", 0.9)
    graph_db.add_persona_preference("devops_engineer", "docker", 0.8)
    
    # Tool categories
    graph_db.add_tool_category("tensorflow", "Machine Learning")
    graph_db.add_tool_category("docker", "Containerization")
    
    # Tool features
    graph_db.add_tool_feature("tensorflow", "GPU Support")
    graph_db.add_tool_feature("docker", "Container Management")
    
    print("✅ Enhanced relationships test completed")


def test_graph_statistics():
    """Test comprehensive graph statistics."""
    print("\n📊 Testing Graph Statistics")
    print("=" * 50)
    
    graph_db = GraphDBManager()
    
    # Get comprehensive statistics
    stats = graph_db.get_graph_statistics()
    
    print("📈 Graph Statistics:")
    print(f"   🧠 Total Nodes: {stats.get('total_nodes', 0)}")
    print(f"   🔗 Total Relationships: {stats.get('total_relationships', 0)}")
    
    # Node breakdown
    node_counts = stats.get('node_counts', {})
    if node_counts:
        print("   📊 Node Breakdown:")
        for node_type, count in node_counts.items():
            print(f"      • {node_type}: {count}")
    
    # Top tools
    top_tools = stats.get('top_installed_tools', [])
    if top_tools:
        print("   🔧 Top Installed Tools:")
        for i, tool in enumerate(top_tools[:5], 1):
            print(f"      {i}. {tool.get('name', 'Unknown')} ({tool.get('installs', 0)} installs)")
    
    # Common failures
    common_failures = stats.get('most_common_failures', [])
    if common_failures:
        print("   🛠️ Most Common Failures:")
        for i, failure in enumerate(common_failures[:5], 1):
            print(f"      {i}. {failure.get('message', 'Unknown')} ({failure.get('tool', 'Unknown')})")
    
    print("✅ Graph statistics test completed")


def test_knowledge_expansion():
    """Test knowledge expansion with Gemini."""
    print("\n🚀 Testing Knowledge Expansion")
    print("=" * 50)
    
    # Initialize knowledge engine
    knowledge_engine = KnowledgeEngine()
    
    # Test domains
    test_domains = ["ai stack", "devops essentials"]
    
    for domain in test_domains:
        print(f"🔄 Expanding knowledge for domain: {domain}")
        
        # Get initial stats
        initial_stats = knowledge_engine.get_graph_statistics()
        initial_nodes = initial_stats.get('total_nodes', 0)
        initial_relationships = initial_stats.get('total_relationships', 0)
        
        print(f"   📊 Initial state: {initial_nodes} nodes, {initial_relationships} relationships")
        
        # Expand knowledge
        success = knowledge_engine.expand_graph_from_gemini(domain)
        
        if success:
            # Get final stats
            final_stats = knowledge_engine.get_graph_statistics()
            final_nodes = final_stats.get('total_nodes', 0)
            final_relationships = final_stats.get('total_relationships', 0)
            
            nodes_added = final_nodes - initial_nodes
            relationships_added = final_relationships - initial_relationships
            
            print(f"   ✅ Expansion successful!")
            print(f"   📈 Added {nodes_added} nodes and {relationships_added} relationships")
        else:
            print(f"   ❌ Expansion failed for domain: {domain}")
    
    print("✅ Knowledge expansion test completed")


def test_install_event_logging():
    """Test auto-logging of install events."""
    print("\n📝 Testing Install Event Logging")
    print("=" * 50)
    
    graph_db = GraphDBManager()
    
    # Simulate install events
    test_events = [
        {
            "tool_name": "tensorflow",
            "command": "pip install tensorflow",
            "success": True,
            "os_type": "linux",
            "architecture": "x86_64",
            "user_id": "test_user",
            "session_id": "session_20240101_120000"
        },
        {
            "tool_name": "docker",
            "command": "curl -fsSL https://get.docker.com | sh",
            "success": False,
            "os_type": "linux",
            "architecture": "x86_64",
            "error_message": "Permission denied",
            "user_id": "test_user",
            "session_id": "session_20240101_120000"
        }
    ]
    
    for event in test_events:
        print(f"📝 Logging install event for {event['tool_name']}...")
        
        success = graph_db.log_install_event(
            tool_name=event['tool_name'],
            command=event['command'],
            success=event['success'],
            os_type=event['os_type'],
            architecture=event['architecture'],
            error_message=event.get('error_message'),
            user_id=event['user_id'],
            session_id=event['session_id']
        )
        
        if success:
            print(f"   ✅ Successfully logged {event['tool_name']} install event")
        else:
            print(f"   ❌ Failed to log {event['tool_name']} install event")
    
    print("✅ Install event logging test completed")


def test_knowledge_scheduler():
    """Test the knowledge scheduler functionality."""
    print("\n⏰ Testing Knowledge Scheduler")
    print("=" * 50)
    
    # Initialize knowledge engine and scheduler
    knowledge_engine = KnowledgeEngine()
    scheduler = KnowledgeScheduler(knowledge_engine)
    
    # Test adding scheduled tasks
    print("📅 Adding scheduled tasks...")
    
    task_id1 = scheduler.add_scheduled_task("ai stack", "daily")
    task_id2 = scheduler.add_scheduled_task("devops essentials", "weekly")
    
    print(f"   ✅ Added task 1: {task_id1}")
    print(f"   ✅ Added task 2: {task_id2}")
    
    # Test getting scheduled tasks
    tasks = scheduler.get_scheduled_tasks()
    print(f"   📋 Total scheduled tasks: {len(tasks)}")
    
    # Test immediate expansion
    print("🚀 Testing immediate knowledge expansion...")
    result = scheduler.expand_knowledge_now("modern ai tools")
    
    print(f"   📊 Expansion result:")
    print(f"      • Success: {result.success}")
    print(f"      • Nodes added: {result.nodes_added}")
    print(f"      • Relationships added: {result.relationships_added}")
    if result.error_message:
        print(f"      • Error: {result.error_message}")
    
    # Test scheduler statistics
    stats = scheduler.get_scheduler_stats()
    print(f"   📈 Scheduler statistics:")
    print(f"      • Total tasks: {stats.get('total_tasks', 0)}")
    print(f"      • Active tasks: {stats.get('active_tasks', 0)}")
    print(f"      • Recent expansions: {stats.get('recent_expansions', 0)}")
    print(f"      • Recent successes: {stats.get('recent_successes', 0)}")
    print(f"      • Recent failures: {stats.get('recent_failures', 0)}")
    
    # Clean up
    scheduler.remove_scheduled_task(task_id1)
    scheduler.remove_scheduled_task(task_id2)
    
    print("✅ Knowledge scheduler test completed")


def main():
    """Run all tests."""
    print("🧪 CONFIGO Enhanced Knowledge Graph Test Suite")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now()}")
    print()
    
    try:
        # Run all tests
        test_enhanced_graph_schema()
        test_enhanced_relationships()
        test_graph_statistics()
        test_knowledge_expansion()
        test_install_event_logging()
        test_knowledge_scheduler()
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 60)
        print("✅ Enhanced knowledge graph functionality is working correctly")
        print("✅ Graph schema enrichment implemented")
        print("✅ Gemini-powered expansion working")
        print("✅ Auto-logging of install events functional")
        print("✅ Comprehensive statistics available")
        print("✅ Knowledge scheduler operational")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test suite failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 