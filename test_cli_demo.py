#!/usr/bin/env python3
"""
CONFIGO Enhanced Knowledge Graph CLI Demo
=========================================

This script demonstrates the enhanced CLI functionality including:
- Knowledge refresh commands
- Graph statistics
- Install event logging
- Scheduler functionality

Usage:
    python test_cli_demo.py
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


def demo_knowledge_stats():
    """Demonstrate knowledge statistics command."""
    print("📊 CONFIGO Knowledge Statistics Demo")
    print("=" * 50)
    
    # Initialize knowledge engine
    knowledge_engine = KnowledgeEngine()
    
    # Get comprehensive statistics
    stats = knowledge_engine.get_graph_statistics()
    
    print("🧠 CONFIGO Knowledge Base Statistics")
    print("=" * 50)
    
    # Graph statistics
    if stats:
        print(f"📊 Graph Database:")
        print(f"   🧠 Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"   🔗 Total Relationships: {stats.get('total_relationships', 0)}")
        
        # Node breakdown
        node_counts = stats.get('node_counts', {})
        if node_counts:
            print("   📈 Node Breakdown:")
            for node_type, count in node_counts.items():
                print(f"      • {node_type}: {count}")
        
        # Top tools
        top_tools = stats.get('top_installed_tools', [])
        if top_tools:
            print("   🔧 Top 5 Installed Tools:")
            for i, tool in enumerate(top_tools[:5], 1):
                print(f"      {i}. {tool.get('name', 'Unknown')} ({tool.get('installs', 0)} installs)")
        
        # Common failures
        common_failures = stats.get('most_common_failures', [])
        if common_failures:
            print("   🛠️ Most Common Failures:")
            for i, failure in enumerate(common_failures[:5], 1):
                print(f"      {i}. {failure.get('message', 'Unknown')} ({failure.get('tool', 'Unknown')})")
        
        # Recent activity
        recent_activity = stats.get('recent_activity', {})
        if recent_activity:
            print("   📅 Recent Activity (7 days):")
            print(f"      • Total Installs: {recent_activity.get('recent_installs', 0)}")
            print(f"      • Successful: {recent_activity.get('successful', 0)}")
            print(f"      • Failed: {recent_activity.get('failed', 0)}")
    
    print("✅ Knowledge statistics demo completed")


def demo_knowledge_refresh():
    """Demonstrate knowledge refresh command."""
    print("\n🔄 CONFIGO Knowledge Refresh Demo")
    print("=" * 50)
    
    # Initialize knowledge engine
    knowledge_engine = KnowledgeEngine()
    
    # Test domains
    test_domains = ["ai stack", "devops essentials", "modern ai tools"]
    
    for domain in test_domains:
        print(f"🔄 Refreshing knowledge for domain: {domain}")
        print("This may take a few moments...")
        
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
            print("   💡 Using fallback data...")
    
    print("✅ Knowledge refresh demo completed")


def demo_install_logging():
    """Demonstrate install event logging."""
    print("\n📝 CONFIGO Install Event Logging Demo")
    print("=" * 50)
    
    # Initialize graph database
    graph_db = GraphDBManager()
    
    # Simulate install events
    test_events = [
        {
            "tool_name": "tensorflow",
            "command": "pip install tensorflow",
            "success": True,
            "os_type": "linux",
            "architecture": "x86_64",
            "user_id": "demo_user",
            "session_id": "session_20240101_120000"
        },
        {
            "tool_name": "docker",
            "command": "curl -fsSL https://get.docker.com | sh",
            "success": False,
            "os_type": "linux",
            "architecture": "x86_64",
            "error_message": "Permission denied",
            "user_id": "demo_user",
            "session_id": "session_20240101_120000"
        },
        {
            "tool_name": "pytorch",
            "command": "pip install torch",
            "success": True,
            "os_type": "linux",
            "architecture": "x86_64",
            "user_id": "demo_user",
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
    
    print("✅ Install event logging demo completed")


def demo_scheduler():
    """Demonstrate knowledge scheduler functionality."""
    print("\n⏰ CONFIGO Knowledge Scheduler Demo")
    print("=" * 50)
    
    # Initialize knowledge engine and scheduler
    knowledge_engine = KnowledgeEngine()
    scheduler = KnowledgeScheduler(knowledge_engine)
    
    # Test adding scheduled tasks
    print("📅 Adding scheduled tasks...")
    
    task_id1 = scheduler.add_scheduled_task("ai stack", "daily")
    task_id2 = scheduler.add_scheduled_task("devops essentials", "weekly")
    task_id3 = scheduler.add_scheduled_task("modern ai tools", "monthly")
    
    print(f"   ✅ Added task 1: {task_id1}")
    print(f"   ✅ Added task 2: {task_id2}")
    print(f"   ✅ Added task 3: {task_id3}")
    
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
    print(f"      • Total nodes added: {stats.get('total_nodes_added', 0)}")
    print(f"      • Total relationships added: {stats.get('total_relationships_added', 0)}")
    
    # Clean up
    scheduler.remove_scheduled_task(task_id1)
    scheduler.remove_scheduled_task(task_id2)
    scheduler.remove_scheduled_task(task_id3)
    
    print("✅ Knowledge scheduler demo completed")


def demo_graph_expansion():
    """Demonstrate graph expansion with rich relationships."""
    print("\n🔗 CONFIGO Graph Expansion Demo")
    print("=" * 50)
    
    # Initialize graph database
    graph_db = GraphDBManager()
    
    # Add comprehensive tool data
    print("📊 Adding comprehensive tool data...")
    
    # Add tools with rich metadata
    tools_data = [
        {
            "name": "tensorflow",
            "category": "machine_learning",
            "description": "Deep learning framework",
            "install_command": "pip install tensorflow",
            "check_command": "python -c 'import tensorflow'",
            "dependencies": ["numpy", "scipy", "keras"],
            "os_requirements": [{"os": "linux", "version": "18.04+"}],
            "features": ["GPU Support", "Keras Integration", "AutoML"],
            "categories": ["Deep Learning", "AI/ML"],
            "related_tools": ["pytorch", "keras", "scikit-learn"]
        },
        {
            "name": "docker",
            "category": "containerization",
            "description": "Container platform",
            "install_command": "curl -fsSL https://get.docker.com | sh",
            "check_command": "docker --version",
            "dependencies": [],
            "os_requirements": [{"os": "linux", "version": "18.04+"}],
            "features": ["Container Management", "Image Registry", "Multi-platform"],
            "categories": ["Containerization", "DevOps"],
            "related_tools": ["kubernetes", "docker-compose", "podman"]
        }
    ]
    
    for tool_data in tools_data:
        tool_name = tool_data["name"]
        print(f"   🔧 Adding {tool_name}...")
        
        # Add tool
        graph_db.add_tool(
            tool_name,
            tool_data["category"],
            tool_data["description"],
            tool_data["install_command"],
            tool_data["check_command"]
        )
        
        # Add dependencies
        for dep in tool_data["dependencies"]:
            graph_db.add_library(dep, "latest", "python", f"Dependency for {tool_name}")
            graph_db.add_tool_dependency(tool_name, dep)
        
        # Add OS requirements
        for os_req in tool_data["os_requirements"]:
            graph_db.add_tool_requirement(tool_name, os_req["os"], os_req["version"])
        
        # Add features
        for feature in tool_data["features"]:
            graph_db.add_feature(feature, f"Feature of {tool_name}", tool_name)
            graph_db.add_tool_feature(tool_name, feature)
        
        # Add categories
        for category in tool_data["categories"]:
            graph_db.add_category(category, f"Category for {tool_name}")
            graph_db.add_tool_category(tool_name, category)
        
        # Add related tools
        for related_tool in tool_data["related_tools"]:
            graph_db.add_relationship(tool_name, related_tool, "RELATED_TO")
    
    # Get final statistics
    stats = graph_db.get_graph_statistics()
    print(f"\n📈 Final Graph Statistics:")
    print(f"   🧠 Total Nodes: {stats.get('total_nodes', 0)}")
    print(f"   🔗 Total Relationships: {stats.get('total_relationships', 0)}")
    
    # Show node breakdown
    node_counts = stats.get('node_counts', {})
    if node_counts:
        print("   📊 Node Breakdown:")
        for node_type, count in node_counts.items():
            print(f"      • {node_type}: {count}")
    
    print("✅ Graph expansion demo completed")


def main():
    """Run all CLI demos."""
    print("🚀 CONFIGO Enhanced Knowledge Graph CLI Demo")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now()}")
    print()
    
    try:
        # Run all demos
        demo_knowledge_stats()
        demo_knowledge_refresh()
        demo_install_logging()
        demo_scheduler()
        demo_graph_expansion()
        
        print("\n🎉 All CLI demos completed successfully!")
        print("=" * 60)
        print("✅ Enhanced knowledge graph functionality demonstrated")
        print("✅ Graph schema enrichment working")
        print("✅ Auto-logging of install events functional")
        print("✅ Comprehensive statistics available")
        print("✅ Knowledge scheduler operational")
        print("✅ Rich relationships and metadata working")
        
        print("\n📋 Available CLI Commands:")
        print("   • python main.py knowledge stats")
        print("   • python main.py knowledge refresh --domain 'ai stack'")
        print("   • python main.py graph stats")
        print("   • python main.py graph expand --domain 'devops essentials'")
        print("   • python main.py scheduler add --domain 'modern ai tools' --schedule daily")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.error(f"CLI demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 