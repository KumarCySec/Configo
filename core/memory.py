"""
CONFIGO Memory System
====================

Intelligent memory system that tracks user preferences, installed tools, and session history.
Provides context injection for LLM prompts and supports both mem0 integration and JSON fallback.

Features:
- 🧠 Persistent tool installation tracking
- 📊 Session history and analytics
- ⚙️ User preference management
- 🔍 Semantic memory search
- 🔄 Self-healing retry logic
- 📈 Performance analytics
- 👤 Multi-profile support
- 🌐 Login portal tracking
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def dataclass_to_dict(obj) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a dictionary.
    
    This is a replacement for the deprecated asdict function.
    
    Args:
        obj: Dataclass instance to convert
        
    Returns:
        Dict[str, Any]: Dictionary representation of the dataclass
    """
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name, field_info in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            if hasattr(value, '__dataclass_fields__'):
                result[field_name] = dataclass_to_dict(value)
            elif isinstance(value, (list, tuple)):
                result[field_name] = [
                    dataclass_to_dict(item) if hasattr(item, '__dataclass_fields__') else item
                    for item in value
                ]
            else:
                result[field_name] = value
        return result
    return obj

# Try to import mem0, fallback to JSON if not available
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
    logger.info("mem0 available - using intelligent memory storage")
except ImportError:
    MEM0_AVAILABLE = False
    logger.info("mem0 not available - using enhanced JSON-based memory with semantic simulation")

@dataclass
class ToolMemory:
    """
    Memory entry for a tool installation.
    
    Tracks installation details, success/failure status, versions,
    and retry information for intelligent decision making.
    """
    name: str
    install_command: str
    check_command: str
    installed_at: datetime
    version: Optional[str] = None
    last_failure: Optional[datetime] = None
    last_failure_error: Optional[str] = None
    extension_id: Optional[str] = None
    install_success: bool = True
    failure_count: int = 0
    is_extension: bool = False

@dataclass
class LoginPortalMemory:
    """
    Memory entry for login portals.
    
    Tracks portal visits, URLs, and usage statistics
    for better portal recommendations.
    """
    name: str
    url: str
    description: str
    last_opened: Optional[datetime] = None
    opened_count: int = 0

@dataclass
class UserPreferences:
    """
    User preferences and settings.
    
    Configurable preferences that affect tool installation
    behavior and user experience.
    """
    preferred_editor: str = "VS Code"
    skip_already_installed: bool = True
    auto_retry_failed: bool = True
    max_retry_attempts: int = 3
    preferred_package_manager: str = "apt-get"
    auto_open_login_portals: bool = True
    show_improvement_suggestions: bool = True

@dataclass
class SessionMemory:
    """
    Memory entry for user sessions.
    
    Tracks complete setup sessions with tools installed,
    failures, and user preferences for session analysis.
    """
    session_id: str
    environment: str
    start_time: datetime
    tools_installed: List[str]
    tools_failed: List[str]
    login_portals: List[str]
    user_preferences: UserPreferences
    end_time: Optional[datetime] = None
    """
    User preferences and settings.
    
    Configurable preferences that affect tool installation
    behavior and user experience.
    """
    preferred_editor: str = "VS Code"
    skip_already_installed: bool = True
    auto_retry_failed: bool = True
    max_retry_attempts: int = 3
    preferred_package_manager: str = "apt-get"
    auto_open_login_portals: bool = True
    show_improvement_suggestions: bool = True

@dataclass
class UserProfile:
    """
    User profile with preferences and history.
    
    Supports multiple user profiles with personalized
    settings and installation history.
    """
    profile_id: str
    name: str
    created_at: datetime
    preferences: UserPreferences
    installed_tools: Optional[List[str]] = None
    skipped_portals: Optional[List[str]] = None
    last_used: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.installed_tools is None:
            self.installed_tools = []
        if self.skipped_portals is None:
            self.skipped_portals = []

@dataclass
class SemanticMemoryEntry:
    """
    Entry for semantic memory storage.
    
    Stores content with metadata, timestamps, and tags
    for intelligent memory retrieval.
    """
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    tags: List[str]

class EnhancedJSONMemory:
    """
    Enhanced JSON-based memory with semantic simulation.
    
    Provides semantic search capabilities using keyword matching
    and tag-based retrieval when mem0 is not available.
    """
    
    def __init__(self, storage_path: str):
        """
        Initialize enhanced JSON memory storage.
        
        Args:
            storage_path: Path to the JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: List[SemanticMemoryEntry] = []
        self._load_entries()
    
    def _load_entries(self) -> None:
        """Load existing entries from file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.entries = [
                        SemanticMemoryEntry(
                            content=entry['content'],
                            metadata=entry['metadata'],
                            timestamp=datetime.fromisoformat(entry['timestamp']),
                            tags=entry.get('tags', [])
                        )
                        for entry in data.get('entries', [])
                    ]
        except Exception as e:
            logger.error(f"Error loading semantic memory: {e}")
            self.entries = []
    
    def _save_entries(self) -> None:
        """Save entries to file."""
        try:
            data = {
                'entries': [
                    {
                        'content': entry.content,
                        'metadata': entry.metadata,
                        'timestamp': entry.timestamp.isoformat(),
                        'tags': entry.tags
                    }
                    for entry in self.entries
                ]
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving semantic memory: {e}")
    
    def save(self, document: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Save document with metadata.
        
        Args:
            document: Content to save
            metadata: Optional metadata dictionary
        """
        # Extract tags from content for semantic search
        tags = self._extract_tags(document)
        
        entry = SemanticMemoryEntry(
            content=document,
            metadata=metadata or {},
            timestamp=datetime.now(),
            tags=tags
        )
        
        self.entries.append(entry)
        self._save_entries()
    
    def query(self, query: str, limit: int = 5) -> List[str]:
        """
        Query entries using simple keyword matching.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching content strings
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score entries based on word overlap
        scored_entries = []
        for entry in self.entries:
            content_lower = entry.content.lower()
            content_words = set(content_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words.intersection(content_words))
            if overlap > 0:
                scored_entries.append((overlap, entry))
        
        # Sort by score and return top results
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry.content for _, entry in scored_entries[:limit]]
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        Extract relevant tags from content.
        
        Args:
            content: Content to extract tags from
            
        Returns:
            List of extracted tags
        """
        # Simple tag extraction - can be enhanced
        words = content.lower().split()
        tags = []
        
        # Common tool-related keywords
        tool_keywords = ['install', 'tool', 'package', 'extension', 'failed', 'success', 'error']
        for word in words:
            if word in tool_keywords:
                tags.append(word)
        
        return tags

class AgentMemory:
    """
    Main memory system for the CONFIGO agent.
    
    Provides persistent storage for tool installations, sessions,
    user preferences, and semantic memory with mem0 integration.
    """
    
    def __init__(self, memory_dir: str = ".configo_memory"):
        """
        Initialize the agent memory system.
        
        Args:
            memory_dir: Directory to store memory files
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory storage files
        self.tools_file = self.memory_dir / "tools.json"
        self.sessions_file = self.memory_dir / "sessions.json"
        self.preferences_file = self.memory_dir / "preferences.json"
        self.portals_file = self.memory_dir / "portals.json"
        self.profiles_file = self.memory_dir / "profiles.json"
        self.semantic_file = self.memory_dir / "semantic.json"
        
        # Initialize memory components
        self._initialize_memory()
        
        # Initialize mem0 if available
        if MEM0_AVAILABLE:
            try:
                # Get mem0 API key from environment
                mem0_api_key = os.getenv('MEM0_API_KEY')
                if mem0_api_key:
                    # Initialize mem0 client with API key
                    from mem0 import MemoryClient
                    self.mem0_client = MemoryClient(api_key=mem0_api_key)
                    logger.info("mem0 client initialized successfully with API key")
                else:
                    logger.warning("MEM0_API_KEY not found - mem0 client not initialized")
                    self.mem0_client = None
            except Exception as e:
                logger.warning(f"Failed to initialize mem0 client: {e}")
                self.mem0_client = None
        else:
            self.mem0_client = None
        
        # Initialize enhanced JSON memory for semantic search
        self.semantic_memory = EnhancedJSONMemory(str(self.semantic_file))
        
        logger.info("Agent memory system initialized")
    
    def _initialize_memory(self) -> None:
        """Initialize memory storage with default values."""
        # Initialize tools memory
        if not self.tools_file.exists():
            self._save_memory()
        
        # Load existing memory
        self._load_memory()
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """
        Parse datetime string with fallback handling.
        
        Args:
            date_str: ISO format datetime string
            
        Returns:
            Parsed datetime object
        """
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            return datetime.now()
    
    def _load_memory(self) -> None:
        """Load all memory data from files."""
        try:
            # Load tools memory
            if self.tools_file.exists():
                with open(self.tools_file, 'r') as f:
                    tools_data = json.load(f)
                    self.tools_memory = {
                        name: ToolMemory(
                            name=name,
                            install_command=data['install_command'],
                            check_command=data['check_command'],
                            installed_at=self._parse_datetime(data['installed_at']),
                            version=data.get('version'),
                            last_failure=self._parse_datetime(data['last_failure']) if data.get('last_failure') else None,
                            last_failure_error=data.get('last_failure_error'),
                            extension_id=data.get('extension_id'),
                            install_success=data.get('install_success', True),
                            failure_count=data.get('failure_count', 0),
                            is_extension=data.get('is_extension', False)
                        )
                        for name, data in tools_data.items()
                    }
            else:
                self.tools_memory = {}
            
            # Load sessions memory
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    self.sessions_memory = {
                        session_id: SessionMemory(
                            session_id=session_id,
                            environment=data['environment'],
                            start_time=self._parse_datetime(data['start_time']),
                            tools_installed=data['tools_installed'],
                            tools_failed=data['tools_failed'],
                            login_portals=data['login_portals'],
                            user_preferences=UserPreferences(**data['user_preferences']),
                            end_time=self._parse_datetime(data['end_time']) if data.get('end_time') else None
                        )
                        for session_id, data in sessions_data.items()
                    }
            else:
                self.sessions_memory = {}
            
            # Load user preferences
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    prefs_data = json.load(f)
                    self.user_preferences = UserPreferences(**prefs_data)
            else:
                self.user_preferences = UserPreferences()
            
            # Load login portals memory
            if self.portals_file.exists():
                with open(self.portals_file, 'r') as f:
                    portals_data = json.load(f)
                    self.portals_memory = {
                        name: LoginPortalMemory(
                            name=name,
                            url=data['url'],
                            description=data['description'],
                            last_opened=self._parse_datetime(data['last_opened']) if data.get('last_opened') else None,
                            opened_count=data.get('opened_count', 0)
                        )
                        for name, data in portals_data.items()
                    }
            else:
                self.portals_memory = {}
            
            # Load user profiles
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r') as f:
                    profiles_data = json.load(f)
                    self.profiles = {
                        profile_id: UserProfile(
                            profile_id=profile_id,
                            name=data['name'],
                            created_at=self._parse_datetime(data['created_at']),
                            preferences=UserPreferences(**data['preferences']),
                            installed_tools=data.get('installed_tools', []),
                            skipped_portals=data.get('skipped_portals', []),
                            last_used=self._parse_datetime(data['last_used']) if data.get('last_used') else None
                        )
                        for profile_id, data in profiles_data.items()
                    }
            else:
                self.profiles = {}
            
            logger.info("Memory loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            # Initialize with defaults
            self.tools_memory = {}
            self.sessions_memory = {}
            self.user_preferences = UserPreferences()
            self.portals_memory = {}
            self.profiles = {}
    
    def _save_memory(self) -> None:
        """Save all memory data to files."""
        try:
            # Save tools memory
            tools_data = {
                name: {
                    'install_command': tool.install_command,
                    'check_command': tool.check_command,
                    'installed_at': tool.installed_at.isoformat(),
                    'version': tool.version,
                    'last_failure': tool.last_failure.isoformat() if tool.last_failure else None,
                    'last_failure_error': tool.last_failure_error,
                    'extension_id': tool.extension_id,
                    'install_success': tool.install_success,
                    'failure_count': tool.failure_count,
                    'is_extension': tool.is_extension
                }
                for name, tool in self.tools_memory.items()
            }
            with open(self.tools_file, 'w') as f:
                json.dump(tools_data, f, indent=2)
            
            # Save sessions memory
            sessions_data = {
                session_id: {
                    'environment': session.environment,
                    'start_time': session.start_time.isoformat(),
                    'tools_installed': session.tools_installed,
                    'tools_failed': session.tools_failed,
                    'login_portals': session.login_portals,
                    'user_preferences': dataclass_to_dict(session.user_preferences),
                    'end_time': session.end_time.isoformat() if session.end_time else None
                }
                for session_id, session in self.sessions_memory.items()
            }
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)
            
            # Save user preferences
            with open(self.preferences_file, 'w') as f:
                json.dump(dataclass_to_dict(self.user_preferences), f, indent=2)
            
            # Save portals memory
            portals_data = {
                name: {
                    'url': portal.url,
                    'description': portal.description,
                    'last_opened': portal.last_opened.isoformat() if portal.last_opened else None,
                    'opened_count': portal.opened_count
                }
                for name, portal in self.portals_memory.items()
            }
            with open(self.portals_file, 'w') as f:
                json.dump(portals_data, f, indent=2)
            
            # Save user profiles
            profiles_data = {
                profile_id: {
                    'name': profile.name,
                    'created_at': profile.created_at.isoformat(),
                    'preferences': dataclass_to_dict(profile.preferences),
                    'installed_tools': profile.installed_tools,
                    'skipped_portals': profile.skipped_portals,
                    'last_used': profile.last_used.isoformat() if profile.last_used else None
                }
                for profile_id, profile in self.profiles.items()
            }
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            logger.debug("Memory saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def save_to_memory(self, document: str, metadata: Optional[Dict[str, Any]] = None, 
                      user_id: Optional[str] = None, agent_id: Optional[str] = None) -> None:
        """
        Save document to semantic memory.
        
        Args:
            document: Content to save
            metadata: Optional metadata
            user_id: Optional user identifier
            agent_id: Optional agent identifier
        """
        if self.mem0_client:
            try:
                self.mem0_client.save(document, metadata, user_id, agent_id)
            except Exception as e:
                logger.warning(f"mem0 save failed, falling back to JSON: {e}")
                self.semantic_memory.save(document, metadata)
        else:
            self.semantic_memory.save(document, metadata)
    
    def query_memory(self, query: str, limit: int = 5, user_id: Optional[str] = None, 
                    agent_id: Optional[str] = None) -> List[str]:
        """
        Query semantic memory.
        
        Args:
            query: Search query
            limit: Maximum results to return
            user_id: Optional user identifier
            agent_id: Optional agent identifier
            
        Returns:
            List of matching content strings
        """
        if self.mem0_client:
            try:
                return self.mem0_client.query(query, limit, user_id, agent_id)
            except Exception as e:
                logger.warning(f"mem0 query failed, falling back to JSON: {e}")
                return self.semantic_memory.query(query, limit)
        else:
            return self.semantic_memory.query(query, limit)
    
    def record_tool_installation(self, tool_name: str, install_command: str, 
                                check_command: str, success: bool, 
                                version: Optional[str] = None, 
                                error: Optional[str] = None,
                                is_extension: bool = False,
                                extension_id: Optional[str] = None) -> None:
        """
        Record a tool installation attempt.
        
        Args:
            tool_name: Name of the tool
            install_command: Installation command used
            check_command: Command to check if tool is installed
            success: Whether installation was successful
            version: Installed version if successful
            error: Error message if failed
            is_extension: Whether this is an extension
            extension_id: Extension ID if applicable
        """
        now = datetime.now()
        
        if tool_name in self.tools_memory:
            # Update existing tool memory
            tool_memory = self.tools_memory[tool_name]
            if success:
                tool_memory.install_success = True
                tool_memory.version = version
                tool_memory.installed_at = now
                tool_memory.failure_count = 0
            else:
                tool_memory.install_success = False
                tool_memory.last_failure = now
                tool_memory.last_failure_error = error
                tool_memory.failure_count += 1
        else:
            # Create new tool memory
            self.tools_memory[tool_name] = ToolMemory(
                name=tool_name,
                install_command=install_command,
                check_command=check_command,
                installed_at=now,
                version=version if success else None,
                last_failure=now if not success else None,
                last_failure_error=error if not success else None,
                install_success=success,
                failure_count=0 if success else 1,
                is_extension=is_extension,
                extension_id=extension_id
            )
        
        # Save to persistent storage
        self._save_memory()
        
        # Save to semantic memory for context
        context = f"Tool {tool_name} installation {'succeeded' if success else 'failed'}"
        if version:
            context += f" with version {version}"
        if error:
            context += f" with error: {error}"
        
        self.save_to_memory(context, {
            'tool_name': tool_name,
            'success': success,
            'version': version,
            'error': error,
            'is_extension': is_extension
        })
    
    def get_tool_memory(self, tool_name: str) -> Optional[ToolMemory]:
        """Get memory for a specific tool."""
        return self.tools_memory.get(tool_name)
    
    def is_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is marked as successfully installed."""
        tool_memory = self.get_tool_memory(tool_name)
        return tool_memory.install_success if tool_memory else False
    
    def get_failed_tools(self) -> List[ToolMemory]:
        """Get list of tools that have failed installation."""
        return [tool for tool in self.tools_memory.values() if not tool.install_success]
    
    def get_recent_failures(self, days: int = 7) -> List[ToolMemory]:
        """
        Get tools that failed recently.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of tools that failed within the specified period
        """
        cutoff = datetime.now() - timedelta(days=days)
        return [
            tool for tool in self.tools_memory.values()
            if tool.last_failure and tool.last_failure > cutoff
        ]
    
    def should_skip_tool(self, tool_name: str) -> bool:
        """
        Determine if a tool should be skipped based on memory.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool should be skipped, False otherwise
        """
        tool_memory = self.get_tool_memory(tool_name)
        if not tool_memory:
            return False
        
        # Skip if successfully installed and user prefers to skip
        if tool_memory.install_success and self.user_preferences.skip_already_installed:
            return True
        
        # Skip if max retries reached
        if tool_memory.failure_count >= self.user_preferences.max_retry_attempts:
            return True
        
        return False
    
    def should_retry_tool(self, tool_name: str) -> bool:
        """
        Determine if a tool should be retried based on memory.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool should be retried, False otherwise
        """
        tool_memory = self.get_tool_memory(tool_name)
        if not tool_memory:
            return True  # New tool, should try
        
        # Don't retry if auto-retry is disabled
        if not self.user_preferences.auto_retry_failed:
            return False
        
        # Don't retry if max attempts reached
        if tool_memory.failure_count >= self.user_preferences.max_retry_attempts:
            return False
        
        return True
    
    def record_login_portal(self, name: str, url: str, description: str = "") -> None:
        """
        Record a login portal.
        
        Args:
            name: Portal name
            url: Portal URL
            description: Portal description
        """
        if name in self.portals_memory:
            # Update existing portal
            portal = self.portals_memory[name]
            portal.url = url
            portal.description = description
        else:
            # Create new portal
            self.portals_memory[name] = LoginPortalMemory(
                name=name,
                url=url,
                description=description
            )
        
        self._save_memory()
    
    def get_login_portals(self) -> List[LoginPortalMemory]:
        """Get all recorded login portals."""
        return list(self.portals_memory.values())
    
    def start_session(self, environment: str) -> str:
        """
        Start a new session.
        
        Args:
            environment: Environment description
            
        Returns:
            Session ID for the new session
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.sessions_memory[session_id] = SessionMemory(
            session_id=session_id,
            environment=environment,
            start_time=now,
            tools_installed=[],
            tools_failed=[],
            login_portals=[],
            user_preferences=self.user_preferences
        )
        
        self._save_memory()
        logger.info(f"Started session {session_id} for environment: {environment}")
        
        return session_id
    
    def end_session(self, session_id: str) -> None:
        """
        End a session.
        
        Args:
            session_id: ID of the session to end
        """
        if session_id in self.sessions_memory:
            self.sessions_memory[session_id].end_time = datetime.now()
            self._save_memory()
            logger.info(f"Ended session {session_id}")
    
    def update_session_tools(self, session_id: str, installed: List[str], failed: List[str]) -> None:
        """
        Update session with tool installation results.
        
        Args:
            session_id: Session ID
            installed: List of successfully installed tools
            failed: List of failed tools
        """
        if session_id in self.sessions_memory:
            session = self.sessions_memory[session_id]
            session.tools_installed = installed
            session.tools_failed = failed
            self._save_memory()
    
    def update_session_portals(self, session_id: str, portals: List[str]) -> None:
        """
        Update session with portal information.
        
        Args:
            session_id: Session ID
            portals: List of portal names
        """
        if session_id in self.sessions_memory:
            session = self.sessions_memory[session_id]
            session.login_portals = portals
            self._save_memory()
    
    def get_recent_sessions(self, limit: int = 5) -> List[SessionMemory]:
        """
        Get recent sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of recent sessions sorted by start time
        """
        sessions = list(self.sessions_memory.values())
        sessions.sort(key=lambda s: s.start_time, reverse=True)
        return sessions[:limit]
    
    def update_preferences(self, **kwargs) -> None:
        """
        Update user preferences.
        
        Args:
            **kwargs: Preference key-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self.user_preferences, key):
                setattr(self.user_preferences, key, value)
        
        self._save_memory()
    
    def get_memory_context(self) -> str:
        """
        Get memory context for LLM prompts.
        
        Returns:
            Formatted string with memory context
        """
        context_parts = []
        
        # Add tool installation history
        if self.tools_memory:
            successful_tools = [name for name, tool in self.tools_memory.items() if tool.install_success]
            failed_tools = [name for name, tool in self.tools_memory.items() if not tool.install_success]
            
            context_parts.append(f"Previously installed tools: {', '.join(successful_tools)}")
            if failed_tools:
                context_parts.append(f"Previously failed tools: {', '.join(failed_tools)}")
        
        # Add recent session information
        recent_sessions = self.get_recent_sessions(3)
        if recent_sessions:
            session_info = []
            for session in recent_sessions:
                session_info.append(f"{session.environment} ({len(session.tools_installed)} tools installed)")
            context_parts.append(f"Recent sessions: {'; '.join(session_info)}")
        
        # Add user preferences
        prefs = self.user_preferences
        context_parts.append(f"User preferences: editor={prefs.preferred_editor}, package_manager={prefs.preferred_package_manager}")
        
        # Add semantic memory context
        if self.mem0_client or self.semantic_memory.entries:
            recent_memory = self.query_memory("tool installation", limit=3)
            if recent_memory:
                context_parts.append(f"Recent memory: {'; '.join(recent_memory)}")
        
        return "\n".join(context_parts) if context_parts else "No previous context available"
    
    def record_login_portal_visit(self, portal_name: str, url: str) -> None:
        """
        Record a login portal visit.
        
        Args:
            portal_name: Name of the portal
            url: Portal URL
        """
        if portal_name in self.portals_memory:
            portal = self.portals_memory[portal_name]
            portal.last_opened = datetime.now()
            portal.opened_count += 1
        else:
            self.portals_memory[portal_name] = LoginPortalMemory(
                name=portal_name,
                url=url,
                description="",
                last_opened=datetime.now(),
                opened_count=1
            )
        
        self._save_memory()
        
        # Save to semantic memory
        self.save_to_memory(
            f"User visited login portal: {portal_name}",
            {'portal_name': portal_name, 'url': url}
        )
    
    def record_login_portal_status(self, portal_name: str, is_logged_in: bool, 
                                 last_check: Optional[float] = None, 
                                 installation_status: str = "not_installed") -> None:
        """
        Record login portal status.
        
        Args:
            portal_name: Name of the portal
            is_logged_in: Whether user is logged in
            last_check: Timestamp of last check
            installation_status: CLI tool installation status
        """
        # Save to semantic memory
        status_text = "logged in" if is_logged_in else "not logged in"
        self.save_to_memory(
            f"Login portal {portal_name} status: {status_text}, CLI tool: {installation_status}",
            {
                'portal_name': portal_name,
                'is_logged_in': is_logged_in,
                'last_check': last_check,
                'installation_status': installation_status
            }
        )
    
    def get_login_portals_memory(self) -> Dict[str, Any]:
        """
        Get login portals memory for context.
        
        Returns:
            Dictionary with portal memory information
        """
        return {
            'portals': [
                {
                    'name': portal.name,
                    'url': portal.url,
                    'description': portal.description,
                    'last_opened': portal.last_opened.isoformat() if portal.last_opened else None,
                    'opened_count': portal.opened_count
                }
                for portal in self.portals_memory.values()
            ],
            'total_portals': len(self.portals_memory),
            'recently_opened': [
                portal.name for portal in self.portals_memory.values()
                if portal.last_opened and (datetime.now() - portal.last_opened).days < 7
            ]
        }
    
    def get_tool_justification_context(self, tool_name: str) -> str:
        """
        Get context for tool justification.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Context string for tool justification
        """
        tool_memory = self.get_tool_memory(tool_name)
        if not tool_memory:
            return f"No previous installation history for {tool_name}"
        
        if tool_memory.install_success:
            return f"{tool_name} was successfully installed previously with version {tool_memory.version}"
        else:
            return f"{tool_name} failed installation {tool_memory.failure_count} times. Last error: {tool_memory.last_failure_error}"
    
    def clear_memory(self) -> None:
        """Clear all memory data."""
        self.tools_memory = {}
        self.sessions_memory = {}
        self.portals_memory = {}
        self.profiles = {}
        self.semantic_memory.entries = []
        
        # Clear files
        for file_path in [self.tools_file, self.sessions_file, self.portals_file, 
                         self.profiles_file, self.semantic_file]:
            if file_path.exists():
                file_path.unlink()
        
        # Reset preferences to defaults
        self.user_preferences = UserPreferences()
        self._save_memory()
        
        logger.info("Memory cleared successfully")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        total_tools = len(self.tools_memory)
        successful_installations = sum(1 for tool in self.tools_memory.values() if tool.install_success)
        failed_installations = total_tools - successful_installations
        success_rate = (successful_installations / total_tools * 100) if total_tools > 0 else 0
        
        return {
            "total_tools": total_tools,
            "successful_installations": successful_installations,
            "failed_installations": failed_installations,
            "total_sessions": len(self.sessions_memory),
            "success_rate": success_rate,
            "total_portals": len(self.portals_memory),
            "total_profiles": len(self.profiles),
            "semantic_entries": len(self.semantic_memory.entries)
        }
    
    def create_profile(self, profile_id: str, name: str) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            profile_id: Unique profile identifier
            name: Profile display name
            
        Returns:
            Created user profile
        """
        if profile_id in self.profiles:
            raise ValueError(f"Profile {profile_id} already exists")
        
        profile = UserProfile(
            profile_id=profile_id,
            name=name,
            created_at=datetime.now(),
            preferences=UserPreferences()
        )
        
        self.profiles[profile_id] = profile
        self._save_memory()
        
        logger.info(f"Created profile: {name} ({profile_id})")
        return profile
    
    def switch_profile(self, profile_id: str) -> bool:
        """
        Switch to a different user profile.
        
        Args:
            profile_id: Profile ID to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
        if profile_id not in self.profiles:
            logger.error(f"Profile {profile_id} not found")
            return False
        
        profile = self.profiles[profile_id]
        profile.last_used = datetime.now()
        
        # Update current preferences to match profile
        self.user_preferences = profile.preferences
        self._save_memory()
        
        logger.info(f"Switched to profile: {profile.name} ({profile_id})")
        return True
    
    def get_current_profile(self) -> Optional[UserProfile]:
        """
        Get the current active profile.
        
        Returns:
            Current profile or None if no profile is active
        """
        # Find profile that matches current preferences
        for profile in self.profiles.values():
            if (profile.preferences.preferred_editor == self.user_preferences.preferred_editor and
                profile.preferences.preferred_package_manager == self.user_preferences.preferred_package_manager):
                return profile
        return None
    
    def list_profiles(self) -> List[UserProfile]:
        """Get list of all user profiles."""
        return list(self.profiles.values())
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a user profile.
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if profile_id not in self.profiles:
            logger.error(f"Profile {profile_id} not found")
            return False
        
        profile_name = self.profiles[profile_id].name
        del self.profiles[profile_id]
        self._save_memory()
        
        logger.info(f"Deleted profile: {profile_name} ({profile_id})")
        return True
    
    def update_profile_preferences(self, profile_id: str, **preferences) -> bool:
        """
        Update preferences for a specific profile.
        
        Args:
            profile_id: Profile ID to update
            **preferences: Preference key-value pairs
            
        Returns:
            True if update successful, False otherwise
        """
        if profile_id not in self.profiles:
            logger.error(f"Profile {profile_id} not found")
            return False
        
        profile = self.profiles[profile_id]
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(profile.preferences, key):
                setattr(profile.preferences, key, value)
        
        profile.last_used = datetime.now()
        self._save_memory()
        
        logger.info(f"Updated preferences for profile: {profile.name} ({profile_id})")
        return True
    
    def _load_profiles(self) -> None:
        """Load user profiles from file."""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r') as f:
                    profiles_data = json.load(f)
                    self.profiles = {
                        profile_id: UserProfile(
                            profile_id=profile_id,
                            name=data['name'],
                            created_at=self._parse_datetime(data['created_at']),
                            preferences=UserPreferences(**data['preferences']),
                            installed_tools=data.get('installed_tools', []),
                            skipped_portals=data.get('skipped_portals', []),
                            last_used=self._parse_datetime(data['last_used']) if data.get('last_used') else None
                        )
                        for profile_id, data in profiles_data.items()
                    }
            else:
                self.profiles = {}
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
            self.profiles = {}
    
    def _save_profiles(self) -> None:
        """Save user profiles to file."""
        try:
            profiles_data = {
                profile_id: {
                    'name': profile.name,
                    'created_at': profile.created_at.isoformat(),
                    'preferences': dataclass_to_dict(profile.preferences),
                    'installed_tools': profile.installed_tools,
                    'skipped_portals': profile.skipped_portals,
                    'last_used': profile.last_used.isoformat() if profile.last_used else None
                }
                for profile_id, profile in self.profiles.items()
            }
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving profiles: {e}")
    
    def _load_profile_data(self, profile_id: str) -> None:
        """Load profile-specific data."""
        # This method can be extended to load profile-specific tool lists, etc.
        pass
    
    def get_profile_context(self, profile_id: str) -> str:
        """Get context string for a specific profile."""
        profile = self._get_profile_by_id(profile_id)
        if not profile:
            return ""
        
        context = f"Profile: {profile.name}\n"
        context += f"Created: {profile.created_at.strftime('%Y-%m-%d')}\n"
        context += f"Last Used: {profile.last_used.strftime('%Y-%m-%d %H:%M') if profile.last_used else 'Never'}\n"
        context += f"Installed Tools: {', '.join(profile.installed_tools)}\n"
        context += f"Preferences: {profile.preferences}\n"
        
        return context

    def record_app_install(self, app_name: str, plan: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Record app installation information to memory.
        
        Args:
            app_name: Name of the installed app
            plan: Original installation plan
            result: Installation result
        """
        try:
            # Create app installation record
            app_record = {
                'app_name': app_name,
                'installed_at': datetime.now().isoformat(),
                'method': result.get('method', 'unknown'),
                'success': result.get('success', False),
                'version': result.get('version'),
                'launch_command': result.get('launch_command', ''),
                'desktop_entry': result.get('desktop_entry', {}),
                'error': result.get('error'),
                'install_commands': result.get('install_commands', [])
            }
            
            # Load existing installed apps
            installed_apps_file = self.memory_dir / 'installed_apps.json'
            installed_apps = {}
            
            if installed_apps_file.exists():
                try:
                    with open(installed_apps_file, 'r') as f:
                        installed_apps = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading installed apps: {e}")
                    installed_apps = {}
            
            # Add/update app record
            installed_apps[app_name] = app_record
            
            # Save to file
            with open(installed_apps_file, 'w') as f:
                json.dump(installed_apps, f, indent=2)
            
            # Also save to semantic memory for context
            memory_context = f"App {app_name} was installed using {result.get('method', 'unknown')} method. "
            if result.get('success'):
                memory_context += f"Installation was successful. Launch command: {result.get('launch_command', 'N/A')}"
            else:
                memory_context += f"Installation failed: {result.get('error', 'Unknown error')}"
            
            self.save_to_memory(
                memory_context,
                metadata={
                    'type': 'app_installation',
                    'app_name': app_name,
                    'success': result.get('success', False),
                    'method': result.get('method', 'unknown')
                }
            )
            
            logger.info(f"Recorded app installation: {app_name}")
            
        except Exception as e:
            logger.error(f"Error recording app installation for {app_name}: {e}")

    def get_installed_apps(self) -> Dict[str, Any]:
        """
        Get all installed apps from memory.
        
        Returns:
            Dict[str, Any]: Dictionary of installed apps
        """
        try:
            installed_apps_file = self.memory_dir / 'installed_apps.json'
            if installed_apps_file.exists():
                with open(installed_apps_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading installed apps: {e}")
        
        return {}

    def is_app_installed(self, app_name: str) -> bool:
        """
        Check if an app is already installed.
        
        Args:
            app_name: Name of the app to check
            
        Returns:
            bool: True if app is installed, False otherwise
        """
        installed_apps = self.get_installed_apps()
        app_record = installed_apps.get(app_name)
        
        if app_record:
            return app_record.get('success', False)
        
        return False 