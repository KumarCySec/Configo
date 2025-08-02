"""
CONFIGO Knowledge Engine
========================

Handles graph and vector database operations for CONFIGO.
Provides semantic search, relationship mapping, and knowledge retrieval.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeEngine:
    """
    Core knowledge engine for CONFIGO.
    
    Handles graph database operations, vector search, and knowledge
    retrieval for intelligent decision making.
    """
    
    def __init__(self, config=None):
        """Initialize the knowledge engine."""
        self.config = config
        self.graph_manager = None
        self.vector_manager = None
        self.gemini_scraper = None
        
        self._initialize_managers()
        self._initialize_gemini_scraper()
        logger.info("CONFIGO Knowledge Engine initialized")
    
    def _initialize_managers(self) -> None:
        """Initialize graph and vector database managers."""
        try:
            from .graph_db_manager import GraphDBManager
            from .vector_store_manager import VectorStoreManager
            
            # Get configuration
            if self.config:
                graph_uri = self.config.database.neo4j_uri
                graph_username = self.config.database.neo4j_username
                graph_password = self.config.database.neo4j_password
                vector_mode = getattr(self.config, 'vector_mode', 'chroma')
                vector_path = self.config.database.vector_storage_path
            else:
                graph_uri = None
                graph_username = "neo4j"
                graph_password = "password"
                vector_mode = "chroma"
                vector_path = ".configo_vectors"
            
            # Initialize graph manager
            self.graph_manager = GraphDBManager(
                uri=graph_uri,
                username=graph_username,
                password=graph_password
            )
            
            # Initialize vector manager
            self.vector_manager = VectorStoreManager(
                storage_path=vector_path,
                mode=vector_mode
            )
            
            logger.info("Knowledge managers initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize knowledge managers: {e}")
            logger.info("Knowledge features will be limited")
    
    def _initialize_gemini_scraper(self) -> None:
        """Initialize the Gemini scraper."""
        try:
            from .gemini_scraper import GeminiScraper
            
            # Get Gemini API key from config
            gemini_api_key = None
            if self.config:
                gemini_api_key = getattr(self.config, 'gemini_api_key', None)
            
            self.gemini_scraper = GeminiScraper(api_key=gemini_api_key)
            logger.info("Gemini scraper initialized")
        except ImportError:
            logger.warning("Gemini scraper not available")
            self.gemini_scraper = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini scraper: {e}")
            self.gemini_scraper = None
    
    def add_tool_knowledge(self, tool_name: str, metadata: Dict[str, Any]) -> bool:
        """
        Add tool knowledge to the knowledge base.
        
        Args:
            tool_name: Name of the tool
            metadata: Tool metadata and information
            
        Returns:
            bool: Success status
        """
        try:
            # Add to graph database
            if self.graph_manager:
                self.graph_manager.add_tool_node(tool_name, metadata)
            
            # Add to vector database
            if self.vector_manager:
                content = f"Tool: {tool_name}\nDescription: {metadata.get('description', '')}\nCategory: {metadata.get('category', '')}"
                self.vector_manager.add_document(content, {
                    'type': 'tool',
                    'name': tool_name,
                    'metadata': metadata
                })
            
            logger.info(f"Added tool knowledge: {tool_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add tool knowledge: {e}")
            return False
    
    def add_relationship(self, source: str, target: str, relationship_type: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a relationship between tools or concepts.
        
        Args:
            source: Source node
            target: Target node
            relationship_type: Type of relationship
            metadata: Additional relationship metadata
            
        Returns:
            bool: Success status
        """
        try:
            if self.graph_manager:
                self.graph_manager.add_relationship(source, target, relationship_type, metadata)
                logger.info(f"Added relationship: {source} -> {target} ({relationship_type})")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return False
    
    def search_tools(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tools using semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        try:
            if self.vector_manager:
                results = self.vector_manager.search(query, limit)
                return results
            else:
                # Fallback to simple keyword search
                return self._fallback_search(query, limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_tool_relationships(self, tool_name: str) -> List[Dict[str, Any]]:
        """
        Get relationships for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List[Dict[str, Any]]: Tool relationships
        """
        try:
            if self.graph_manager:
                return self.graph_manager.get_tool_relationships(tool_name)
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to get tool relationships: {e}")
            return []
    
    def find_similar_tools(self, tool_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find tools similar to the given tool.
        
        Args:
            tool_name: Name of the tool
            limit: Maximum number of similar tools
            
        Returns:
            List[Dict[str, Any]]: Similar tools
        """
        try:
            if self.vector_manager:
                # Get tool description
                tool_info = self.get_tool_info(tool_name)
                if tool_info:
                    description = tool_info.get('description', tool_name)
                    results = self.vector_manager.search(description, limit + 1)
                    # Filter out the tool itself
                    return [r for r in results if r.get('name') != tool_name][:limit]
                else:
                    return []
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to find similar tools: {e}")
            return []
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Optional[Dict[str, Any]]: Tool information
        """
        try:
            if self.graph_manager:
                return self.graph_manager.get_tool_info(tool_name)
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get tool info: {e}")
            return None
    
    def query_graph(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the graph database.
        
        Args:
            query: Graph query
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            if self.graph_manager:
                return self.graph_manager.query(query)
            else:
                return []
        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            return []
    
    def visualize_plan(self, plan_name: str) -> bool:
        """
        Visualize an installation plan.
        
        Args:
            plan_name: Name of the plan to visualize
            
        Returns:
            bool: Success status
        """
        try:
            if self.graph_manager:
                return self.graph_manager.visualize_plan(plan_name)
            else:
                logger.warning("Graph manager not available for visualization")
                return False
        except Exception as e:
            logger.error(f"Failed to visualize plan: {e}")
            return False
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph database statistics."""
        try:
            if self.graph_manager:
                return self.graph_manager.get_stats()
            else:
                return {'nodes': 0, 'relationships': 0, 'status': 'disabled'}
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {'nodes': 0, 'relationships': 0, 'status': 'error'}
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        try:
            if self.vector_manager:
                return self.vector_manager.get_stats()
            else:
                return {'documents': 0, 'status': 'disabled'}
        except Exception as e:
            logger.error(f"Failed to get vector stats: {e}")
            return {'documents': 0, 'status': 'error'}
    
    def _fallback_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback search when vector manager is not available."""
        # Simple keyword-based search
        query_lower = query.lower()
        
        # Common tool mappings
        tool_mappings = {
            'git': {'name': 'git', 'description': 'Version control system', 'category': 'vcs'},
            'python': {'name': 'python', 'description': 'Programming language', 'category': 'language'},
            'node': {'name': 'node', 'description': 'JavaScript runtime', 'category': 'runtime'},
            'docker': {'name': 'docker', 'description': 'Container platform', 'category': 'container'},
            'vscode': {'name': 'vscode', 'description': 'Code editor', 'category': 'editor'},
            'npm': {'name': 'npm', 'description': 'Package manager for Node.js', 'category': 'package_manager'},
            'pip': {'name': 'pip', 'description': 'Package manager for Python', 'category': 'package_manager'},
            'java': {'name': 'java', 'description': 'Programming language', 'category': 'language'},
            'gcc': {'name': 'gcc', 'description': 'C compiler', 'category': 'compiler'},
            'make': {'name': 'make', 'description': 'Build automation tool', 'category': 'build'}
        }
        
        results = []
        for tool_name, tool_info in tool_mappings.items():
            if (query_lower in tool_name.lower() or 
                query_lower in tool_info['description'].lower() or
                query_lower in tool_info['category'].lower()):
                results.append({
                    'name': tool_name,
                    'description': tool_info['description'],
                    'category': tool_info['category'],
                    'score': 0.8  # Default score
                })
        
        return results[:limit]
    
    def add_installation_plan(self, plan_name: str, plan_data: Dict[str, Any]) -> bool:
        """
        Add an installation plan to the knowledge base.
        
        Args:
            plan_name: Name of the plan
            plan_data: Plan data
            
        Returns:
            bool: Success status
        """
        try:
            if self.graph_manager:
                self.graph_manager.add_plan_node(plan_name, plan_data)
            
            # Add plan description to vector store
            if self.vector_manager:
                description = f"Installation plan: {plan_name}\nEnvironment: {plan_data.get('environment', '')}\nTools: {', '.join(plan_data.get('tools', []))}"
                self.vector_manager.add_document(description, {
                    'type': 'plan',
                    'name': plan_name,
                    'data': plan_data
                })
            
            logger.info(f"Added installation plan: {plan_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add installation plan: {e}")
            return False
    
    def get_recommended_tools(self, environment_type: str) -> List[Dict[str, Any]]:
        """
        Get recommended tools for an environment type.
        
        Args:
            environment_type: Type of development environment
            
        Returns:
            List[Dict[str, Any]]: Recommended tools
        """
        try:
            if self.vector_manager:
                query = f"tools for {environment_type} development"
                results = self.vector_manager.search(query, 10)
                return results
            else:
                # Fallback recommendations
                return self._get_fallback_recommendations(environment_type)
        except Exception as e:
            logger.error(f"Failed to get recommended tools: {e}")
            return self._get_fallback_recommendations(environment_type)
    
    def _get_fallback_recommendations(self, environment_type: str) -> List[Dict[str, Any]]:
        """Get fallback tool recommendations."""
        recommendations = {
            'web_development': [
                {'name': 'node', 'description': 'JavaScript runtime', 'priority': 'high'},
                {'name': 'npm', 'description': 'Package manager', 'priority': 'high'},
                {'name': 'git', 'description': 'Version control', 'priority': 'high'},
                {'name': 'vscode', 'description': 'Code editor', 'priority': 'medium'}
            ],
            'python_development': [
                {'name': 'python', 'description': 'Programming language', 'priority': 'high'},
                {'name': 'pip', 'description': 'Package manager', 'priority': 'high'},
                {'name': 'git', 'description': 'Version control', 'priority': 'high'},
                {'name': 'vscode', 'description': 'Code editor', 'priority': 'medium'}
            ],
            'ai_development': [
                {'name': 'python', 'description': 'Programming language', 'priority': 'high'},
                {'name': 'pip', 'description': 'Package manager', 'priority': 'high'},
                {'name': 'docker', 'description': 'Container platform', 'priority': 'medium'},
                {'name': 'jupyter', 'description': 'Notebook environment', 'priority': 'medium'}
            ]
        }
        
        return recommendations.get(environment_type, [])
    
    def backup_knowledge(self, backup_path: str) -> bool:
        """
        Create a backup of the knowledge base.
        
        Args:
            backup_path: Path for backup
            
        Returns:
            bool: Success status
        """
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(exist_ok=True)
            
            # Backup graph data
            if self.graph_manager:
                self.graph_manager.backup(backup_dir / "graph")
            
            # Backup vector data
            if self.vector_manager:
                self.vector_manager.backup(backup_dir / "vector")
            
            logger.info(f"Knowledge base backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup knowledge base: {e}")
            return False
    
    def clear_knowledge(self) -> bool:
        """Clear all knowledge data."""
        try:
            if self.graph_manager:
                self.graph_manager.clear()
            
            if self.vector_manager:
                self.vector_manager.clear()
            
            logger.info("Knowledge base cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear knowledge base: {e}")
            return False
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Log an event to the knowledge base.
        
        Args:
            event_type: Type of event (install, error, search, etc.)
            data: Event data
            
        Returns:
            bool: Success status
        """
        try:
            # Log to vector store
            if self.vector_manager:
                content = f"{event_type}: {str(data)}"
                metadata = {
                    'type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    **data
                }
                self.vector_manager.add_document(content, metadata)
            
            # Log to graph if relevant
            if self.graph_manager and event_type in ['install', 'error', 'tool']:
                if event_type == 'install':
                    self.graph_manager.add_installation_result(
                        data.get('tool_name', 'unknown'),
                        data.get('success', False),
                        data.get('system_info', {}),
                        data.get('error_message')
                    )
                elif event_type == 'error':
                    self.graph_manager.log_error_fix(
                        data.get('error_message', ''),
                        data.get('fix_command', ''),
                        data.get('tool_name')
                    )
            
            return True
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            return False
    
    def get_similar_fixes(self, error_message: str) -> List[Dict[str, Any]]:
        """
        Get similar fixes for an error.
        
        Args:
            error_message: Error message
            
        Returns:
            List[Dict[str, Any]]: Similar fixes
        """
        try:
            # Search vector store
            if self.vector_manager:
                return self.vector_manager.search_similar_errors(error_message)
            
            return []
        except Exception as e:
            logger.error(f"Failed to get similar fixes: {e}")
            return []
    
    def recommend_stack(self, domain_profile: str) -> Dict[str, Any]:
        """
        Recommend tools for a domain profile.
        
        Args:
            domain_profile: Domain profile (e.g., 'full stack ai')
            
        Returns:
            Dict[str, Any]: Recommended stack
        """
        try:
            # Use Gemini scraper if available
            if self.gemini_scraper and self.gemini_scraper.is_connected():
                return self.gemini_scraper.search_tools_for_domain(domain_profile)
            
            # Fallback to graph query
            if self.graph_manager:
                tools = self.graph_manager.query_recommended_tools(domain_profile)
                return {
                    'domain': domain_profile,
                    'tools': tools,
                    'recommended_stack': [tool['name'] for tool in tools[:5]]
                }
            
            return {
                'domain': domain_profile,
                'tools': [],
                'recommended_stack': []
            }
        except Exception as e:
            logger.error(f"Failed to recommend stack: {e}")
            return {
                'domain': domain_profile,
                'tools': [],
                'recommended_stack': []
            }
    
    def expand_graph_from_gemini(self, domain: str) -> bool:
        """
        Expand knowledge graph using Gemini scraper.
        
        Args:
            domain: Domain to expand
            
        Returns:
            bool: Success status
        """
        try:
            if not self.gemini_scraper or not self.gemini_scraper.is_connected():
                return False
            
            # Get tools from Gemini
            tools_data = self.gemini_scraper.search_tools_for_domain(domain)
            
            if not self.graph_manager:
                return False
            
            # Add tools to graph
            for tool in tools_data.get('tools', []):
                self.graph_manager.add_tool(
                    tool['name'],
                    tool['category'],
                    tool['description']
                )
                
                # Add relationships
                for related_tool in tool.get('related_tools', []):
                    self.graph_manager.add_relationship(
                        tool['name'],
                        related_tool,
                        'RELATED_TO'
                    )
            
            # Add to vector store
            if self.vector_manager:
                content = f"Domain: {domain}\nTools: {[tool['name'] for tool in tools_data.get('tools', [])]}"
                metadata = {
                    'type': 'domain',
                    'domain': domain,
                    'timestamp': datetime.now().isoformat()
                }
                self.vector_manager.add_document(content, metadata)
            
            logger.info(f"Expanded graph for domain: {domain}")
            return True
        except Exception as e:
            logger.error(f"Failed to expand graph from Gemini: {e}")
            return False 