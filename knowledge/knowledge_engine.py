"""
CONFIGO Knowledge Engine
========================

Central knowledge engine that coordinates between graph and vector databases
to provide intelligent, unified knowledge layer functionality.

Features:
- 🧠 Coordinated graph + vector queries
- 🔍 Intelligent error matching and resolution
- 🎯 Personalized tool recommendations
- 📊 Cross-database analytics and insights
- 🔄 Self-improving knowledge base
- 👤 User persona and preference learning
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .graph_db_manager import GraphDBManager
from .vector_store_manager import VectorStoreManager

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeQuery:
    """Represents a knowledge query with context."""
    query_type: str  # 'error', 'tool', 'user', 'recommendation'
    query_text: str
    context: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class KnowledgeResult:
    """Represents a knowledge query result."""
    query: KnowledgeQuery
    results: List[Dict[str, Any]]
    confidence: float
    source: str  # 'graph', 'vector', 'combined'
    metadata: Dict[str, Any]


class KnowledgeEngine:
    """
    Central knowledge engine for CONFIGO.
    
    Coordinates between graph and vector databases to provide intelligent
    knowledge layer functionality with unified APIs.
    """
    
    def __init__(self, graph_config: Optional[Dict[str, Any]] = None,
                 vector_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the knowledge engine.
        
        Args:
            graph_config: Configuration for graph database
            vector_config: Configuration for vector database
        """
        # Initialize graph database
        graph_config = graph_config or {}
        self.graph_db = GraphDBManager(
            uri=graph_config.get('uri'),
            username=graph_config.get('username'),
            password=graph_config.get('password'),
            storage_path=graph_config.get('storage_path', '.configo_graph')
        )
        
        # Initialize vector database
        vector_config = vector_config or {}
        self.vector_db = VectorStoreManager(
            storage_path=vector_config.get('storage_path', '.configo_vectors'),
            embedding_model=vector_config.get('embedding_model', 'all-MiniLM-L6-v2')
        )
        
        logger.info("Knowledge engine initialized")
    
    def log_install_event(self, tool_name: str, command: str, success: bool,
                         os_type: str, architecture: str, error_message: Optional[str] = None,
                         user_id: Optional[str] = None, session_id: Optional[str] = None,
                         retry_count: int = 0) -> bool:
        """
        Log an installation event to both graph and vector databases.
        
        Args:
            tool_name: Name of the tool being installed
            command: Installation command used
            success: Whether installation succeeded
            os_type: Operating system type
            architecture: System architecture
            error_message: Error message if failed
            user_id: User ID (optional)
            session_id: Session ID (optional)
            retry_count: Number of retry attempts
            
        Returns:
            bool: True if successful
        """
        try:
            # Log to graph database
            graph_success = self.graph_db.log_install_event(
                tool_name=tool_name,
                command=command,
                success=success,
                os_type=os_type,
                architecture=architecture,
                error_message=error_message,
                user_id=user_id,
                session_id=session_id,
                retry_count=retry_count
            )
            
            # Log error to vector database if failed
            vector_success = True
            if not success and error_message:
                vector_success = self.vector_db.add_error_message(
                    error_message=error_message,
                    tool_name=tool_name,
                    os_type=os_type,
                    architecture=architecture
                ) is not None
            
            return graph_success and vector_success
        except Exception as e:
            logger.error(f"Failed to log install event: {e}")
            return False
    
    def query_similar_errors(self, error_message: str, limit: int = 5) -> KnowledgeResult:
        """
        Search for similar error messages and their solutions.
        
        Args:
            error_message: Error message to search for
            limit: Maximum number of results
            
        Returns:
            KnowledgeResult: Similar errors with solutions and confidence scores
        """
        query = KnowledgeQuery(
            query_type='error',
            query_text=error_message,
            context={'limit': limit}
        )
        
        try:
            # Search in vector database
            vector_results = self.vector_db.search_similar_errors(error_message, limit)
            
            # Extract tool names from vector results for graph lookup
            tool_names = []
            for result in vector_results:
                metadata = result.get('metadata', {})
                tool_name = metadata.get('tool_name')
                if tool_name:
                    tool_names.append(tool_name)
            
            # Get related tools from graph database
            graph_results = []
            for tool_name in tool_names[:3]:  # Limit to top 3 tools
                related_tools = self.graph_db.get_related_tools(tool_name, limit=2)
                graph_results.extend(related_tools)
            
            # Combine and rank results
            combined_results = []
            
            # Add vector results (errors with solutions)
            for result in vector_results:
                combined_results.append({
                    'type': 'error_solution',
                    'content': result['content'],
                    'metadata': result['metadata'],
                    'similarity': result['similarity'],
                    'source': 'vector'
                })
            
            # Add graph results (related tools)
            for result in graph_results:
                combined_results.append({
                    'type': 'related_tool',
                    'content': f"Related tool: {result['name']} - {result['description']}",
                    'metadata': result,
                    'similarity': result.get('success_rate', 0.5),
                    'source': 'graph'
                })
            
            # Sort by similarity/confidence
            combined_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Calculate overall confidence
            confidence = sum(r['similarity'] for r in combined_results[:3]) / 3 if combined_results else 0.0
            
            return KnowledgeResult(
                query=query,
                results=combined_results[:limit],
                confidence=confidence,
                source='combined',
                metadata={
                    'vector_results': len(vector_results),
                    'graph_results': len(graph_results),
                    'total_results': len(combined_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to query similar errors: {e}")
            return KnowledgeResult(
                query=query,
                results=[],
                confidence=0.0,
                source='error',
                metadata={'error': str(e)}
            )
    
    def get_related_tools(self, tool_name: str, limit: int = 5) -> KnowledgeResult:
        """
        Get tools related to the specified tool using both graph and vector databases.
        
        Args:
            tool_name: Name of the tool
            limit: Maximum number of results
            
        Returns:
            KnowledgeResult: Related tools with metadata
        """
        query = KnowledgeQuery(
            query_type='tool',
            query_text=tool_name,
            context={'limit': limit}
        )
        
        try:
            # Get related tools from graph database
            graph_results = self.graph_db.get_related_tools(tool_name, limit)
            
            # Search for similar tools in vector database
            vector_results = self.vector_db.search_similar_tools(tool_name, limit)
            
            # Combine results
            combined_results = []
            
            # Add graph results (direct relationships)
            for result in graph_results:
                combined_results.append({
                    'type': 'graph_related',
                    'content': f"Graph related: {result['name']} - {result['description']}",
                    'metadata': result,
                    'similarity': result.get('success_rate', 0.5),
                    'source': 'graph'
                })
            
            # Add vector results (semantic similarity)
            for result in vector_results:
                metadata = result.get('metadata', {})
                if metadata.get('tool_name') != tool_name:  # Exclude self
                    combined_results.append({
                        'type': 'vector_similar',
                        'content': f"Semantically similar: {metadata.get('tool_name', 'Unknown')}",
                        'metadata': metadata,
                        'similarity': result['similarity'],
                        'source': 'vector'
                    })
            
            # Sort by similarity
            combined_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Calculate confidence
            confidence = sum(r['similarity'] for r in combined_results[:3]) / 3 if combined_results else 0.0
            
            return KnowledgeResult(
                query=query,
                results=combined_results[:limit],
                confidence=confidence,
                source='combined',
                metadata={
                    'graph_results': len(graph_results),
                    'vector_results': len(vector_results),
                    'total_results': len(combined_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get related tools: {e}")
            return KnowledgeResult(
                query=query,
                results=[],
                confidence=0.0,
                source='error',
                metadata={'error': str(e)}
            )
    
    def get_recommended_plan(self, user_profile: Dict[str, Any], 
                           target_environment: str) -> KnowledgeResult:
        """
        Get recommended installation plan using both graph and vector databases.
        
        Args:
            user_profile: User profile with preferences and history
            target_environment: Target environment (e.g., "ai-stack", "web-dev")
            
        Returns:
            KnowledgeResult: Recommended tools with installation order
        """
        query = KnowledgeQuery(
            query_type='recommendation',
            query_text=target_environment,
            context={'user_profile': user_profile}
        )
        
        try:
            # Get recommendations from graph database
            graph_results = self.graph_db.get_recommended_plan(user_profile, target_environment)
            
            # Search for similar environments in vector database
            vector_results = self.vector_db.search(
                target_environment, "tools", limit=5, similarity_threshold=0.4
            )
            
            # Combine results
            combined_results = []
            
            # Add graph results (based on user history and success rates)
            for result in graph_results:
                combined_results.append({
                    'type': 'graph_recommended',
                    'content': f"Recommended: {result['name']} - {result['description']}",
                    'metadata': result,
                    'similarity': result.get('avg_success', 0.5),
                    'source': 'graph'
                })
            
            # Add vector results (semantic similarity)
            for result in vector_results:
                metadata = result.get('metadata', {})
                combined_results.append({
                    'type': 'vector_similar',
                    'content': f"Semantically similar: {metadata.get('tool_name', 'Unknown')}",
                    'metadata': metadata,
                    'similarity': result['similarity'],
                    'source': 'vector'
                })
            
            # Sort by similarity/confidence
            combined_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Calculate confidence
            confidence = sum(r['similarity'] for r in combined_results[:5]) / 5 if combined_results else 0.0
            
            return KnowledgeResult(
                query=query,
                results=combined_results,
                confidence=confidence,
                source='combined',
                metadata={
                    'graph_results': len(graph_results),
                    'vector_results': len(vector_results),
                    'total_results': len(combined_results),
                    'target_environment': target_environment
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get recommended plan: {e}")
            return KnowledgeResult(
                query=query,
                results=[],
                confidence=0.0,
                source='error',
                metadata={'error': str(e)}
            )
    
    def add_tool_knowledge(self, tool_name: str, category: str, description: str,
                          install_command: str, check_command: str) -> bool:
        """
        Add tool knowledge to both graph and vector databases.
        
        Args:
            tool_name: Name of the tool
            category: Tool category
            description: Tool description
            install_command: Installation command
            check_command: Command to check if tool is installed
            
        Returns:
            bool: True if successful
        """
        try:
            # Add to graph database
            graph_success = self.graph_db.add_tool(
                name=tool_name,
                category=category,
                description=description,
                install_command=install_command,
                check_command=check_command
            )
            
            # Add to vector database
            vector_success = self.vector_db.add_tool_description(
                tool_name=tool_name,
                description=description,
                category=category,
                install_command=install_command
            ) is not None
            
            return graph_success and vector_success
        except Exception as e:
            logger.error(f"Failed to add tool knowledge: {e}")
            return False
    
    def add_tool_relationship(self, tool1: str, tool2: str, 
                            relationship_type: str = "USED_WITH") -> bool:
        """
        Add a relationship between two tools.
        
        Args:
            tool1: First tool name
            tool2: Second tool name
            relationship_type: Type of relationship (DEPENDS_ON, USED_WITH, SIMILAR_TO)
            
        Returns:
            bool: True if successful
        """
        try:
            return self.graph_db.add_relationship(tool1, tool2, relationship_type)
        except Exception as e:
            logger.error(f"Failed to add tool relationship: {e}")
            return False
    
    def get_knowledge_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive knowledge statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict[str, Any]: Statistics from both graph and vector databases
        """
        try:
            # Get graph statistics
            graph_stats = self.graph_db.get_install_statistics(days)
            
            # Get vector statistics
            vector_stats = {
                'errors': self.vector_db.get_collection_stats('errors'),
                'tools': self.vector_db.get_collection_stats('tools'),
                'personas': self.vector_db.get_collection_stats('personas')
            }
            
            return {
                'graph_database': graph_stats,
                'vector_database': vector_stats,
                'period_days': days,
                'total_errors': vector_stats['errors'].get('count', 0),
                'total_tools': vector_stats['tools'].get('count', 0),
                'total_personas': vector_stats['personas'].get('count', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get knowledge statistics: {e}")
            return {}
    
    def find_similar_users(self, persona_description: str, limit: int = 5) -> KnowledgeResult:
        """
        Find users with similar personas using vector database.
        
        Args:
            persona_description: Description of the user persona
            limit: Maximum number of results
            
        Returns:
            KnowledgeResult: Similar users with metadata
        """
        query = KnowledgeQuery(
            query_type='user',
            query_text=persona_description,
            context={'limit': limit}
        )
        
        try:
            vector_results = self.vector_db.find_similar_users(persona_description, limit)
            
            # Convert to standard format
            results = []
            for result in vector_results:
                results.append({
                    'type': 'similar_user',
                    'content': result['content'],
                    'metadata': result['metadata'],
                    'similarity': result['similarity'],
                    'source': 'vector'
                })
            
            # Calculate confidence
            confidence = sum(r['similarity'] for r in results[:3]) / 3 if results else 0.0
            
            return KnowledgeResult(
                query=query,
                results=results,
                confidence=confidence,
                source='vector',
                metadata={
                    'total_results': len(results),
                    'persona_description': persona_description
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to find similar users: {e}")
            return KnowledgeResult(
                query=query,
                results=[],
                confidence=0.0,
                source='error',
                metadata={'error': str(e)}
            )
    
    def add_user_persona(self, user_id: str, persona_description: str,
                        preferences: Dict[str, Any]) -> bool:
        """
        Add user persona to vector database.
        
        Args:
            user_id: User ID
            persona_description: Description of the user persona
            preferences: User preferences
            
        Returns:
            bool: True if successful
        """
        try:
            return self.vector_db.add_user_persona(
                user_id=user_id,
                persona_description=persona_description,
                preferences=preferences
            ) is not None
        except Exception as e:
            logger.error(f"Failed to add user persona: {e}")
            return False
    
    def get_combined_insights(self, tool_name: str) -> Dict[str, Any]:
        """
        Get comprehensive insights about a tool from both databases.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dict[str, Any]: Combined insights from graph and vector databases
        """
        try:
            insights = {
                'tool_name': tool_name,
                'graph_insights': {},
                'vector_insights': {},
                'combined_recommendations': []
            }
            
            # Get graph insights
            related_tools = self.graph_db.get_related_tools(tool_name, limit=5)
            insights['graph_insights'] = {
                'related_tools': related_tools,
                'total_related': len(related_tools)
            }
            
            # Get vector insights
            similar_tools = self.vector_db.search_similar_tools(tool_name, limit=5)
            insights['vector_insights'] = {
                'similar_tools': similar_tools,
                'total_similar': len(similar_tools)
            }
            
            # Combine recommendations
            all_tools = set()
            
            # Add graph-related tools
            for tool in related_tools:
                all_tools.add(tool['name'])
            
            # Add vector-similar tools
            for tool in similar_tools:
                metadata = tool.get('metadata', {})
                tool_name_from_vector = metadata.get('tool_name')
                if tool_name_from_vector:
                    all_tools.add(tool_name_from_vector)
            
            insights['combined_recommendations'] = list(all_tools)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get combined insights: {e}")
            return {'error': str(e)}
    
    def close(self) -> None:
        """Close database connections."""
        try:
            self.graph_db.close()
            logger.info("Knowledge engine connections closed")
        except Exception as e:
            logger.error(f"Failed to close knowledge engine: {e}") 