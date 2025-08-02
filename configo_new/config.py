"""
CONFIGO Configuration Management
===============================

Centralized configuration handling for all CONFIGO components.
Manages environment variables, API keys, and feature toggles.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


@dataclass
class APIConfig:
    """API configuration settings."""
    gemini_api_key: Optional[str] = None
    mem0_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    def __post_init__(self):
        """Load API keys from environment variables."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.mem0_api_key = os.getenv('MEM0_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    neo4j_uri: Optional[str] = None
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    graph_storage_path: str = ".configo_graph"
    vector_storage_path: str = ".configo_vectors"
    memory_storage_path: str = ".configo_memory"
    
    def __post_init__(self):
        """Load database configuration from environment variables."""
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_username = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
        self.graph_storage_path = os.getenv('CONFIGO_GRAPH_PATH', '.configo_graph')
        self.vector_storage_path = os.getenv('CONFIGO_VECTOR_PATH', '.configo_vectors')
        self.memory_storage_path = os.getenv('CONFIGO_MEMORY_PATH', '.configo_memory')


@dataclass
class FeatureConfig:
    """Feature toggle configuration."""
    memory_enabled: bool = True
    graph_enabled: bool = True
    vector_enabled: bool = True
    chat_enabled: bool = True
    portal_enabled: bool = True
    validation_enabled: bool = True
    auto_retry_enabled: bool = True
    debug_mode: bool = False
    
    def __post_init__(self):
        """Load feature toggles from environment variables."""
        self.memory_enabled = os.getenv('CONFIGO_MEMORY_ENABLED', 'true').lower() == 'true'
        self.graph_enabled = os.getenv('CONFIGO_GRAPH_ENABLED', 'true').lower() == 'true'
        self.vector_enabled = os.getenv('CONFIGO_VECTOR_ENABLED', 'true').lower() == 'true'
        self.chat_enabled = os.getenv('CONFIGO_CHAT_ENABLED', 'true').lower() == 'true'
        self.portal_enabled = os.getenv('CONFIGO_PORTAL_ENABLED', 'true').lower() == 'true'
        self.validation_enabled = os.getenv('CONFIGO_VALIDATION_ENABLED', 'true').lower() == 'true'
        self.auto_retry_enabled = os.getenv('CONFIGO_AUTO_RETRY_ENABLED', 'true').lower() == 'true'
        self.debug_mode = os.getenv('CONFIGO_DEBUG_MODE', 'false').lower() == 'true'


@dataclass
class UIConfig:
    """UI configuration settings."""
    theme: str = "dark"
    colors_enabled: bool = True
    animations_enabled: bool = True
    emoji_enabled: bool = True
    progress_bars_enabled: bool = True
    
    def __post_init__(self):
        """Load UI configuration from environment variables."""
        self.theme = os.getenv('CONFIGO_UI_THEME', 'dark')
        self.colors_enabled = os.getenv('CONFIGO_UI_COLORS', 'true').lower() == 'true'
        self.animations_enabled = os.getenv('CONFIGO_UI_ANIMATIONS', 'true').lower() == 'true'
        self.emoji_enabled = os.getenv('CONFIGO_UI_EMOJI', 'true').lower() == 'true'
        self.progress_bars_enabled = os.getenv('CONFIGO_UI_PROGRESS', 'true').lower() == 'true'


@dataclass
class PerformanceConfig:
    """Performance and optimization settings."""
    max_retry_attempts: int = 3
    timeout_seconds: int = 30
    max_search_results: int = 10
    similarity_threshold: float = 0.3
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    def __post_init__(self):
        """Load performance settings from environment variables."""
        self.max_retry_attempts = int(os.getenv('CONFIGO_MAX_RETRY_ATTEMPTS', '3'))
        self.timeout_seconds = int(os.getenv('CONFIGO_TIMEOUT_SECONDS', '30'))
        self.max_search_results = int(os.getenv('CONFIGO_MAX_SEARCH_RESULTS', '10'))
        self.similarity_threshold = float(os.getenv('CONFIGO_SIMILARITY_THRESHOLD', '0.3'))
        self.cache_enabled = os.getenv('CONFIGO_CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('CONFIGO_CACHE_TTL', '3600'))


class Config:
    """
    Main configuration class for CONFIGO.
    
    Centralizes all configuration settings and provides validation.
    """
    
    def __init__(self):
        """Initialize configuration with all subsystems."""
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.features = FeatureConfig()
        self.ui = UIConfig()
        self.performance = PerformanceConfig()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration and log warnings for missing required settings."""
        warnings = []
        
        # Check API keys
        if not self.api.gemini_api_key:
            warnings.append("GEMINI_API_KEY not set - LLM features may be limited")
        
        if not self.api.mem0_api_key:
            warnings.append("MEM0_API_KEY not set - using fallback memory system")
        
        # Check database configuration
        if self.features.graph_enabled and not self.database.neo4j_uri:
            warnings.append("NEO4J_URI not set - graph features disabled")
            self.features.graph_enabled = False
        
        # Log warnings
        if warnings:
            import logging
            logger = logging.getLogger(__name__)
            for warning in warnings:
                logger.warning(warning)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        key_map = {
            'gemini': self.api.gemini_api_key,
            'mem0': self.api.mem0_api_key,
            'google': self.api.google_api_key,
        }
        return key_map.get(service)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        feature_map = {
            'memory': self.features.memory_enabled,
            'graph': self.features.graph_enabled,
            'vector': self.features.vector_enabled,
            'chat': self.features.chat_enabled,
            'portal': self.features.portal_enabled,
            'validation': self.features.validation_enabled,
            'auto_retry': self.features.auto_retry_enabled,
            'debug': self.features.debug_mode,
        }
        return feature_map.get(feature, False)
    
    def get_storage_path(self, storage_type: str) -> str:
        """Get storage path for a specific type."""
        path_map = {
            'graph': self.database.graph_storage_path,
            'vector': self.database.vector_storage_path,
            'memory': self.database.memory_storage_path,
        }
        return path_map.get(storage_type, '.configo_data')
    
    def get_performance_setting(self, setting: str) -> Any:
        """Get a performance setting."""
        setting_map = {
            'max_retry_attempts': self.performance.max_retry_attempts,
            'timeout_seconds': self.performance.timeout_seconds,
            'max_search_results': self.performance.max_search_results,
            'similarity_threshold': self.performance.similarity_threshold,
            'cache_enabled': self.performance.cache_enabled,
            'cache_ttl': self.performance.cache_ttl,
        }
        return setting_map.get(setting)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            'api': {
                'gemini_api_key': '***' if self.api.gemini_api_key else None,
                'mem0_api_key': '***' if self.api.mem0_api_key else None,
                'google_api_key': '***' if self.api.google_api_key else None,
            },
            'database': {
                'neo4j_uri': self.database.neo4j_uri,
                'neo4j_username': self.database.neo4j_username,
                'graph_storage_path': self.database.graph_storage_path,
                'vector_storage_path': self.database.vector_storage_path,
                'memory_storage_path': self.database.memory_storage_path,
            },
            'features': {
                'memory_enabled': self.features.memory_enabled,
                'graph_enabled': self.features.graph_enabled,
                'vector_enabled': self.features.vector_enabled,
                'chat_enabled': self.features.chat_enabled,
                'portal_enabled': self.features.portal_enabled,
                'validation_enabled': self.features.validation_enabled,
                'auto_retry_enabled': self.features.auto_retry_enabled,
                'debug_mode': self.features.debug_mode,
            },
            'ui': {
                'theme': self.ui.theme,
                'colors_enabled': self.ui.colors_enabled,
                'animations_enabled': self.ui.animations_enabled,
                'emoji_enabled': self.ui.emoji_enabled,
                'progress_bars_enabled': self.ui.progress_bars_enabled,
            },
            'performance': {
                'max_retry_attempts': self.performance.max_retry_attempts,
                'timeout_seconds': self.performance.timeout_seconds,
                'max_search_results': self.performance.max_search_results,
                'similarity_threshold': self.performance.similarity_threshold,
                'cache_enabled': self.performance.cache_enabled,
                'cache_ttl': self.performance.cache_ttl,
            }
        }
    
    def validate_required_apis(self) -> Dict[str, bool]:
        """Validate that required API keys are available."""
        return {
            'gemini': bool(self.api.gemini_api_key),
            'mem0': bool(self.api.mem0_api_key),
            'google': bool(self.api.google_api_key),
        }
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get a summary of the current environment configuration."""
        return {
            'features_enabled': {
                'memory': self.features.memory_enabled,
                'graph': self.features.graph_enabled,
                'vector': self.features.vector_enabled,
                'chat': self.features.chat_enabled,
                'portal': self.features.portal_enabled,
                'validation': self.features.validation_enabled,
            },
            'apis_available': self.validate_required_apis(),
            'storage_paths': {
                'graph': self.database.graph_storage_path,
                'vector': self.database.vector_storage_path,
                'memory': self.database.memory_storage_path,
            },
            'performance': {
                'max_retry_attempts': self.performance.max_retry_attempts,
                'timeout_seconds': self.performance.timeout_seconds,
                'max_search_results': self.performance.max_search_results,
            }
        } 