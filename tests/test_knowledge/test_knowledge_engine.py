"""
Test Knowledge Engine
====================

Unit tests for the CONFIGO knowledge engine functionality.
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime
from pathlib import Path

# Import knowledge layer components
from knowledge.knowledge_engine import KnowledgeEngine, KnowledgeQuery, KnowledgeResult
from knowledge.config import KnowledgeConfig


class TestKnowledgeEngine(unittest.TestCase):
    """Test cases for the KnowledgeEngine class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.graph_path = os.path.join(self.test_dir, 'test_graph')
        self.vector_path = os.path.join(self.test_dir, 'test_vectors')
        
        # Initialize knowledge engine with test configuration
        graph_config = {
            'storage_path': self.graph_path,
            'enabled': True
        }
        vector_config = {
            'storage_path': self.vector_path,
            'enabled': True
        }
        
        self.engine = KnowledgeEngine(graph_config, vector_config)
    
    def tearDown(self):
        """Clean up test environment."""
        # Close engine connections
        self.engine.close()
        
        # Remove test directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_engine_initialization(self):
        """Test knowledge engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.graph_db)
        self.assertIsNotNone(self.engine.vector_db)
    
    def test_log_install_event(self):
        """Test logging installation events."""
        # Test successful installation
        success = self.engine.log_install_event(
            tool_name="docker",
            command="apt-get install docker",
            success=True,
            os_type="linux",
            architecture="x86_64"
        )
        self.assertTrue(success)
        
        # Test failed installation
        success = self.engine.log_install_event(
            tool_name="python",
            command="apt-get install python",
            success=False,
            os_type="linux",
            architecture="x86_64",
            error_message="Package not found"
        )
        self.assertTrue(success)
    
    def test_add_tool_knowledge(self):
        """Test adding tool knowledge."""
        success = self.engine.add_tool_knowledge(
            tool_name="vscode",
            category="editor",
            description="Visual Studio Code editor",
            install_command="snap install code",
            check_command="code --version"
        )
        self.assertTrue(success)
    
    def test_add_tool_relationship(self):
        """Test adding tool relationships."""
        # First add tools
        self.engine.add_tool_knowledge(
            tool_name="python",
            category="language",
            description="Python programming language",
            install_command="apt-get install python3",
            check_command="python3 --version"
        )
        
        self.engine.add_tool_knowledge(
            tool_name="pip",
            category="package_manager",
            description="Python package installer",
            install_command="apt-get install python3-pip",
            check_command="pip3 --version"
        )
        
        # Add relationship
        success = self.engine.add_tool_relationship("python", "pip", "DEPENDS_ON")
        self.assertTrue(success)
    
    def test_query_similar_errors(self):
        """Test querying similar errors."""
        # Add some error messages first
        self.engine.vector_db.add_error_message(
            error_message="Permission denied",
            tool_name="docker",
            os_type="linux",
            architecture="x86_64",
            solution="Run with sudo"
        )
        
        self.engine.vector_db.add_error_message(
            error_message="Package not found",
            tool_name="python",
            os_type="linux",
            architecture="x86_64",
            solution="Update package list"
        )
        
        # Query similar errors
        result = self.engine.query_similar_errors("Permission denied", limit=5)
        
        self.assertIsInstance(result, KnowledgeResult)
        self.assertEqual(result.query.query_type, 'error')
        self.assertGreater(len(result.results), 0)
    
    def test_get_related_tools(self):
        """Test getting related tools."""
        # Add tools first
        self.engine.add_tool_knowledge(
            tool_name="python",
            category="language",
            description="Python programming language",
            install_command="apt-get install python3",
            check_command="python3 --version"
        )
        
        self.engine.add_tool_knowledge(
            tool_name="pip",
            category="package_manager",
            description="Python package installer",
            install_command="apt-get install python3-pip",
            check_command="pip3 --version"
        )
        
        # Add relationship
        self.engine.add_tool_relationship("python", "pip", "USED_WITH")
        
        # Get related tools
        result = self.engine.get_related_tools("python", limit=5)
        
        self.assertIsInstance(result, KnowledgeResult)
        self.assertEqual(result.query.query_type, 'tool')
    
    def test_get_recommended_plan(self):
        """Test getting recommended installation plans."""
        # Add some tools first
        self.engine.add_tool_knowledge(
            tool_name="docker",
            category="tool",
            description="Container platform",
            install_command="apt-get install docker",
            check_command="docker --version"
        )
        
        self.engine.add_tool_knowledge(
            tool_name="python",
            category="language",
            description="Python programming language",
            install_command="apt-get install python3",
            check_command="python3 --version"
        )
        
        # Get recommended plan
        user_profile = {
            'persona': 'developer',
            'preferences': {'auto_retry': True}
        }
        
        result = self.engine.get_recommended_plan(user_profile, "ai-stack")
        
        self.assertIsInstance(result, KnowledgeResult)
        self.assertEqual(result.query.query_type, 'recommendation')
    
    def test_find_similar_users(self):
        """Test finding similar users."""
        # Add user personas first
        self.engine.add_user_persona(
            user_id="user1",
            persona_description="AI developer working with Python and TensorFlow",
            preferences={'auto_retry': True, 'preferred_editor': 'vscode'}
        )
        
        self.engine.add_user_persona(
            user_id="user2",
            persona_description="Data scientist using Python and Jupyter",
            preferences={'auto_retry': False, 'preferred_editor': 'jupyter'}
        )
        
        # Find similar users
        result = self.engine.find_similar_users(
            "AI developer working with Python",
            limit=5
        )
        
        self.assertIsInstance(result, KnowledgeResult)
        self.assertEqual(result.query.query_type, 'user')
    
    def test_get_knowledge_statistics(self):
        """Test getting knowledge statistics."""
        # Add some data first
        self.engine.log_install_event(
            tool_name="docker",
            command="apt-get install docker",
            success=True,
            os_type="linux",
            architecture="x86_64"
        )
        
        self.engine.vector_db.add_error_message(
            error_message="Test error",
            tool_name="test",
            os_type="linux",
            architecture="x86_64"
        )
        
        # Get statistics
        stats = self.engine.get_knowledge_statistics(days=30)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('graph_database', stats)
        self.assertIn('vector_database', stats)
    
    def test_get_combined_insights(self):
        """Test getting combined insights for a tool."""
        # Add tool and related data
        self.engine.add_tool_knowledge(
            tool_name="python",
            category="language",
            description="Python programming language",
            install_command="apt-get install python3",
            check_command="python3 --version"
        )
        
        self.engine.add_tool_knowledge(
            tool_name="pip",
            category="package_manager",
            description="Python package installer",
            install_command="apt-get install python3-pip",
            check_command="pip3 --version"
        )
        
        self.engine.add_tool_relationship("python", "pip", "USED_WITH")
        
        # Get combined insights
        insights = self.engine.get_combined_insights("python")
        
        self.assertIsInstance(insights, dict)
        self.assertIn('tool_name', insights)
        self.assertIn('graph_insights', insights)
        self.assertIn('vector_insights', insights)
    
    def test_knowledge_query_creation(self):
        """Test KnowledgeQuery creation."""
        query = KnowledgeQuery(
            query_type='test',
            query_text='test query',
            context={'test': True}
        )
        
        self.assertEqual(query.query_type, 'test')
        self.assertEqual(query.query_text, 'test query')
        self.assertIn('test', query.context)
        self.assertIsInstance(query.timestamp, datetime)
    
    def test_knowledge_result_creation(self):
        """Test KnowledgeResult creation."""
        query = KnowledgeQuery(
            query_type='test',
            query_text='test query',
            context={}
        )
        
        result = KnowledgeResult(
            query=query,
            results=[{'test': 'data'}],
            confidence=0.8,
            source='test',
            metadata={'test': True}
        )
        
        self.assertEqual(result.query, query)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.source, 'test')


class TestKnowledgeConfig(unittest.TestCase):
    """Test cases for the KnowledgeConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = KnowledgeConfig()
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        self.assertIsNotNone(self.config.graph_db)
        self.assertIsNotNone(self.config.vector_db)
        self.assertIsNotNone(self.config.engine)
        self.assertIsNotNone(self.config.features)
        self.assertIsNotNone(self.config.performance)
    
    def test_get_graph_config(self):
        """Test getting graph database configuration."""
        graph_config = self.config.get_graph_config()
        self.assertIsInstance(graph_config, dict)
        self.assertIn('storage_path', graph_config)
        self.assertIn('enabled', graph_config)
    
    def test_get_vector_config(self):
        """Test getting vector database configuration."""
        vector_config = self.config.get_vector_config()
        self.assertIsInstance(vector_config, dict)
        self.assertIn('storage_path', vector_config)
        self.assertIn('embedding_model', vector_config)
    
    def test_feature_toggles(self):
        """Test feature toggle functionality."""
        # Test default feature states
        self.assertTrue(self.config.is_feature_enabled('error_matching'))
        self.assertTrue(self.config.is_feature_enabled('tool_recommendations'))
        
        # Test non-existent feature
        self.assertFalse(self.config.is_feature_enabled('non_existent_feature'))
    
    def test_performance_settings(self):
        """Test performance settings."""
        max_results = self.config.get_performance_setting('max_search_results')
        self.assertIsInstance(max_results, int)
        self.assertGreater(max_results, 0)
        
        threshold = self.config.get_performance_setting('similarity_threshold')
        self.assertIsInstance(threshold, float)
        self.assertGreaterEqual(threshold, 0.0)
        self.assertLessEqual(threshold, 1.0)
    
    def test_config_validation(self):
        """Test configuration validation."""
        validation = self.config.validate_config()
        
        self.assertIsInstance(validation, dict)
        self.assertIn('valid', validation)
        self.assertIn('warnings', validation)
        self.assertIn('errors', validation)
        
        self.assertIsInstance(validation['valid'], bool)
        self.assertIsInstance(validation['warnings'], list)
        self.assertIsInstance(validation['errors'], list)
    
    def test_config_save_load(self):
        """Test configuration save and load functionality."""
        # Test save
        success = self.config.save_config('.test_config.json')
        self.assertTrue(success)
        
        # Test load
        success = self.config.load_config('.test_config.json')
        self.assertTrue(success)
        
        # Clean up
        if os.path.exists('.test_config.json'):
            os.remove('.test_config.json')


if __name__ == '__main__':
    unittest.main() 