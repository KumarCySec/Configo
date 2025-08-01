"""
CONFIGO Knowledge Layer Configuration
====================================

Configuration settings for the knowledge layer including database connections,
embedding models, and feature toggles.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class KnowledgeConfig:
    """Configuration class for CONFIGO knowledge layer."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables and defaults."""
        
        # Graph Database Configuration
        self.graph_db = {
            'uri': os.getenv('NEO4J_URI'),
            'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
            'password': os.getenv('NEO4J_PASSWORD', 'password'),
            'storage_path': os.getenv('CONFIGO_GRAPH_PATH', '.configo_graph'),
            'enabled': os.getenv('CONFIGO_GRAPH_ENABLED', 'true').lower() == 'true'
        }
        
        # Vector Database Configuration
        self.vector_db = {
            'storage_path': os.getenv('CONFIGO_VECTOR_PATH', '.configo_vectors'),
            'embedding_model': os.getenv('CONFIGO_EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
            'enabled': os.getenv('CONFIGO_VECTOR_ENABLED', 'true').lower() == 'true'
        }
        
        # Knowledge Engine Configuration
        self.engine = {
            'enabled': os.getenv('CONFIGO_KNOWLEDGE_ENABLED', 'true').lower() == 'true',
            'log_level': os.getenv('CONFIGO_KNOWLEDGE_LOG_LEVEL', 'INFO'),
            'auto_save': os.getenv('CONFIGO_AUTO_SAVE', 'true').lower() == 'true',
            'backup_enabled': os.getenv('CONFIGO_BACKUP_ENABLED', 'true').lower() == 'true'
        }
        
        # Feature Toggles
        self.features = {
            'error_matching': os.getenv('CONFIGO_ERROR_MATCHING', 'true').lower() == 'true',
            'tool_recommendations': os.getenv('CONFIGO_TOOL_RECOMMENDATIONS', 'true').lower() == 'true',
            'user_personas': os.getenv('CONFIGO_USER_PERSONAS', 'true').lower() == 'true',
            'semantic_search': os.getenv('CONFIGO_SEMANTIC_SEARCH', 'true').lower() == 'true',
            'graph_relationships': os.getenv('CONFIGO_GRAPH_RELATIONSHIPS', 'true').lower() == 'true'
        }
        
        # Performance Settings
        self.performance = {
            'max_search_results': int(os.getenv('CONFIGO_MAX_SEARCH_RESULTS', '10')),
            'similarity_threshold': float(os.getenv('CONFIGO_SIMILARITY_THRESHOLD', '0.3')),
            'cache_enabled': os.getenv('CONFIGO_CACHE_ENABLED', 'true').lower() == 'true',
            'cache_ttl': int(os.getenv('CONFIGO_CACHE_TTL', '3600'))  # 1 hour
        }
    
    def get_graph_config(self) -> Dict[str, Any]:
        """Get graph database configuration."""
        return self.graph_db.copy()
    
    def get_vector_config(self) -> Dict[str, Any]:
        """Get vector database configuration."""
        return self.vector_db.copy()
    
    def get_engine_config(self) -> Dict[str, Any]:
        """Get knowledge engine configuration."""
        return self.engine.copy()
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature_name, False)
    
    def get_performance_setting(self, setting_name: str) -> Any:
        """Get a performance setting."""
        return self.performance.get(setting_name)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results."""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check graph database configuration
        if self.graph_db['enabled']:
            if not self.graph_db['uri']:
                validation_results['warnings'].append(
                    "NEO4J_URI not set - using local graph simulation"
                )
        
        # Check vector database configuration
        if self.vector_db['enabled']:
            storage_path = Path(self.vector_db['storage_path'])
            if not storage_path.exists():
                try:
                    storage_path.mkdir(parents=True, exist_ok=True)
                    validation_results['warnings'].append(
                        f"Created vector storage directory: {storage_path}"
                    )
                except Exception as e:
                    validation_results['errors'].append(
                        f"Failed to create vector storage directory: {e}"
                    )
                    validation_results['valid'] = False
        
        # Check knowledge engine configuration
        if not self.engine['enabled']:
            validation_results['warnings'].append(
                "Knowledge engine is disabled - some features may not work"
            )
        
        # Check required directories
        required_dirs = [
            self.graph_db['storage_path'],
            self.vector_db['storage_path']
        ]
        
        for dir_path in required_dirs:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                validation_results['errors'].append(
                    f"Failed to create directory {dir_path}: {e}"
                )
                validation_results['valid'] = False
        
        return validation_results
    
    def save_config(self, config_path: str = '.configo_knowledge_config.json') -> bool:
        """Save current configuration to file."""
        try:
            import json
            config_data = {
                'graph_db': self.graph_db,
                'vector_db': self.vector_db,
                'engine': self.engine,
                'features': self.features,
                'performance': self.performance
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    def load_config(self, config_path: str = '.configo_knowledge_config.json') -> bool:
        """Load configuration from file."""
        try:
            import json
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            self.graph_db = config_data.get('graph_db', self.graph_db)
            self.vector_db = config_data.get('vector_db', self.vector_db)
            self.engine = config_data.get('engine', self.engine)
            self.features = config_data.get('features', self.features)
            self.performance = config_data.get('performance', self.performance)
            
            return True
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return False


# Global configuration instance
config = KnowledgeConfig()


def get_config() -> KnowledgeConfig:
    """Get the global configuration instance."""
    return config


def validate_and_setup() -> Dict[str, Any]:
    """Validate configuration and setup knowledge layer."""
    validation = config.validate_config()
    
    if validation['valid']:
        print("✅ Knowledge layer configuration validated successfully")
    else:
        print("❌ Knowledge layer configuration has errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("⚠️  Knowledge layer configuration warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    return validation 