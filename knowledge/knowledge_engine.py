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
        Get comprehensive knowledge base statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict[str, Any]: Complete knowledge statistics
        """
        try:
            stats = {
                'graph': {},
                'vector': {},
                'combined': {}
            }
            
            # Get graph statistics
            if self.graph_db:
                stats['graph'] = self.graph_db.get_graph_statistics()
            
            # Get vector statistics
            if self.vector_db:
                stats['vector'] = self.vector_db.get_statistics()
            
            # Calculate combined statistics
            if stats['graph'] and stats['vector']:
                stats['combined'] = {
                    'total_nodes': stats['graph'].get('total_nodes', 0),
                    'total_relationships': stats['graph'].get('total_relationships', 0),
                    'total_documents': stats['vector'].get('total_documents', 0),
                    'embedding_model': stats['vector'].get('embedding_model', 'Unknown')
                }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get knowledge statistics: {e}")
            return {}

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dict[str, Any]: Complete graph statistics
        """
        try:
            if self.graph_db:
                return self.graph_db.get_graph_statistics()
            return {}
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
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

    def expand_graph_from_gemini(self, domain: str) -> bool:
        """
        Expand knowledge graph using Gemini scraper with rich metadata extraction.
        
        Args:
            domain: Domain to expand (e.g., "ai stack", "devops essentials")
            
        Returns:
            bool: Success status
        """
        try:
            if not self.gemini_scraper or not self.gemini_scraper.is_connected():
                logger.warning("Gemini scraper not available, using fallback")
                return self._expand_graph_fallback(domain)
            
            # Get comprehensive tool data from Gemini
            tools_data = self.gemini_scraper.search_tools_for_domain(domain)
            
            if not tools_data or not tools_data.get('tools'):
                logger.warning(f"No tools found for domain: {domain}")
                return False
            
            # Process each tool with rich metadata
            for tool_data in tools_data.get('tools', []):
                success = self._process_tool_with_metadata(tool_data, domain)
                if not success:
                    logger.error(f"Failed to process tool: {tool_data.get('name', 'Unknown')}")
            
            # Add domain knowledge to vector store
            if self.vector_db:
                domain_content = self._create_domain_content(tools_data, domain)
                metadata = {
                    'type': 'domain_knowledge',
                    'domain': domain,
                    'timestamp': datetime.now().isoformat(),
                    'tool_count': len(tools_data.get('tools', []))
                }
                self.vector_db.add_document(domain_content, metadata)
            
            logger.info(f"Successfully expanded graph for domain: {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to expand graph from Gemini: {e}")
            return False

    def _process_tool_with_metadata(self, tool_data: Dict[str, Any], domain: str) -> bool:
        """Process a tool with comprehensive metadata extraction."""
        try:
            tool_name = tool_data.get('name', '')
            if not tool_name:
                return False
            
            # Add tool with enhanced metadata
            success = self.graph_db.add_tool(
                name=tool_name,
                category=tool_data.get('category', 'unknown'),
                description=tool_data.get('description', ''),
                install_command=tool_data.get('install_command', ''),
                check_command=tool_data.get('check_command', '')
            )
            
            if not success:
                return False
            
            # Add libraries/dependencies
            for dep in tool_data.get('dependencies', []):
                self.graph_db.add_library(
                    name=dep.get('name', ''),
                    version=dep.get('version', 'latest'),
                    language=dep.get('language', 'unknown'),
                    description=dep.get('description', ''),
                    compatibility=dep.get('compatibility', [])
                )
                self.graph_db.add_tool_dependency(tool_name, dep.get('name', ''))
            
            # Add OS requirements
            for os_req in tool_data.get('os_requirements', []):
                self.graph_db.add_tool_requirement(
                    tool_name=tool_name,
                    os_name=os_req.get('os', ''),
                    os_version=os_req.get('version', '')
                )
            
            # Add common errors and fixes
            for error in tool_data.get('common_errors', []):
                error_id = f"{tool_name}_{error.get('id', 'error')}"
                self.graph_db.add_error(
                    error_id=error_id,
                    message=error.get('message', ''),
                    solution=error.get('solution', ''),
                    severity=error.get('severity', 'medium'),
                    tool_name=tool_name,
                    os_type=error.get('os_type', 'unknown')
                )
                
                # Add fix command if available
                if error.get('fix_command'):
                    command_id = f"{error_id}_fix"
                    self.graph_db.add_command(
                        command_id=command_id,
                        command=error.get('fix_command', ''),
                        description=f"Fix for {error.get('message', '')}",
                        tool_name=tool_name,
                        os_type=error.get('os_type', 'unknown')
                    )
                    self.graph_db.add_error_fix(error_id, command_id)
            
            # Add features
            for feature in tool_data.get('features', []):
                self.graph_db.add_feature(
                    name=feature.get('name', ''),
                    description=feature.get('description', ''),
                    tool_name=tool_name
                )
                self.graph_db.add_tool_feature(tool_name, feature.get('name', ''))
            
            # Add categories
            for category in tool_data.get('categories', []):
                self.graph_db.add_category(
                    name=category.get('name', ''),
                    description=category.get('description', ''),
                    parent_category=category.get('parent', None)
                )
                self.graph_db.add_tool_category(tool_name, category.get('name', ''))
            
            # Add related tools
            for related_tool in tool_data.get('related_tools', []):
                self.graph_db.add_relationship(tool_name, related_tool, 'RELATED_TO')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process tool with metadata: {e}")
            return False

    def _create_domain_content(self, tools_data: Dict[str, Any], domain: str) -> str:
        """Create comprehensive domain content for vector storage."""
        content_parts = [f"Domain: {domain}"]
        
        for tool in tools_data.get('tools', []):
            tool_content = f"""
Tool: {tool.get('name', 'Unknown')}
Category: {tool.get('category', 'Unknown')}
Description: {tool.get('description', 'No description')}
Install Command: {tool.get('install_command', 'Unknown')}
Dependencies: {', '.join([dep.get('name', '') for dep in tool.get('dependencies', [])])}
Features: {', '.join([feat.get('name', '') for feat in tool.get('features', [])])}
Common Errors: {', '.join([err.get('message', '') for err in tool.get('common_errors', [])])}
"""
            content_parts.append(tool_content)
        
        return "\n".join(content_parts)

    def _expand_graph_fallback(self, domain: str) -> bool:
        """Fallback method when Gemini is not available."""
        try:
            # Use predefined knowledge for common domains
            fallback_data = self._get_fallback_domain_data(domain)
            
            if not fallback_data:
                logger.warning(f"No fallback data available for domain: {domain}")
                return False
            
            for tool_data in fallback_data:
                self._process_tool_with_metadata(tool_data, domain)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to expand graph with fallback: {e}")
            return False

    def _get_fallback_domain_data(self, domain: str) -> List[Dict[str, Any]]:
        """Get fallback data for common domains."""
        fallback_data = {
            "ai stack": [
                {
                    "name": "tensorflow",
                    "category": "machine_learning",
                    "description": "Open source machine learning framework",
                    "install_command": "pip install tensorflow",
                    "check_command": "python -c 'import tensorflow'",
                    "dependencies": [
                        {"name": "numpy", "version": "1.19.0", "language": "python"}
                    ],
                    "os_requirements": [
                        {"os": "linux", "version": "18.04+"},
                        {"os": "macos", "version": "10.15+"}
                    ],
                    "common_errors": [
                        {
                            "id": "cuda_error",
                            "message": "CUDA not found",
                            "solution": "Install CUDA toolkit",
                            "severity": "medium",
                            "os_type": "linux",
                            "fix_command": "sudo apt-get install nvidia-cuda-toolkit"
                        }
                    ],
                    "features": [
                        {"name": "GPU Support", "description": "CUDA acceleration"},
                        {"name": "Keras Integration", "description": "High-level API"}
                    ],
                    "categories": [
                        {"name": "Deep Learning", "description": "Neural network frameworks"}
                    ],
                    "related_tools": ["pytorch", "keras", "scikit-learn"]
                }
            ],
            "devops essentials": [
                {
                    "name": "docker",
                    "category": "containerization",
                    "description": "Container platform for applications",
                    "install_command": "curl -fsSL https://get.docker.com | sh",
                    "check_command": "docker --version",
                    "dependencies": [],
                    "os_requirements": [
                        {"os": "linux", "version": "18.04+"}
                    ],
                    "common_errors": [
                        {
                            "id": "permission_error",
                            "message": "Permission denied",
                            "solution": "Add user to docker group",
                            "severity": "low",
                            "os_type": "linux",
                            "fix_command": "sudo usermod -aG docker $USER"
                        }
                    ],
                    "features": [
                        {"name": "Container Management", "description": "Create and manage containers"},
                        {"name": "Image Registry", "description": "Docker Hub integration"}
                    ],
                    "categories": [
                        {"name": "Containerization", "description": "Container platforms"}
                    ],
                    "related_tools": ["kubernetes", "docker-compose", "podman"]
                }
            ]
        }
        
        return fallback_data.get(domain.lower(), []) 