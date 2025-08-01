"""
CONFIGO Knowledge Layer
======================

A modular, production-ready graph + vector knowledge layer for CONFIGO CLI.
Provides intelligent memory, semantic search, and relationship modeling capabilities.

Features:
- 🧠 Graph Database (Neo4j) for relationship modeling
- 🔍 Vector Database (Chroma/FAISS) for semantic search
- 🎯 Knowledge Engine for coordinated queries
- 📊 Install event tracking and analytics
- 🔄 Self-improving recommendations
- 👤 User persona similarity detection
- 🛠️ Tool dependency graph modeling

Usage:
    from knowledge import KnowledgeEngine
    
    engine = KnowledgeEngine()
    engine.log_install_event("docker", "apt-get install docker", True)
    similar_errors = engine.query_similar_errors("permission denied")
    related_tools = engine.get_related_tools("python")
"""

from .graph_db_manager import GraphDBManager
from .vector_store_manager import VectorStoreManager
from .knowledge_engine import KnowledgeEngine

__all__ = [
    'GraphDBManager',
    'VectorStoreManager', 
    'KnowledgeEngine'
] 