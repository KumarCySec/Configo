"""
CONFIGO Graph Database Manager
=============================

Handles Neo4j graph database operations for CONFIGO.
Manages tool relationships, installation plans, and knowledge graph queries.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GraphDBManager:
    """
    Neo4j graph database manager for CONFIGO.
    
    Handles tool relationships, installation plans, and knowledge graph
    operations for intelligent decision making.
    """
    
    def __init__(self, uri: Optional[str] = None, username: str = "neo4j", password: str = "password"):
        """Initialize the graph database manager."""
        self.uri = uri or "bolt://localhost:7687"
        self.username = username
        self.password = password
        self.driver = None
        self.connected = False
        
        self._initialize_connection()
        self._create_constraints()
        logger.info("CONFIGO Graph Database Manager initialized")
    
    def _initialize_connection(self) -> None:
        """Initialize Neo4j connection."""
        try:
            from neo4j import GraphDatabase
            
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            self.connected = True
            logger.info("Connected to Neo4j database")
        except ImportError:
            logger.warning("Neo4j driver not available - graph features disabled")
            self.connected = False
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}")
            self.connected = False
    
    def _create_constraints(self) -> None:
        """Create database constraints for data integrity."""
        if not self.connected:
            return
        
        try:
            with self.driver.session() as session:
                # Create unique constraints
                session.run("CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE")
                session.run("CREATE CONSTRAINT plan_name IF NOT EXISTS FOR (p:Plan) REQUIRE p.name IS UNIQUE")
                session.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
                
                logger.info("Database constraints created")
        except Exception as e:
            logger.warning(f"Failed to create constraints: {e}")
    
    def add_tool_node(self, tool_name: str, metadata: Dict[str, Any]) -> bool:
        """
        Add a tool node to the graph.
        
        Args:
            tool_name: Name of the tool
            metadata: Tool metadata
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (t:Tool {name: $name})
                SET t.description = $description,
                    t.category = $category,
                    t.version = $version,
                    t.updated_at = datetime()
                RETURN t
                """
                
                result = session.run(query, {
                    'name': tool_name,
                    'description': metadata.get('description', ''),
                    'category': metadata.get('category', 'unknown'),
                    'version': metadata.get('version', '')
                })
                
                result.single()
                logger.info(f"Added tool node: {tool_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add tool node: {e}")
            return False
    
    def add_plan_node(self, plan_name: str, plan_data: Dict[str, Any]) -> bool:
        """
        Add an installation plan node to the graph.
        
        Args:
            plan_name: Name of the plan
            plan_data: Plan data
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (p:Plan {name: $name})
                SET p.environment = $environment,
                    p.description = $description,
                    p.complexity = $complexity,
                    p.created_at = datetime(),
                    p.updated_at = datetime()
                RETURN p
                """
                
                result = session.run(query, {
                    'name': plan_name,
                    'environment': plan_data.get('environment', ''),
                    'description': plan_data.get('description', ''),
                    'complexity': plan_data.get('complexity', 'medium')
                })
                
                result.single()
                logger.info(f"Added plan node: {plan_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add plan node: {e}")
            return False
    
    def add_relationship(self, source: str, target: str, relationship_type: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a relationship between nodes.
        
        Args:
            source: Source node name
            target: Target node name
            relationship_type: Type of relationship
            metadata: Relationship metadata
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (a), (b)
                WHERE a.name = $source AND b.name = $target
                MERGE (a)-[r:RELATES_TO {type: $type}]->(b)
                SET r.metadata = $metadata,
                    r.created_at = datetime()
                RETURN r
                """
                
                result = session.run(query, {
                    'source': source,
                    'target': target,
                    'type': relationship_type,
                    'metadata': json.dumps(metadata) if metadata else None
                })
                
                result.single()
                logger.info(f"Added relationship: {source} -> {target} ({relationship_type})")
                return True
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return False
    
    def add_installation_result(self, tool_name: str, success: bool, 
                               system_info: Dict[str, Any], error_message: Optional[str] = None) -> bool:
        """
        Add an installation result to the graph.
        
        Args:
            tool_name: Name of the tool
            success: Whether installation was successful
            system_info: System information
            error_message: Error message if failed
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            return False
        
        try:
            with self.driver.session() as session:
                # Add system node
                system_id = f"{system_info.get('os', 'unknown')}_{system_info.get('arch', 'unknown')}"
                
                query = """
                MERGE (s:System {id: $system_id})
                SET s.os = $os,
                    s.arch = $arch,
                    s.python_version = $python_version,
                    s.updated_at = datetime()
                """
                
                session.run(query, {
                    'system_id': system_id,
                    'os': system_info.get('os', 'unknown'),
                    'arch': system_info.get('arch', 'unknown'),
                    'python_version': system_info.get('python_version', 'unknown')
                })
                
                # Add installation result
                query = """
                MATCH (t:Tool {name: $tool_name})
                MATCH (s:System {id: $system_id})
                MERGE (t)-[r:INSTALLED_ON]->(s)
                SET r.success = $success,
                    r.error_message = $error_message,
                    r.installed_at = datetime()
                RETURN r
                """
                
                result = session.run(query, {
                    'tool_name': tool_name,
                    'system_id': system_id,
                    'success': success,
                    'error_message': error_message
                })
                
                result.single()
                logger.info(f"Added installation result: {tool_name} (success: {success})")
                return True
        except Exception as e:
            logger.error(f"Failed to add installation result: {e}")
            return False
    
    def get_tool_relationships(self, tool_name: str) -> List[Dict[str, Any]]:
        """
        Get relationships for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List[Dict[str, Any]]: Tool relationships
        """
        if not self.connected:
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (t:Tool {name: $name})-[r:RELATES_TO]-(related)
                RETURN related.name as name, related.category as category, r.type as relationship_type
                """
                
                result = session.run(query, {'name': tool_name})
                relationships = []
                
                for record in result:
                    relationships.append({
                        'name': record['name'],
                        'category': record['category'],
                        'relationship_type': record['relationship_type']
                    })
                
                return relationships
        except Exception as e:
            logger.error(f"Failed to get tool relationships: {e}")
            return []
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Optional[Dict[str, Any]]: Tool information
        """
        if not self.connected:
            return None
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (t:Tool {name: $name})
                RETURN t.name as name, t.description as description, t.category as category, t.version as version
                """
                
                result = session.run(query, {'name': tool_name})
                record = result.single()
                
                if record:
                    return {
                        'name': record['name'],
                        'description': record['description'],
                        'category': record['category'],
                        'version': record['version']
                    }
                else:
                    return None
        except Exception as e:
            logger.error(f"Failed to get tool info: {e}")
            return None
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        if not self.connected:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def visualize_plan(self, plan_name: str) -> bool:
        """
        Visualize an installation plan.
        
        Args:
            plan_name: Name of the plan to visualize
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (p:Plan {name: $name})-[r:INCLUDES]->(t:Tool)
                RETURN p.name as plan_name, t.name as tool_name, t.category as category
                ORDER BY t.category, t.name
                """
                
                result = session.run(query, {'name': plan_name})
                tools = []
                
                for record in result:
                    tools.append({
                        'name': record['tool_name'],
                        'category': record['category']
                    })
                
                if tools:
                    logger.info(f"Visualized plan '{plan_name}' with {len(tools)} tools")
                    return True
                else:
                    logger.warning(f"Plan '{plan_name}' not found")
                    return False
        except Exception as e:
            logger.error(f"Failed to visualize plan: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph database statistics."""
        if not self.connected:
            return {'nodes': 0, 'relationships': 0, 'status': 'disconnected'}
        
        try:
            with self.driver.session() as session:
                # Count nodes
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = result.single()['node_count']
                
                # Count relationships
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = result.single()['rel_count']
                
                # Count tools
                result = session.run("MATCH (t:Tool) RETURN count(t) as tool_count")
                tool_count = result.single()['tool_count']
                
                # Count plans
                result = session.run("MATCH (p:Plan) RETURN count(p) as plan_count")
                plan_count = result.single()['plan_count']
                
                return {
                    'nodes': node_count,
                    'relationships': rel_count,
                    'tools': tool_count,
                    'plans': plan_count,
                    'status': 'connected'
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'nodes': 0, 'relationships': 0, 'status': 'error'}
    
    def backup(self, backup_path: Path) -> bool:
        """
        Create a backup of the graph database.
        
        Args:
            backup_path: Path for backup
            
        Returns:
            bool: Success status
        """
        if not self.connected:
            return False
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            with self.driver.session() as session:
                # Export tools
                result = session.run("MATCH (t:Tool) RETURN t")
                tools = [dict(record['t']) for record in result]
                
                with open(backup_path / "tools.json", 'w') as f:
                    json.dump(tools, f, indent=2)
                
                # Export plans
                result = session.run("MATCH (p:Plan) RETURN p")
                plans = [dict(record['p']) for record in result]
                
                with open(backup_path / "plans.json", 'w') as f:
                    json.dump(plans, f, indent=2)
                
                # Export relationships
                result = session.run("MATCH (a)-[r]->(b) RETURN a.name as source, b.name as target, r")
                relationships = []
                for record in result:
                    rel_data = dict(record['r'])
                    rel_data['source'] = record['source']
                    rel_data['target'] = record['target']
                    relationships.append(rel_data)
                
                with open(backup_path / "relationships.json", 'w') as f:
                    json.dump(relationships, f, indent=2)
                
                logger.info(f"Graph database backed up to: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to backup graph database: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all data from the graph database."""
        if not self.connected:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Graph database cleared")
                return True
        except Exception as e:
            logger.error(f"Failed to clear graph database: {e}")
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Graph database connection closed") 