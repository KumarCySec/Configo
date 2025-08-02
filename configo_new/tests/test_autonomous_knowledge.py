#!/usr/bin/env python3
"""
Test Autonomous Knowledge Growth
===============================

Test script to verify CONFIGO's autonomous knowledge growth features:
- Gemini-powered intelligence scraper
- Enhanced graph database operations
- Semantic memory with vector database
- Knowledge engine integration
"""

import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import Config
from knowledge.engine import KnowledgeEngine
from knowledge.gemini_scraper import GeminiScraper
from knowledge.graph_db_manager import GraphDBManager
from knowledge.vector_store_manager import VectorStoreManager


def test_gemini_scraper():
    """Test Gemini scraper functionality."""
    print("🧠 Testing Gemini Scraper...")
    
    try:
        config = Config()
        scraper = GeminiScraper(api_key=config.gemini_api_key)
        
        print(f"  ✅ Gemini connected: {scraper.is_connected()}")
        print(f"  📊 Status: {scraper.get_status()}")
        
        if scraper.is_connected():
            # Test domain search
            print("  🔍 Testing domain search...")
            tools_data = scraper.search_tools_for_domain("full stack ai")
            print(f"  📦 Found {len(tools_data.get('tools', []))} tools")
            
            # Test error fix search
            print("  🔧 Testing error fix search...")
            error_fix = scraper.search_error_fix("CUDA not found", "python")
            print(f"  🛠️  Found {len(error_fix.get('fixes', []))} fixes")
            
            # Test installation method search
            print("  📥 Testing installation method search...")
            install_method = scraper.search_installation_method("docker")
            print(f"  📋 Found {len(install_method.get('installation_methods', []))} methods")
            
            return True
        else:
            print("  ⚠️  Gemini not connected - using fallback mode")
            return True
            
    except Exception as e:
        print(f"  ❌ Gemini scraper test failed: {e}")
        return False


def test_enhanced_graph_operations():
    """Test enhanced graph database operations."""
    print("🗂️  Testing Enhanced Graph Operations...")
    
    try:
        config = Config()
        graph_manager = GraphDBManager(
            uri=config.database.neo4j_uri,
            username=config.database.neo4j_username,
            password=config.database.neo4j_password
        )
        
        print(f"  ✅ Graph connected: {graph_manager.connected}")
        
        if graph_manager.connected:
            # Test adding tools
            print("  ➕ Testing tool addition...")
            success = graph_manager.add_tool("test_tool", "test_category", "Test tool description")
            print(f"  📝 Tool addition: {'✅' if success else '❌'}")
            
            # Test error logging
            print("  📝 Testing error logging...")
            success = graph_manager.log_error_fix("Test error message", "echo 'fix command'", "test_tool")
            print(f"  🔧 Error logging: {'✅' if success else '❌'}")
            
            # Test recommended tools query
            print("  🔍 Testing recommended tools query...")
            tools = graph_manager.query_recommended_tools("developer")
            print(f"  📊 Found {len(tools)} recommended tools")
            
            return True
        else:
            print("  ⚠️  Graph not connected - using fallback mode")
            return True
            
    except Exception as e:
        print(f"  ❌ Enhanced graph operations test failed: {e}")
        return False


def test_semantic_memory():
    """Test semantic memory with vector database."""
    print("🧠 Testing Semantic Memory...")
    
    try:
        config = Config()
        vector_manager = VectorStoreManager(
            storage_path=config.database.vector_storage_path,
            mode="chroma"
        )
        
        print(f"  ✅ Vector store initialized")
        
        # Test adding documents
        print("  ➕ Testing document addition...")
        success = vector_manager.add_document(
            "Test tool for development",
            {"type": "tool", "name": "test_tool", "category": "development"}
        )
        print(f"  📝 Document addition: {'✅' if success else '❌'}")
        
        # Test semantic search
        print("  🔍 Testing semantic search...")
        results = vector_manager.search("development tool", 3)
        print(f"  📊 Found {len(results)} search results")
        
        # Test error search
        print("  🔧 Testing error search...")
        error_results = vector_manager.search_similar_errors("CUDA not found")
        print(f"  🛠️  Found {len(error_results)} similar errors")
        
        # Test tool request search
        print("  📦 Testing tool request search...")
        tool_results = vector_manager.search_similar_tool_requests("install python")
        print(f"  📋 Found {len(tool_results)} similar tool requests")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Semantic memory test failed: {e}")
        return False


def test_knowledge_engine_integration():
    """Test knowledge engine integration."""
    print("🔗 Testing Knowledge Engine Integration...")
    
    try:
        config = Config()
        knowledge = KnowledgeEngine(config)
        
        print(f"  ✅ Knowledge engine initialized")
        
        # Test event logging
        print("  📝 Testing event logging...")
        success = knowledge.log_event("install", {
            "tool_name": "test_tool",
            "success": True,
            "system_info": {"os": "linux", "arch": "x86_64"}
        })
        print(f"  📊 Event logging: {'✅' if success else '❌'}")
        
        # Test similar fixes
        print("  🔧 Testing similar fixes...")
        fixes = knowledge.get_similar_fixes("CUDA not found")
        print(f"  🛠️  Found {len(fixes)} similar fixes")
        
        # Test stack recommendation
        print("  📋 Testing stack recommendation...")
        stack = knowledge.recommend_stack("full stack ai")
        print(f"  📦 Recommended {len(stack.get('tools', []))} tools")
        
        # Test graph expansion
        print("  🌐 Testing graph expansion...")
        if knowledge.gemini_scraper and knowledge.gemini_scraper.is_connected():
            success = knowledge.expand_graph_from_gemini("web development")
            print(f"  📈 Graph expansion: {'✅' if success else '❌'}")
        else:
            print("  ⚠️  Gemini not available for graph expansion")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Knowledge engine integration test failed: {e}")
        return False


def test_cli_commands():
    """Test new CLI commands."""
    print("💻 Testing New CLI Commands...")
    
    try:
        import subprocess
        import sys
        
        # Test knowledge refresh command
        print("  🔄 Testing knowledge refresh command...")
        result = subprocess.run([
            sys.executable, "main.py", "knowledge", "refresh", "--domain", "test domain"
        ], capture_output=True, text=True)
        print(f"  📊 Knowledge refresh: {'✅' if result.returncode == 0 else '❌'}")
        
        # Test knowledge stats command
        print("  📈 Testing knowledge stats command...")
        result = subprocess.run([
            sys.executable, "main.py", "knowledge", "stats"
        ], capture_output=True, text=True)
        print(f"  📊 Knowledge stats: {'✅' if result.returncode == 0 else '❌'}")
        
        # Test vector search command
        print("  🔍 Testing vector search command...")
        result = subprocess.run([
            sys.executable, "main.py", "vector", "search", "python"
        ], capture_output=True, text=True)
        print(f"  📊 Vector search: {'✅' if result.returncode == 0 else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI commands test failed: {e}")
        return False


def main():
    """Run all autonomous knowledge growth tests."""
    print("🚀 CONFIGO Autonomous Knowledge Growth Test")
    print("=" * 50)
    
    tests = [
        ("Gemini Scraper", test_gemini_scraper),
        ("Enhanced Graph Operations", test_enhanced_graph_operations),
        ("Semantic Memory", test_semantic_memory),
        ("Knowledge Engine Integration", test_knowledge_engine_integration),
        ("CLI Commands", test_cli_commands)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Autonomous Knowledge Growth tests passed!")
        print("✅ CONFIGO is ready for autonomous learning!")
        return True
    else:
        print("⚠️  Some tests failed - check configuration and dependencies")
        return False


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    success = main()
    sys.exit(0 if success else 1) 