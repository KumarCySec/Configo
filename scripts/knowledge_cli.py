#!/usr/bin/env python3
"""
CONFIGO Knowledge Layer CLI
============================

Command-line interface for testing and using the CONFIGO knowledge layer.
Provides commands for managing tools, errors, and user personas.

Usage:
    python scripts/knowledge_cli.py add-tool <name> <category> <description>
    python scripts/knowledge_cli.py log-error <tool> <error> [solution]
    python scripts/knowledge_cli.py search-errors <error_message>
    python scripts/knowledge_cli.py related-tools <tool_name>
    python scripts/knowledge_cli.py stats
    python scripts/knowledge_cli.py demo
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge import KnowledgeEngine
from knowledge.config import validate_and_setup


def setup_knowledge_engine():
    """Initialize the knowledge engine."""
    print("🔧 Initializing CONFIGO Knowledge Engine...")
    
    # Validate configuration
    validation = validate_and_setup()
    
    if not validation['valid']:
        print("❌ Configuration validation failed!")
        return None
    
    # Initialize knowledge engine
    try:
        engine = KnowledgeEngine()
        print("✅ Knowledge engine initialized successfully")
        return engine
    except Exception as e:
        print(f"❌ Failed to initialize knowledge engine: {e}")
        return None


def add_tool(engine, name, category, description, install_cmd, check_cmd):
    """Add a tool to the knowledge base."""
    print(f"📦 Adding tool: {name}")
    
    success = engine.add_tool_knowledge(
        tool_name=name,
        category=category,
        description=description,
        install_command=install_cmd,
        check_command=check_cmd
    )
    
    if success:
        print(f"✅ Successfully added tool: {name}")
    else:
        print(f"❌ Failed to add tool: {name}")


def log_error(engine, tool_name, error_message, solution=None):
    """Log an error message."""
    print(f"🚨 Logging error for {tool_name}: {error_message}")
    
    success = engine.vector_db.add_error_message(
        error_message=error_message,
        tool_name=tool_name,
        os_type="linux",
        architecture="x86_64",
        solution=solution
    )
    
    if success:
        print(f"✅ Successfully logged error for {tool_name}")
    else:
        print(f"❌ Failed to log error for {tool_name}")


def search_errors(engine, error_message):
    """Search for similar errors."""
    print(f"🔍 Searching for errors similar to: {error_message}")
    
    result = engine.query_similar_errors(error_message, limit=5)
    
    print(f"\n📊 Search Results (Confidence: {result.confidence:.2f}):")
    print(f"Source: {result.source}")
    print(f"Total Results: {len(result.results)}")
    
    for i, res in enumerate(result.results, 1):
        print(f"\n{i}. {res['type']}")
        print(f"   Content: {res['content'][:100]}...")
        print(f"   Similarity: {res['similarity']:.2f}")
        print(f"   Source: {res['source']}")


def get_related_tools(engine, tool_name):
    """Get tools related to the specified tool."""
    print(f"🔗 Finding tools related to: {tool_name}")
    
    result = engine.get_related_tools(tool_name, limit=5)
    
    print(f"\n📊 Related Tools (Confidence: {result.confidence:.2f}):")
    print(f"Source: {result.source}")
    print(f"Total Results: {len(result.results)}")
    
    for i, res in enumerate(result.results, 1):
        print(f"\n{i}. {res['type']}")
        print(f"   Content: {res['content'][:100]}...")
        print(f"   Similarity: {res['similarity']:.2f}")
        print(f"   Source: {res['source']}")


def get_statistics(engine):
    """Get knowledge base statistics."""
    print("📊 Knowledge Base Statistics")
    
    stats = engine.get_knowledge_statistics(days=30)
    
    print(f"\n📈 Graph Database:")
    graph_stats = stats.get('graph_database', {})
    print(f"   Total Installs: {graph_stats.get('total_installs', 0)}")
    print(f"   Successful: {graph_stats.get('successful_installs', 0)}")
    print(f"   Failed: {graph_stats.get('failed_installs', 0)}")
    print(f"   Success Rate: {graph_stats.get('success_rate', 0):.2%}")
    
    print(f"\n🔍 Vector Database:")
    vector_stats = stats.get('vector_database', {})
    print(f"   Errors: {vector_stats.get('errors', {}).get('count', 0)}")
    print(f"   Tools: {vector_stats.get('tools', {}).get('count', 0)}")
    print(f"   Personas: {vector_stats.get('personas', {}).get('count', 0)}")
    
    print(f"\n📅 Period: {stats.get('period_days', 0)} days")


def run_demo(engine):
    """Run a comprehensive demo of the knowledge layer."""
    print("🎯 CONFIGO Knowledge Layer Demo")
    print("=" * 50)
    
    # Add some sample tools
    print("\n1. 📦 Adding sample tools...")
    tools = [
        ("python", "language", "Python programming language", 
         "apt-get install python3", "python3 --version"),
        ("pip", "package_manager", "Python package installer", 
         "apt-get install python3-pip", "pip3 --version"),
        ("docker", "tool", "Container platform", 
         "apt-get install docker", "docker --version"),
        ("vscode", "editor", "Visual Studio Code", 
         "snap install code", "code --version"),
        ("git", "tool", "Version control system", 
         "apt-get install git", "git --version")
    ]
    
    for name, category, desc, install_cmd, check_cmd in tools:
        add_tool(engine, name, category, desc, install_cmd, check_cmd)
    
    # Add tool relationships
    print("\n2. 🔗 Adding tool relationships...")
    relationships = [
        ("python", "pip", "DEPENDS_ON"),
        ("python", "vscode", "USED_WITH"),
        ("docker", "git", "USED_WITH"),
        ("vscode", "git", "USED_WITH")
    ]
    
    for tool1, tool2, rel_type in relationships:
        success = engine.add_tool_relationship(tool1, tool2, rel_type)
        if success:
            print(f"   ✅ {tool1} --{rel_type}--> {tool2}")
        else:
            print(f"   ❌ Failed to add relationship: {tool1} --{rel_type}--> {tool2}")
    
    # Log some sample errors
    print("\n3. 🚨 Logging sample errors...")
    errors = [
        ("docker", "Permission denied", "Run with sudo"),
        ("python", "Package not found", "Update package list"),
        ("pip", "Connection timeout", "Check internet connection"),
        ("vscode", "Installation failed", "Try alternative installation method")
    ]
    
    for tool, error, solution in errors:
        log_error(engine, tool, error, solution)
    
    # Add user personas
    print("\n4. 👤 Adding user personas...")
    personas = [
        ("user1", "AI developer working with Python and TensorFlow", 
         {"auto_retry": True, "preferred_editor": "vscode"}),
        ("user2", "Data scientist using Python and Jupyter", 
         {"auto_retry": False, "preferred_editor": "jupyter"}),
        ("user3", "DevOps engineer using Docker and Git", 
         {"auto_retry": True, "preferred_editor": "vim"})
    ]
    
    for user_id, description, preferences in personas:
        success = engine.add_user_persona(user_id, description, preferences)
        if success:
            print(f"   ✅ Added persona: {user_id}")
        else:
            print(f"   ❌ Failed to add persona: {user_id}")
    
    # Demonstrate search functionality
    print("\n5. 🔍 Demonstrating search functionality...")
    
    print("\n   Searching for errors similar to 'Permission denied':")
    search_errors(engine, "Permission denied")
    
    print("\n   Finding tools related to 'python':")
    get_related_tools(engine, "python")
    
    print("\n   Finding users similar to 'AI developer':")
    result = engine.find_similar_users("AI developer working with Python", limit=3)
    print(f"   Found {len(result.results)} similar users (confidence: {result.confidence:.2f})")
    
    # Show statistics
    print("\n6. 📊 Final Statistics:")
    get_statistics(engine)
    
    print("\n🎉 Demo completed successfully!")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="CONFIGO Knowledge Layer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/knowledge_cli.py add-tool python language "Python programming language"
  python scripts/knowledge_cli.py log-error docker "Permission denied" "Run with sudo"
  python scripts/knowledge_cli.py search-errors "Permission denied"
  python scripts/knowledge_cli.py related-tools python
  python scripts/knowledge_cli.py stats
  python scripts/knowledge_cli.py demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add tool command
    add_tool_parser = subparsers.add_parser('add-tool', help='Add a tool to the knowledge base')
    add_tool_parser.add_argument('name', help='Tool name')
    add_tool_parser.add_argument('category', help='Tool category')
    add_tool_parser.add_argument('description', help='Tool description')
    add_tool_parser.add_argument('--install-cmd', default='apt-get install', help='Installation command')
    add_tool_parser.add_argument('--check-cmd', default='--version', help='Check command')
    
    # Log error command
    log_error_parser = subparsers.add_parser('log-error', help='Log an error message')
    log_error_parser.add_argument('tool', help='Tool name')
    log_error_parser.add_argument('error', help='Error message')
    log_error_parser.add_argument('solution', nargs='?', help='Solution (optional)')
    
    # Search errors command
    search_parser = subparsers.add_parser('search-errors', help='Search for similar errors')
    search_parser.add_argument('error_message', help='Error message to search for')
    
    # Related tools command
    related_parser = subparsers.add_parser('related-tools', help='Find related tools')
    related_parser.add_argument('tool_name', help='Tool name')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show knowledge base statistics')
    
    # Demo command
    subparsers.add_parser('demo', help='Run comprehensive demo')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize knowledge engine
    engine = setup_knowledge_engine()
    if not engine:
        return
    
    try:
        # Execute command
        if args.command == 'add-tool':
            add_tool(engine, args.name, args.category, args.description, 
                    args.install_cmd, args.check_cmd)
        
        elif args.command == 'log-error':
            log_error(engine, args.tool, args.error, args.solution)
        
        elif args.command == 'search-errors':
            search_errors(engine, args.error_message)
        
        elif args.command == 'related-tools':
            get_related_tools(engine, args.tool_name)
        
        elif args.command == 'stats':
            get_statistics(engine)
        
        elif args.command == 'demo':
            run_demo(engine)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        engine.close()


if __name__ == '__main__':
    main() 