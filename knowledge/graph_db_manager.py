"""
CONFIGO Graph Database Manager
=============================

Neo4j-based graph database manager for modeling tool relationships,
install events, user personas, and dependency graphs.

Features:
- 🧠 Tool dependency graph modeling
- 📊 Install event tracking with metadata
- 👤 User persona and preference modeling
- 🔄 Success/failure pattern analysis
- 🎯 Personalized install plan generation
- 📈 Performance analytics and insights
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import Neo4j, fallback to local graph simulation
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
    logger.info("Neo4j available - using real graph database")
except ImportError:
    NEO4J_AVAILABLE = False
    logger.info("Neo4j not available - using local graph simulation")


@dataclass
class ToolNode:
    """Represents a tool node in the graph."""
    name: str
    category: str
    description: str
    install_command: str
    check_command: str
    created_at: datetime
    last_installed: Optional[datetime] = None
    install_success_rate: float = 0.0
    total_installs: int = 0
    total_failures: int = 0


@dataclass
class InstallEvent:
    """Represents an installation event."""
    tool_name: str
    command: str
    success: bool
    timestamp: datetime
    os_type: str
    architecture: str
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    retry_count: int = 0


@dataclass
class UserProfile:
    """Represents a user profile in the graph."""
    user_id: str
    name: str
    persona: str
    preferences: Dict[str, Any]
    created_at: datetime
    last_active: Optional[datetime] = None
    total_installs: int = 0
    success_rate: float = 0.0


class LocalGraphSimulator:
    """
    Local graph simulator for when Neo4j is not available.
    
    Simulates graph operations using JSON storage and in-memory relationships.
    """
    
    def __init__(self, storage_path: str = ".configo_graph"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # In-memory graph data
        self.tools: Dict[str, ToolNode] = {}
        self.install_events: List[InstallEvent] = []
        self.user_profiles: Dict[str, UserProfile] = {}
        self.relationships: Dict[str, List[str]] = {}  # tool -> [related_tools]
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load graph data from JSON files."""
        try:
            # Load tools
            tools_file = self.storage_path / "tools.json"
            if tools_file.exists():
                with open(tools_file, 'r') as f:
                    data = json.load(f)
                    for tool_data in data.values():
                        tool_data['created_at'] = datetime.fromisoformat(tool_data['created_at'])
                        if tool_data.get('last_installed'):
                            tool_data['last_installed'] = datetime.fromisoformat(tool_data['last_installed'])
                        self.tools[tool_data['name']] = ToolNode(**tool_data)
            
            # Load install events
            events_file = self.storage_path / "install_events.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    data = json.load(f)
                    for event_data in data:
                        event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'])
                        self.install_events.append(InstallEvent(**event_data))
            
            # Load user profiles
            profiles_file = self.storage_path / "user_profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    for profile_data in data.values():
                        profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
                        if profile_data.get('last_active'):
                            profile_data['last_active'] = datetime.fromisoformat(profile_data['last_active'])
                        self.user_profiles[profile_data['user_id']] = UserProfile(**profile_data)
            
            # Load relationships
            relationships_file = self.storage_path / "relationships.json"
            if relationships_file.exists():
                with open(relationships_file, 'r') as f:
                    self.relationships = json.load(f)
                    
        except Exception as e:
            logger.warning(f"Failed to load graph data: {e}")
    
    def _save_data(self) -> None:
        """Save graph data to JSON files."""
        try:
            # Save tools
            tools_data = {}
            for tool in self.tools.values():
                tools_data[tool.name] = asdict(tool)
                tools_data[tool.name]['created_at'] = tool.created_at.isoformat()
                if tool.last_installed:
                    tools_data[tool.name]['last_installed'] = tool.last_installed.isoformat()
            
            with open(self.storage_path / "tools.json", 'w') as f:
                json.dump(tools_data, f, indent=2)
            
            # Save install events
            events_data = []
            for event in self.install_events:
                event_dict = asdict(event)
                event_dict['timestamp'] = event.timestamp.isoformat()
                events_data.append(event_dict)
            
            with open(self.storage_path / "install_events.json", 'w') as f:
                json.dump(events_data, f, indent=2)
            
            # Save user profiles
            profiles_data = {}
            for profile in self.user_profiles.values():
                profiles_data[profile.user_id] = asdict(profile)
                profiles_data[profile.user_id]['created_at'] = profile.created_at.isoformat()
                if profile.last_active:
                    profiles_data[profile.user_id]['last_active'] = profile.last_active.isoformat()
            
            with open(self.storage_path / "user_profiles.json", 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            # Save relationships
            with open(self.storage_path / "relationships.json", 'w') as f:
                json.dump(self.relationships, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save graph data: {e}")


class GraphDBManager:
    """
    Graph database manager for CONFIGO knowledge layer.
    
    Handles tool relationships, install events, user profiles, and dependency graphs.
    Falls back to local simulation when Neo4j is not available.
    """
    
    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, 
                 password: Optional[str] = None, storage_path: str = ".configo_graph"):
        """
        Initialize the graph database manager.
        
        Args:
            uri: Neo4j database URI (e.g., "bolt://localhost:7687")
            username: Neo4j username
            password: Neo4j password
            storage_path: Local storage path for fallback mode
        """
        self.uri = uri or os.getenv('NEO4J_URI')
        self.username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        if NEO4J_AVAILABLE and self.uri:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self._initialize_schema()
            logger.info("Connected to Neo4j database")
        else:
            self.driver = None
            self.simulator = LocalGraphSimulator(storage_path)
            logger.info("Using local graph simulation")
    
    def _initialize_schema(self) -> None:
        """Initialize Neo4j schema with constraints and indexes."""
        if not self.driver:
            return
            
        with self.driver.session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            
            # Create indexes
            session.run("CREATE INDEX tool_category IF NOT EXISTS FOR (t:Tool) ON (t.category)")
            session.run("CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:InstallEvent) ON (e.timestamp)")
            session.run("CREATE INDEX user_persona IF NOT EXISTS FOR (u:User) ON (u.persona)")
    
    def add_tool(self, name: str, category: str, description: str, 
                 install_command: str, check_command: str) -> bool:
        """
        Add a tool to the graph database.
        
        Args:
            name: Tool name
            category: Tool category (e.g., "editor", "language", "framework")
            description: Tool description
            install_command: Installation command
            check_command: Command to check if tool is installed
            
        Returns:
            bool: True if successful
        """
        if self.driver:
            return self._add_tool_neo4j(name, category, description, install_command, check_command)
        else:
            return self._add_tool_local(name, category, description, install_command, check_command)
    
    def _add_tool_neo4j(self, name: str, category: str, description: str,
                        install_command: str, check_command: str) -> bool:
        """Add tool to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (t:Tool {name: $name})
                    SET t.category = $category,
                        t.description = $description,
                        t.install_command = $install_command,
                        t.check_command = $check_command,
                        t.created_at = datetime(),
                        t.install_success_rate = 0.0,
                        t.total_installs = 0,
                        t.total_failures = 0
                """, name=name, category=category, description=description,
                     install_command=install_command, check_command=check_command)
            return True
        except Exception as e:
            logger.error(f"Failed to add tool to Neo4j: {e}")
            return False
    
    def _add_tool_local(self, name: str, category: str, description: str,
                        install_command: str, check_command: str) -> bool:
        """Add tool to local simulator."""
        try:
            if name not in self.simulator.tools:
                tool = ToolNode(
                    name=name,
                    category=category,
                    description=description,
                    install_command=install_command,
                    check_command=check_command,
                    created_at=datetime.now()
                )
                self.simulator.tools[name] = tool
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add tool locally: {e}")
            return False
    
    def log_install_event(self, tool_name: str, command: str, success: bool,
                         os_type: str, architecture: str, error_message: Optional[str] = None,
                         user_id: Optional[str] = None, session_id: Optional[str] = None,
                         retry_count: int = 0) -> bool:
        """
        Log an installation event.
        
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
        if self.driver:
            return self._log_install_event_neo4j(tool_name, command, success, os_type,
                                               architecture, error_message, user_id, session_id, retry_count)
        else:
            return self._log_install_event_local(tool_name, command, success, os_type,
                                              architecture, error_message, user_id, session_id, retry_count)
    
    def _log_install_event_neo4j(self, tool_name: str, command: str, success: bool,
                                os_type: str, architecture: str, error_message: Optional[str],
                                user_id: Optional[str], session_id: Optional[str], retry_count: int) -> bool:
        """Log install event to Neo4j."""
        try:
            with self.driver.session() as session:
                # Create install event
                session.run("""
                    CREATE (e:InstallEvent {
                        tool_name: $tool_name,
                        command: $command,
                        success: $success,
                        timestamp: datetime(),
                        os_type: $os_type,
                        architecture: $architecture,
                        error_message: $error_message,
                        user_id: $user_id,
                        session_id: $session_id,
                        retry_count: $retry_count
                    })
                """, tool_name=tool_name, command=command, success=success,
                     os_type=os_type, architecture=architecture, error_message=error_message,
                     user_id=user_id, session_id=session_id, retry_count=retry_count)
                
                # Update tool statistics
                session.run("""
                    MATCH (t:Tool {name: $tool_name})
                    SET t.total_installs = t.total_installs + 1,
                        t.last_installed = datetime()
                """, tool_name=tool_name)
                
                if not success:
                    session.run("""
                        MATCH (t:Tool {name: $tool_name})
                        SET t.total_failures = t.total_failures + 1
                    """, tool_name=tool_name)
                
                # Update success rate
                session.run("""
                    MATCH (t:Tool {name: $tool_name})
                    SET t.install_success_rate = 
                        CASE 
                            WHEN t.total_installs > 0 
                            THEN (t.total_installs - t.total_failures) * 1.0 / t.total_installs
                            ELSE 0.0
                        END
                """, tool_name=tool_name)
                
                # Link to user if provided
                if user_id:
                    session.run("""
                        MATCH (e:InstallEvent {tool_name: $tool_name, timestamp: datetime()})
                        MATCH (u:User {user_id: $user_id})
                        CREATE (u)-[:INSTALLED]->(e)
                    """, tool_name=tool_name, user_id=user_id)
                
            return True
        except Exception as e:
            logger.error(f"Failed to log install event to Neo4j: {e}")
            return False
    
    def _log_install_event_local(self, tool_name: str, command: str, success: bool,
                               os_type: str, architecture: str, error_message: Optional[str],
                               user_id: Optional[str], session_id: Optional[str], retry_count: int) -> bool:
        """Log install event to local simulator."""
        try:
            event = InstallEvent(
                tool_name=tool_name,
                command=command,
                success=success,
                timestamp=datetime.now(),
                os_type=os_type,
                architecture=architecture,
                error_message=error_message,
                user_id=user_id,
                session_id=session_id,
                retry_count=retry_count
            )
            self.simulator.install_events.append(event)
            
            # Update tool statistics
            if tool_name in self.simulator.tools:
                tool = self.simulator.tools[tool_name]
                tool.total_installs += 1
                tool.last_installed = datetime.now()
                if not success:
                    tool.total_failures += 1
                tool.install_success_rate = (tool.total_installs - tool.total_failures) / tool.total_installs
            
            self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to log install event locally: {e}")
            return False
    
    def get_related_tools(self, tool_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get tools related to the specified tool.
        
        Args:
            tool_name: Name of the tool
            limit: Maximum number of related tools to return
            
        Returns:
            List[Dict[str, Any]]: List of related tools with metadata
        """
        if self.driver:
            return self._get_related_tools_neo4j(tool_name, limit)
        else:
            return self._get_related_tools_local(tool_name, limit)
    
    def _get_related_tools_neo4j(self, tool_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get related tools from Neo4j."""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (t:Tool {name: $tool_name})-[:DEPENDS_ON|USED_WITH|SIMILAR_TO]-(related:Tool)
                    RETURN related.name as name, related.category as category, 
                           related.description as description, related.install_success_rate as success_rate
                    ORDER BY related.install_success_rate DESC
                    LIMIT $limit
                """, tool_name=tool_name, limit=limit)
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to get related tools from Neo4j: {e}")
            return []
    
    def _get_related_tools_local(self, tool_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get related tools from local simulator."""
        try:
            related_tools = self.simulator.relationships.get(tool_name, [])
            result = []
            
            for related_name in related_tools[:limit]:
                if related_name in self.simulator.tools:
                    tool = self.simulator.tools[related_name]
                    result.append({
                        'name': tool.name,
                        'category': tool.category,
                        'description': tool.description,
                        'success_rate': tool.install_success_rate
                    })
            
            return result
        except Exception as e:
            logger.error(f"Failed to get related tools locally: {e}")
            return []
    
    def get_recommended_plan(self, user_profile: Dict[str, Any], 
                           target_environment: str) -> List[Dict[str, Any]]:
        """
        Get recommended installation plan based on user profile and target environment.
        
        Args:
            user_profile: User profile with preferences and history
            target_environment: Target environment (e.g., "ai-stack", "web-dev")
            
        Returns:
            List[Dict[str, Any]]: Recommended tools with installation order
        """
        if self.driver:
            return self._get_recommended_plan_neo4j(user_profile, target_environment)
        else:
            return self._get_recommended_plan_local(user_profile, target_environment)
    
    def _get_recommended_plan_neo4j(self, user_profile: Dict[str, Any], 
                                   target_environment: str) -> List[Dict[str, Any]]:
        """Get recommended plan from Neo4j."""
        try:
            persona = user_profile.get('persona', 'developer')
            
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {persona: $persona})-[:INSTALLED]->(e:InstallEvent)-[:FOR_TOOL]->(t:Tool)
                    WHERE e.success = true AND t.category IN ['language', 'framework', 'tool']
                    WITH t, count(e) as install_count, avg(t.install_success_rate) as avg_success
                    ORDER BY install_count DESC, avg_success DESC
                    RETURN t.name as name, t.category as category, t.description as description,
                           t.install_command as install_command, install_count, avg_success
                    LIMIT 10
                """, persona=persona)
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to get recommended plan from Neo4j: {e}")
            return []
    
    def _get_recommended_plan_local(self, user_profile: Dict[str, Any], 
                                  target_environment: str) -> List[Dict[str, Any]]:
        """Get recommended plan from local simulator."""
        try:
            # Simple recommendation based on success rates and categories
            recommendations = []
            
            for tool in self.simulator.tools.values():
                if tool.install_success_rate > 0.7 and tool.total_installs > 0:
                    recommendations.append({
                        'name': tool.name,
                        'category': tool.category,
                        'description': tool.description,
                        'install_command': tool.install_command,
                        'install_count': tool.total_installs,
                        'avg_success': tool.install_success_rate
                    })
            
            # Sort by success rate and install count
            recommendations.sort(key=lambda x: (x['avg_success'], x['install_count']), reverse=True)
            return recommendations[:10]
        except Exception as e:
            logger.error(f"Failed to get recommended plan locally: {e}")
            return []
    
    def add_relationship(self, tool1: str, tool2: str, relationship_type: str = "USED_WITH") -> bool:
        """
        Add a relationship between two tools.
        
        Args:
            tool1: First tool name
            tool2: Second tool name
            relationship_type: Type of relationship (DEPENDS_ON, USED_WITH, SIMILAR_TO)
            
        Returns:
            bool: True if successful
        """
        if self.driver:
            return self._add_relationship_neo4j(tool1, tool2, relationship_type)
        else:
            return self._add_relationship_local(tool1, tool2, relationship_type)
    
    def _add_relationship_neo4j(self, tool1: str, tool2: str, relationship_type: str) -> bool:
        """Add relationship to Neo4j."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (t1:Tool {name: $tool1})
                    MATCH (t2:Tool {name: $tool2})
                    MERGE (t1)-[r:$relationship_type]->(t2)
                """, tool1=tool1, tool2=tool2, relationship_type=relationship_type)
            return True
        except Exception as e:
            logger.error(f"Failed to add relationship to Neo4j: {e}")
            return False
    
    def _add_relationship_local(self, tool1: str, tool2: str, relationship_type: str) -> bool:
        """Add relationship to local simulator."""
        try:
            if tool1 not in self.simulator.relationships:
                self.simulator.relationships[tool1] = []
            if tool2 not in self.simulator.relationships:
                self.simulator.relationships[tool2] = []
            
            if tool2 not in self.simulator.relationships[tool1]:
                self.simulator.relationships[tool1].append(tool2)
            if tool1 not in self.simulator.relationships[tool2]:
                self.simulator.relationships[tool2].append(tool1)
            
            self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add relationship locally: {e}")
            return False
    
    def get_install_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get installation statistics for the specified time period.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict[str, Any]: Statistics including success rates, popular tools, etc.
        """
        if self.driver:
            return self._get_install_statistics_neo4j(days)
        else:
            return self._get_install_statistics_local(days)
    
    def _get_install_statistics_neo4j(self, days: int) -> Dict[str, Any]:
        """Get statistics from Neo4j."""
        try:
            with self.driver.session() as session:
                # Get overall statistics
                result = session.run("""
                    MATCH (e:InstallEvent)
                    WHERE e.timestamp > datetime() - duration({days: $days})
                    RETURN count(e) as total_installs,
                           count(CASE WHEN e.success = true THEN 1 END) as successful_installs,
                           count(CASE WHEN e.success = false THEN 1 END) as failed_installs
                """, days=days)
                
                stats = result.single()
                
                # Get popular tools
                result = session.run("""
                    MATCH (e:InstallEvent)
                    WHERE e.timestamp > datetime() - duration({days: $days})
                    WITH e.tool_name as tool, count(e) as install_count
                    ORDER BY install_count DESC
                    RETURN tool, install_count
                    LIMIT 10
                """, days=days)
                
                popular_tools = [dict(record) for record in result]
                
                return {
                    'total_installs': stats['total_installs'],
                    'successful_installs': stats['successful_installs'],
                    'failed_installs': stats['failed_installs'],
                    'success_rate': stats['successful_installs'] / stats['total_installs'] if stats['total_installs'] > 0 else 0,
                    'popular_tools': popular_tools,
                    'period_days': days
                }
        except Exception as e:
            logger.error(f"Failed to get statistics from Neo4j: {e}")
            return {}
    
    def _get_install_statistics_local(self, days: int) -> Dict[str, Any]:
        """Get statistics from local simulator."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_events = [e for e in self.simulator.install_events if e.timestamp > cutoff_date]
            
            total_installs = len(recent_events)
            successful_installs = len([e for e in recent_events if e.success])
            failed_installs = total_installs - successful_installs
            
            # Get popular tools
            tool_counts = {}
            for event in recent_events:
                tool_counts[event.tool_name] = tool_counts.get(event.tool_name, 0) + 1
            
            popular_tools = [
                {'tool': tool, 'install_count': count}
                for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            return {
                'total_installs': total_installs,
                'successful_installs': successful_installs,
                'failed_installs': failed_installs,
                'success_rate': successful_installs / total_installs if total_installs > 0 else 0,
                'popular_tools': popular_tools,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Failed to get statistics locally: {e}")
            return {}
    
    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close() 