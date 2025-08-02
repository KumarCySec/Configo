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


@dataclass
class Library:
    """Represents a library dependency."""
    name: str
    version: str
    language: str
    description: str
    created_at: datetime = None
    last_updated: Optional[datetime] = None
    download_count: int = 0
    compatibility: List[str] = None
    
    def __post_init__(self):
        if self.compatibility is None:
            self.compatibility = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class OS:
    """Represents an operating system."""
    name: str
    version: str
    architecture: str
    family: str  # linux, windows, macos
    created_at: datetime = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Error:
    """Represents an installation or runtime error."""
    error_id: str
    message: str
    solution: str
    severity: str  # low, medium, high, critical
    tool_name: str
    os_type: str
    created_at: datetime = None
    frequency: int = 1
    last_occurred: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Persona:
    """Represents a user persona type."""
    persona_id: str
    name: str
    description: str
    preferences: Dict[str, Any]
    created_at: datetime = None
    total_users: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Category:
    """Represents a tool category."""
    name: str
    description: str
    parent_category: Optional[str] = None
    created_at: datetime = None
    tool_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Feature:
    """Represents a tool feature."""
    name: str
    description: str
    tool_name: str
    created_at: datetime = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Command:
    """Represents a CLI command."""
    command_id: str
    command: str
    description: str
    tool_name: str
    os_type: str
    created_at: datetime = None
    success_rate: float = 0.0
    usage_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


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
        self.libraries: Dict[str, Library] = {}
        self.errors: Dict[str, Error] = {}
        self.personas: Dict[str, Persona] = {}
        self.categories: Dict[str, Category] = {}
        self.features: Dict[str, Feature] = {}
        self.commands: Dict[str, Command] = {}
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
                    tools_data = json.load(f)
                    for tool_data in tools_data:
                        tool = ToolNode(**tool_data)
                        # Convert string timestamps back to datetime
                        for field in ['created_at', 'last_installed']:
                            if tool_data.get(field):
                                setattr(tool, field, datetime.fromisoformat(tool_data[field]))
                        self.tools[tool.name] = tool
            
            # Load libraries
            libraries_file = self.storage_path / "libraries.json"
            if libraries_file.exists():
                with open(libraries_file, 'r') as f:
                    libraries_data = json.load(f)
                    for lib_data in libraries_data:
                        library = Library(**lib_data)
                        for field in ['created_at', 'last_updated']:
                            if lib_data.get(field):
                                setattr(library, field, datetime.fromisoformat(lib_data[field]))
                        self.libraries[library.name] = library
            
            # Load errors
            errors_file = self.storage_path / "errors.json"
            if errors_file.exists():
                with open(errors_file, 'r') as f:
                    errors_data = json.load(f)
                    for error_data in errors_data:
                        error = Error(**error_data)
                        for field in ['created_at', 'last_occurred']:
                            if error_data.get(field):
                                setattr(error, field, datetime.fromisoformat(error_data[field]))
                        self.errors[error.error_id] = error
            
            # Load personas
            personas_file = self.storage_path / "personas.json"
            if personas_file.exists():
                with open(personas_file, 'r') as f:
                    personas_data = json.load(f)
                    for persona_data in personas_data:
                        persona = Persona(**persona_data)
                        if persona_data.get('created_at'):
                            persona.created_at = datetime.fromisoformat(persona_data['created_at'])
                        self.personas[persona.persona_id] = persona
            
            # Load categories
            categories_file = self.storage_path / "categories.json"
            if categories_file.exists():
                with open(categories_file, 'r') as f:
                    categories_data = json.load(f)
                    for category_data in categories_data:
                        category = Category(**category_data)
                        if category_data.get('created_at'):
                            category.created_at = datetime.fromisoformat(category_data['created_at'])
                        self.categories[category.name] = category
            
            # Load features
            features_file = self.storage_path / "features.json"
            if features_file.exists():
                with open(features_file, 'r') as f:
                    features_data = json.load(f)
                    for feature_data in features_data:
                        feature = Feature(**feature_data)
                        if feature_data.get('created_at'):
                            feature.created_at = datetime.fromisoformat(feature_data['created_at'])
                        self.features[feature.name] = feature
            
            # Load commands
            commands_file = self.storage_path / "commands.json"
            if commands_file.exists():
                with open(commands_file, 'r') as f:
                    commands_data = json.load(f)
                    for command_data in commands_data:
                        command = Command(**command_data)
                        if command_data.get('created_at'):
                            command.created_at = datetime.fromisoformat(command_data['created_at'])
                        self.commands[command.command_id] = command
            
            # Load relationships
            relationships_file = self.storage_path / "relationships.json"
            if relationships_file.exists():
                with open(relationships_file, 'r') as f:
                    self.relationships = json.load(f)
            
            logger.info(f"Loaded {len(self.tools)} tools, {len(self.libraries)} libraries, {len(self.errors)} errors")
            
        except Exception as e:
            logger.error(f"Failed to load graph data: {e}")
    
    def _save_data(self) -> None:
        """Save graph data to JSON files."""
        try:
            # Save tools
            tools_data = []
            for tool in self.tools.values():
                tool_dict = asdict(tool)
                for field in ['created_at', 'last_installed']:
                    if tool_dict.get(field):
                        tool_dict[field] = tool_dict[field].isoformat()
                tools_data.append(tool_dict)
            
            with open(self.storage_path / "tools.json", 'w') as f:
                json.dump(tools_data, f, indent=2)
            
            # Save libraries
            libraries_data = []
            for library in self.libraries.values():
                lib_dict = asdict(library)
                for field in ['created_at', 'last_updated']:
                    if lib_dict.get(field):
                        lib_dict[field] = lib_dict[field].isoformat()
                libraries_data.append(lib_dict)
            
            with open(self.storage_path / "libraries.json", 'w') as f:
                json.dump(libraries_data, f, indent=2)
            
            # Save errors
            errors_data = []
            for error in self.errors.values():
                error_dict = asdict(error)
                for field in ['created_at', 'last_occurred']:
                    if error_dict.get(field):
                        error_dict[field] = error_dict[field].isoformat()
                errors_data.append(error_dict)
            
            with open(self.storage_path / "errors.json", 'w') as f:
                json.dump(errors_data, f, indent=2)
            
            # Save personas
            personas_data = []
            for persona in self.personas.values():
                persona_dict = asdict(persona)
                if persona_dict.get('created_at'):
                    persona_dict['created_at'] = persona_dict['created_at'].isoformat()
                personas_data.append(persona_dict)
            
            with open(self.storage_path / "personas.json", 'w') as f:
                json.dump(personas_data, f, indent=2)
            
            # Save categories
            categories_data = []
            for category in self.categories.values():
                category_dict = asdict(category)
                if category_dict.get('created_at'):
                    category_dict['created_at'] = category_dict['created_at'].isoformat()
                categories_data.append(category_dict)
            
            with open(self.storage_path / "categories.json", 'w') as f:
                json.dump(categories_data, f, indent=2)
            
            # Save features
            features_data = []
            for feature in self.features.values():
                feature_dict = asdict(feature)
                if feature_dict.get('created_at'):
                    feature_dict['created_at'] = feature_dict['created_at'].isoformat()
                features_data.append(feature_dict)
            
            with open(self.storage_path / "features.json", 'w') as f:
                json.dump(features_data, f, indent=2)
            
            # Save commands
            commands_data = []
            for command in self.commands.values():
                command_dict = asdict(command)
                if command_dict.get('created_at'):
                    command_dict['created_at'] = command_dict['created_at'].isoformat()
                commands_data.append(command_dict)
            
            with open(self.storage_path / "commands.json", 'w') as f:
                json.dump(commands_data, f, indent=2)
            
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
            # Create constraints for all node types
            session.run("CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT library_name IF NOT EXISTS FOR (l:Library) REQUIRE l.name IS UNIQUE")
            session.run("CREATE CONSTRAINT os_name IF NOT EXISTS FOR (o:OS) REQUIRE o.name IS UNIQUE")
            session.run("CREATE CONSTRAINT error_id IF NOT EXISTS FOR (e:Error) REQUIRE e.error_id IS UNIQUE")
            session.run("CREATE CONSTRAINT persona_id IF NOT EXISTS FOR (p:Persona) REQUIRE p.persona_id IS UNIQUE")
            session.run("CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE")
            session.run("CREATE CONSTRAINT feature_name IF NOT EXISTS FOR (f:Feature) REQUIRE f.name IS UNIQUE")
            session.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            session.run("CREATE CONSTRAINT command_id IF NOT EXISTS FOR (cmd:Command) REQUIRE cmd.command_id IS UNIQUE")
            
            # Create indexes for better query performance
            session.run("CREATE INDEX tool_category IF NOT EXISTS FOR (t:Tool) ON (t.category)")
            session.run("CREATE INDEX tool_install_success_rate IF NOT EXISTS FOR (t:Tool) ON (t.install_success_rate)")
            session.run("CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:InstallEvent) ON (e.timestamp)")
            session.run("CREATE INDEX user_persona IF NOT EXISTS FOR (u:User) ON (u.persona)")
            session.run("CREATE INDEX error_severity IF NOT EXISTS FOR (e:Error) ON (e.severity)")
            session.run("CREATE INDEX library_version IF NOT EXISTS FOR (l:Library) ON (l.version)")
            
            # Create full-text search indexes
            session.run("CREATE FULLTEXT INDEX tool_description IF NOT EXISTS FOR (t:Tool) ON EACH [t.description, t.name]")
            session.run("CREATE FULLTEXT INDEX error_message IF NOT EXISTS FOR (e:Error) ON EACH [e.message, e.solution]")
    
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

    def add_library(self, name: str, version: str, language: str, description: str, 
                   compatibility: List[str] = None) -> bool:
        """Add a library to the graph database."""
        if self.driver:
            return self._add_library_neo4j(name, version, language, description, compatibility)
        else:
            return self._add_library_local(name, version, language, description, compatibility)

    def add_error(self, error_id: str, message: str, solution: str, severity: str,
                 tool_name: str, os_type: str) -> bool:
        """Add an error to the graph database."""
        if self.driver:
            return self._add_error_neo4j(error_id, message, solution, severity, tool_name, os_type)
        else:
            return self._add_error_local(error_id, message, solution, severity, tool_name, os_type)

    def add_persona(self, persona_id: str, name: str, description: str, 
                   preferences: Dict[str, Any]) -> bool:
        """Add a persona to the graph database."""
        if self.driver:
            return self._add_persona_neo4j(persona_id, name, description, preferences)
        else:
            return self._add_persona_local(persona_id, name, description, preferences)

    def add_category(self, name: str, description: str, parent_category: Optional[str] = None) -> bool:
        """Add a category to the graph database."""
        if self.driver:
            return self._add_category_neo4j(name, description, parent_category)
        else:
            return self._add_category_local(name, description, parent_category)

    def add_feature(self, name: str, description: str, tool_name: str) -> bool:
        """Add a feature to the graph database."""
        if self.driver:
            return self._add_feature_neo4j(name, description, tool_name)
        else:
            return self._add_feature_local(name, description, tool_name)

    def add_command(self, command_id: str, command: str, description: str,
                   tool_name: str, os_type: str) -> bool:
        """Add a command to the graph database."""
        if self.driver:
            return self._add_command_neo4j(command_id, command, description, tool_name, os_type)
        else:
            return self._add_command_local(command_id, command, description, tool_name, os_type)
    
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

    def _add_library_neo4j(self, name: str, version: str, language: str, description: str,
                           compatibility: List[str] = None) -> bool:
        """Add library to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (l:Library {name: $name})
                    SET l.version = $version,
                        l.language = $language,
                        l.description = $description,
                        l.compatibility = $compatibility,
                        l.created_at = datetime(),
                        l.download_count = 0
                """, name=name, version=version, language=language, 
                     description=description, compatibility=compatibility or [])
            return True
        except Exception as e:
            logger.error(f"Failed to add library to Neo4j: {e}")
            return False

    def _add_library_local(self, name: str, version: str, language: str, description: str,
                           compatibility: List[str] = None) -> bool:
        """Add library to local simulator."""
        try:
            if name not in self.simulator.libraries:
                library = Library(
                    name=name,
                    version=version,
                    language=language,
                    description=description,
                    created_at=datetime.now(),
                    compatibility=compatibility or []
                )
                self.simulator.libraries[name] = library
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add library locally: {e}")
            return False

    def _add_error_neo4j(self, error_id: str, message: str, solution: str, severity: str,
                         tool_name: str, os_type: str) -> bool:
        """Add error to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (e:Error {error_id: $error_id})
                    SET e.message = $message,
                        e.solution = $solution,
                        e.severity = $severity,
                        e.tool_name = $tool_name,
                        e.os_type = $os_type,
                        e.created_at = datetime(),
                        e.frequency = 1
                """, error_id=error_id, message=message, solution=solution,
                     severity=severity, tool_name=tool_name, os_type=os_type)
            return True
        except Exception as e:
            logger.error(f"Failed to add error to Neo4j: {e}")
            return False

    def _add_error_local(self, error_id: str, message: str, solution: str, severity: str,
                         tool_name: str, os_type: str) -> bool:
        """Add error to local simulator."""
        try:
            if error_id not in self.simulator.errors:
                error = Error(
                    error_id=error_id,
                    message=message,
                    solution=solution,
                    severity=severity,
                    tool_name=tool_name,
                    os_type=os_type,
                    created_at=datetime.now()
                )
                self.simulator.errors[error_id] = error
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add error locally: {e}")
            return False

    def _add_persona_neo4j(self, persona_id: str, name: str, description: str,
                           preferences: Dict[str, Any]) -> bool:
        """Add persona to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (p:Persona {persona_id: $persona_id})
                    SET p.name = $name,
                        p.description = $description,
                        p.preferences = $preferences,
                        p.created_at = datetime(),
                        p.total_users = 0
                """, persona_id=persona_id, name=name, description=description,
                     preferences=preferences)
            return True
        except Exception as e:
            logger.error(f"Failed to add persona to Neo4j: {e}")
            return False

    def _add_persona_local(self, persona_id: str, name: str, description: str,
                           preferences: Dict[str, Any]) -> bool:
        """Add persona to local simulator."""
        try:
            if persona_id not in self.simulator.personas:
                persona = Persona(
                    persona_id=persona_id,
                    name=name,
                    description=description,
                    preferences=preferences,
                    created_at=datetime.now()
                )
                self.simulator.personas[persona_id] = persona
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add persona locally: {e}")
            return False

    def _add_category_neo4j(self, name: str, description: str, parent_category: Optional[str] = None) -> bool:
        """Add category to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (c:Category {name: $name})
                    SET c.description = $description,
                        c.parent_category = $parent_category,
                        c.created_at = datetime(),
                        c.tool_count = 0
                """, name=name, description=description, parent_category=parent_category)
            return True
        except Exception as e:
            logger.error(f"Failed to add category to Neo4j: {e}")
            return False

    def _add_category_local(self, name: str, description: str, parent_category: Optional[str] = None) -> bool:
        """Add category to local simulator."""
        try:
            if name not in self.simulator.categories:
                category = Category(
                    name=name,
                    description=description,
                    parent_category=parent_category,
                    created_at=datetime.now()
                )
                self.simulator.categories[name] = category
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add category locally: {e}")
            return False

    def _add_feature_neo4j(self, name: str, description: str, tool_name: str) -> bool:
        """Add feature to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (f:Feature {name: $name, tool_name: $tool_name})
                    SET f.description = $description,
                        f.created_at = datetime(),
                        f.is_active = true
                """, name=name, description=description, tool_name=tool_name)
            return True
        except Exception as e:
            logger.error(f"Failed to add feature to Neo4j: {e}")
            return False

    def _add_feature_local(self, name: str, description: str, tool_name: str) -> bool:
        """Add feature to local simulator."""
        try:
            if name not in self.simulator.features:
                feature = Feature(
                    name=name,
                    description=description,
                    tool_name=tool_name,
                    created_at=datetime.now()
                )
                self.simulator.features[name] = feature
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add feature locally: {e}")
            return False

    def _add_command_neo4j(self, command_id: str, command: str, description: str,
                           tool_name: str, os_type: str) -> bool:
        """Add command to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (cmd:Command {command_id: $command_id})
                    SET cmd.command = $command,
                        cmd.description = $description,
                        cmd.tool_name = $tool_name,
                        cmd.os_type = $os_type,
                        cmd.created_at = datetime(),
                        cmd.success_rate = 0.0,
                        cmd.usage_count = 0
                """, command_id=command_id, command=command, description=description,
                     tool_name=tool_name, os_type=os_type)
            return True
        except Exception as e:
            logger.error(f"Failed to add command to Neo4j: {e}")
            return False

    def _add_command_local(self, command_id: str, command: str, description: str,
                           tool_name: str, os_type: str) -> bool:
        """Add command to local simulator."""
        try:
            if command_id not in self.simulator.commands:
                command = Command(
                    command_id=command_id,
                    command=command,
                    description=description,
                    tool_name=tool_name,
                    os_type=os_type,
                    created_at=datetime.now()
                )
                self.simulator.commands[command_id] = command
                self.simulator._save_data()
            return True
        except Exception as e:
            logger.error(f"Failed to add command locally: {e}")
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
            relationship_type: Type of relationship
            
        Returns:
            bool: True if successful
        """
        if self.driver:
            return self._add_relationship_neo4j(tool1, tool2, relationship_type)
        else:
            return self._add_relationship_local(tool1, tool2, relationship_type)

    def add_tool_dependency(self, tool_name: str, library_name: str, version: str = None) -> bool:
        """Add a dependency relationship between a tool and a library."""
        if self.driver:
            return self._add_tool_dependency_neo4j(tool_name, library_name, version)
        else:
            return self._add_tool_dependency_local(tool_name, library_name, version)

    def add_tool_requirement(self, tool_name: str, os_name: str, os_version: str = None) -> bool:
        """Add a requirement relationship between a tool and an OS."""
        if self.driver:
            return self._add_tool_requirement_neo4j(tool_name, os_name, os_version)
        else:
            return self._add_tool_requirement_local(tool_name, os_name, os_version)

    def add_error_fix(self, error_id: str, command_id: str) -> bool:
        """Add a relationship between an error and a command that fixes it."""
        if self.driver:
            return self._add_error_fix_neo4j(error_id, command_id)
        else:
            return self._add_error_fix_local(error_id, command_id)

    def add_persona_preference(self, persona_id: str, tool_name: str, preference_score: float = 1.0) -> bool:
        """Add a preference relationship between a persona and a tool."""
        if self.driver:
            return self._add_persona_preference_neo4j(persona_id, tool_name, preference_score)
        else:
            return self._add_persona_preference_local(persona_id, tool_name, preference_score)

    def add_tool_category(self, tool_name: str, category_name: str) -> bool:
        """Add a relationship between a tool and a category."""
        if self.driver:
            return self._add_tool_category_neo4j(tool_name, category_name)
        else:
            return self._add_tool_category_local(tool_name, category_name)

    def add_tool_feature(self, tool_name: str, feature_name: str) -> bool:
        """Add a relationship between a tool and a feature."""
        if self.driver:
            return self._add_tool_feature_neo4j(tool_name, feature_name)
        else:
            return self._add_tool_feature_local(tool_name, feature_name)
    
    def _add_relationship_neo4j(self, tool1: str, tool2: str, relationship_type: str) -> bool:
        """Add relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (t1:Tool {name: $tool1})
                    MATCH (t2:Tool {name: $tool2})
                    MERGE (t1)-[r:RELATED_TO {type: $relationship_type}]->(t2)
                    SET r.created_at = datetime()
                """, tool1=tool1, tool2=tool2, relationship_type=relationship_type)
            return True
        except Exception as e:
            logger.error(f"Failed to add relationship to Neo4j: {e}")
            return False

    def _add_tool_dependency_neo4j(self, tool_name: str, library_name: str, version: str = None) -> bool:
        """Add tool dependency relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (t:Tool {name: $tool_name})
                    MATCH (l:Library {name: $library_name})
                    MERGE (t)-[r:HAS_DEPENDENCY]->(l)
                    SET r.version = $version,
                        r.created_at = datetime()
                """, tool_name=tool_name, library_name=library_name, version=version)
            return True
        except Exception as e:
            logger.error(f"Failed to add tool dependency to Neo4j: {e}")
            return False

    def _add_tool_requirement_neo4j(self, tool_name: str, os_name: str, os_version: str = None) -> bool:
        """Add tool OS requirement relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (t:Tool {name: $tool_name})
                    MATCH (o:OS {name: $os_name})
                    MERGE (t)-[r:REQUIRES]->(o)
                    SET r.version = $os_version,
                        r.created_at = datetime()
                """, tool_name=tool_name, os_name=os_name, os_version=os_version)
            return True
        except Exception as e:
            logger.error(f"Failed to add tool requirement to Neo4j: {e}")
            return False

    def _add_error_fix_neo4j(self, error_id: str, command_id: str) -> bool:
        """Add error fix relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (e:Error {error_id: $error_id})
                    MATCH (cmd:Command {command_id: $command_id})
                    MERGE (e)-[r:FIXED_BY]->(cmd)
                    SET r.created_at = datetime()
                """, error_id=error_id, command_id=command_id)
            return True
        except Exception as e:
            logger.error(f"Failed to add error fix to Neo4j: {e}")
            return False

    def _add_persona_preference_neo4j(self, persona_id: str, tool_name: str, preference_score: float = 1.0) -> bool:
        """Add persona preference relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (p:Persona {persona_id: $persona_id})
                    MATCH (t:Tool {name: $tool_name})
                    MERGE (p)-[r:PREFERS]->(t)
                    SET r.score = $preference_score,
                        r.created_at = datetime()
                """, persona_id=persona_id, tool_name=tool_name, preference_score=preference_score)
            return True
        except Exception as e:
            logger.error(f"Failed to add persona preference to Neo4j: {e}")
            return False

    def _add_tool_category_neo4j(self, tool_name: str, category_name: str) -> bool:
        """Add tool category relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (t:Tool {name: $tool_name})
                    MATCH (c:Category {name: $category_name})
                    MERGE (t)-[r:RELATED_TO]->(c)
                    SET r.created_at = datetime()
                """, tool_name=tool_name, category_name=category_name)
            return True
        except Exception as e:
            logger.error(f"Failed to add tool category to Neo4j: {e}")
            return False

    def _add_tool_feature_neo4j(self, tool_name: str, feature_name: str) -> bool:
        """Add tool feature relationship to Neo4j database."""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (t:Tool {name: $tool_name})
                    MATCH (f:Feature {name: $feature_name, tool_name: $tool_name})
                    MERGE (t)-[r:INCLUDES]->(f)
                    SET r.created_at = datetime()
                """, tool_name=tool_name, feature_name=feature_name)
            return True
        except Exception as e:
            logger.error(f"Failed to add tool feature to Neo4j: {e}")
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

    def _add_tool_dependency_local(self, tool_name: str, library_name: str, version: str = None) -> bool:
        """Add tool dependency relationship to local simulator."""
        try:
            # Ensure both tool and library exist
            if tool_name not in self.simulator.tools:
                logger.warning(f"Tool {tool_name} not found, creating placeholder")
                self.simulator.tools[tool_name] = ToolNode(
                    name=tool_name,
                    category="unknown",
                    description="Placeholder tool",
                    install_command="",
                    check_command="",
                    created_at=datetime.now()
                )
            
            if library_name not in self.simulator.libraries:
                logger.warning(f"Library {library_name} not found, creating placeholder")
                self.simulator.libraries[library_name] = Library(
                    name=library_name,
                    version=version or "latest",
                    language="unknown",
                    description="Placeholder library",
                    created_at=datetime.now()
                )
            
            # Add relationship
            relationship_key = f"{tool_name}_depends_on_{library_name}"
            if relationship_key not in self.simulator.relationships:
                self.simulator.relationships[relationship_key] = {
                    "type": "HAS_DEPENDENCY",
                    "tool": tool_name,
                    "library": library_name,
                    "version": version,
                    "created_at": datetime.now().isoformat()
                }
                self.simulator._save_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add tool dependency locally: {e}")
            return False

    def _add_tool_requirement_local(self, tool_name: str, os_name: str, os_version: str = None) -> bool:
        """Add tool OS requirement relationship to local simulator."""
        try:
            # Ensure tool exists
            if tool_name not in self.simulator.tools:
                logger.warning(f"Tool {tool_name} not found, creating placeholder")
                self.simulator.tools[tool_name] = ToolNode(
                    name=tool_name,
                    category="unknown",
                    description="Placeholder tool",
                    install_command="",
                    check_command="",
                    created_at=datetime.now()
                )
            
            # Add relationship
            relationship_key = f"{tool_name}_requires_{os_name}"
            if relationship_key not in self.simulator.relationships:
                self.simulator.relationships[relationship_key] = {
                    "type": "REQUIRES",
                    "tool": tool_name,
                    "os": os_name,
                    "version": os_version,
                    "created_at": datetime.now().isoformat()
                }
                self.simulator._save_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add tool requirement locally: {e}")
            return False

    def _add_error_fix_local(self, error_id: str, command_id: str) -> bool:
        """Add error fix relationship to local simulator."""
        try:
            # Ensure both error and command exist
            if error_id not in self.simulator.errors:
                logger.warning(f"Error {error_id} not found")
                return False
            
            if command_id not in self.simulator.commands:
                logger.warning(f"Command {command_id} not found")
                return False
            
            # Add relationship
            relationship_key = f"{error_id}_fixed_by_{command_id}"
            if relationship_key not in self.simulator.relationships:
                self.simulator.relationships[relationship_key] = {
                    "type": "FIXED_BY",
                    "error": error_id,
                    "command": command_id,
                    "created_at": datetime.now().isoformat()
                }
                self.simulator._save_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add error fix locally: {e}")
            return False

    def _add_persona_preference_local(self, persona_id: str, tool_name: str, preference_score: float = 1.0) -> bool:
        """Add persona preference relationship to local simulator."""
        try:
            # Ensure both persona and tool exist
            if persona_id not in self.simulator.personas:
                logger.warning(f"Persona {persona_id} not found")
                return False
            
            if tool_name not in self.simulator.tools:
                logger.warning(f"Tool {tool_name} not found")
                return False
            
            # Add relationship
            relationship_key = f"{persona_id}_prefers_{tool_name}"
            if relationship_key not in self.simulator.relationships:
                self.simulator.relationships[relationship_key] = {
                    "type": "PREFERS",
                    "persona": persona_id,
                    "tool": tool_name,
                    "score": preference_score,
                    "created_at": datetime.now().isoformat()
                }
                self.simulator._save_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add persona preference locally: {e}")
            return False

    def _add_tool_category_local(self, tool_name: str, category_name: str) -> bool:
        """Add tool category relationship to local simulator."""
        try:
            # Ensure both tool and category exist
            if tool_name not in self.simulator.tools:
                logger.warning(f"Tool {tool_name} not found")
                return False
            
            if category_name not in self.simulator.categories:
                logger.warning(f"Category {category_name} not found")
                return False
            
            # Add relationship
            relationship_key = f"{tool_name}_in_category_{category_name}"
            if relationship_key not in self.simulator.relationships:
                self.simulator.relationships[relationship_key] = {
                    "type": "RELATED_TO",
                    "tool": tool_name,
                    "category": category_name,
                    "created_at": datetime.now().isoformat()
                }
                self.simulator._save_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add tool category locally: {e}")
            return False

    def _add_tool_feature_local(self, tool_name: str, feature_name: str) -> bool:
        """Add tool feature relationship to local simulator."""
        try:
            # Ensure both tool and feature exist
            if tool_name not in self.simulator.tools:
                logger.warning(f"Tool {tool_name} not found")
                return False
            
            if feature_name not in self.simulator.features:
                logger.warning(f"Feature {feature_name} not found")
                return False
            
            # Add relationship
            relationship_key = f"{tool_name}_includes_{feature_name}"
            if relationship_key not in self.simulator.relationships:
                self.simulator.relationships[relationship_key] = {
                    "type": "INCLUDES",
                    "tool": tool_name,
                    "feature": feature_name,
                    "created_at": datetime.now().isoformat()
                }
                self.simulator._save_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to add tool feature locally: {e}")
            return False
    
    def get_install_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get installation statistics for the specified period.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict[str, Any]: Statistics including success rates, top tools, etc.
        """
        if self.driver:
            return self._get_install_statistics_neo4j(days)
        else:
            return self._get_install_statistics_local(days)

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dict[str, Any]: Complete graph statistics
        """
        if self.driver:
            return self._get_graph_statistics_neo4j()
        else:
            return self._get_graph_statistics_local()

    def _get_graph_statistics_neo4j(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics from Neo4j."""
        try:
            with self.driver.session() as session:
                # Node counts
                node_counts = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] as type, count(n) as count
                    ORDER BY count DESC
                """).data()
                
                # Relationship counts
                relationship_counts = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                    ORDER BY count DESC
                """).data()
                
                # Top installed tools
                top_tools = session.run("""
                    MATCH (t:Tool)
                    RETURN t.name as name, t.total_installs as installs, t.install_success_rate as success_rate
                    ORDER BY t.total_installs DESC
                    LIMIT 5
                """).data()
                
                # Most common failures
                common_failures = session.run("""
                    MATCH (e:Error)
                    RETURN e.message as message, e.frequency as frequency, e.tool_name as tool
                    ORDER BY e.frequency DESC
                    LIMIT 5
                """).data()
                
                # Recent install events
                recent_events = session.run("""
                    MATCH (e:InstallEvent)
                    WHERE e.timestamp > datetime() - duration({days: 7})
                    RETURN count(e) as recent_installs,
                           count(CASE WHEN e.success = true THEN 1 END) as successful,
                           count(CASE WHEN e.success = false THEN 1 END) as failed
                """).data()
                
                # Tool categories distribution
                category_distribution = session.run("""
                    MATCH (t:Tool)
                    RETURN t.category as category, count(t) as count
                    ORDER BY count DESC
                """).data()
                
                return {
                    "node_counts": {item["type"]: item["count"] for item in node_counts},
                    "relationship_counts": {item["type"]: item["count"] for item in relationship_counts},
                    "top_installed_tools": top_tools,
                    "most_common_failures": common_failures,
                    "recent_activity": recent_events[0] if recent_events else {},
                    "category_distribution": category_distribution,
                    "total_nodes": sum(item["count"] for item in node_counts),
                    "total_relationships": sum(item["count"] for item in relationship_counts)
                }
        except Exception as e:
            logger.error(f"Failed to get graph statistics from Neo4j: {e}")
            return {}

    def _get_graph_statistics_local(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics from local simulator."""
        try:
            # Node counts
            node_counts = {
                "Tool": len(self.simulator.tools),
                "Library": len(self.simulator.libraries),
                "Error": len(self.simulator.errors),
                "Persona": len(self.simulator.personas),
                "Category": len(self.simulator.categories),
                "Feature": len(self.simulator.features),
                "Command": len(self.simulator.commands),
                "User": len(self.simulator.user_profiles)
            }
            
            # Top installed tools
            top_tools = sorted(
                self.simulator.tools.values(),
                key=lambda x: x.total_installs,
                reverse=True
            )[:5]
            
            # Most common failures
            common_failures = sorted(
                self.simulator.errors.values(),
                key=lambda x: x.frequency,
                reverse=True
            )[:5]
            
            # Recent activity
            recent_events = [e for e in self.simulator.install_events 
                           if e.timestamp > datetime.now() - timedelta(days=7)]
            
            recent_stats = {
                "recent_installs": len(recent_events),
                "successful": len([e for e in recent_events if e.success]),
                "failed": len([e for e in recent_events if not e.success])
            }
            
            # Category distribution
            category_counts = {}
            for tool in self.simulator.tools.values():
                category_counts[tool.category] = category_counts.get(tool.category, 0) + 1
            
            return {
                "node_counts": node_counts,
                "relationship_counts": {"RELATED_TO": len(self.simulator.relationships)},
                "top_installed_tools": [
                    {"name": t.name, "installs": t.total_installs, "success_rate": t.install_success_rate}
                    for t in top_tools
                ],
                "most_common_failures": [
                    {"message": e.message, "frequency": e.frequency, "tool": e.tool_name}
                    for e in common_failures
                ],
                "recent_activity": recent_stats,
                "category_distribution": [{"category": k, "count": v} for k, v in category_counts.items()],
                "total_nodes": sum(node_counts.values()),
                "total_relationships": len(self.simulator.relationships)
            }
        except Exception as e:
            logger.error(f"Failed to get graph statistics locally: {e}")
            return {}
    
    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close() 