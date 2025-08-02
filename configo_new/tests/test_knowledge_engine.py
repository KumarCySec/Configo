"""
Tests for CONFIGO Knowledge Engine
==================================

Tests the knowledge engine functionality including graph and vector operations.
"""

import pytest
from unittest.mock import Mock, patch
from knowledge.engine import KnowledgeEngine


class TestKnowledgeEngine:
    """Test cases for the KnowledgeEngine class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = KnowledgeEngine()
    
    def test_initialization(self):
        """Test knowledge engine initialization."""
        assert self.engine is not None
        assert hasattr(self.engine, 'graph_manager')
        assert hasattr(self.engine, 'vector_manager')
    
    def test_add_tool_knowledge(self):
        """Test adding tool knowledge."""
        tool_name = "test-tool"
        metadata = {
            'description': 'Test tool',
            'category': 'testing',
            'version': '1.0.0'
        }
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            with patch.object(self.engine, 'vector_manager') as mock_vector:
                mock_graph.add_tool_node.return_value = True
                mock_vector.add_document.return_value = True
                
                result = self.engine.add_tool_knowledge(tool_name, metadata)
                assert result is True
    
    def test_add_relationship(self):
        """Test adding relationships."""
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            mock_graph.add_relationship.return_value = True
            
            result = self.engine.add_relationship('tool1', 'tool2', 'depends_on')
            assert result is True
    
    def test_search_tools(self):
        """Test tool search functionality."""
        query = "database"
        expected_results = [
            {'name': 'postgresql', 'description': 'Database', 'score': 0.9},
            {'name': 'mysql', 'description': 'Database', 'score': 0.8}
        ]
        
        with patch.object(self.engine, 'vector_manager') as mock_vector:
            mock_vector.search.return_value = expected_results
            
            results = self.engine.search_tools(query)
            assert len(results) == 2
            assert results[0]['name'] == 'postgresql'
    
    def test_search_tools_fallback(self):
        """Test tool search fallback when vector manager is not available."""
        query = "python"
        
        # Test with no vector manager
        self.engine.vector_manager = None
        results = self.engine.search_tools(query)
        
        # Should return fallback results
        assert len(results) > 0
        assert any('python' in result['name'].lower() for result in results)
    
    def test_get_tool_relationships(self):
        """Test getting tool relationships."""
        tool_name = "python"
        expected_relationships = [
            {'target': 'pip', 'type': 'package_manager'},
            {'target': 'django', 'type': 'framework'}
        ]
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            mock_graph.get_tool_relationships.return_value = expected_relationships
            
            relationships = self.engine.get_tool_relationships(tool_name)
            assert len(relationships) == 2
            assert relationships[0]['target'] == 'pip'
    
    def test_find_similar_tools(self):
        """Test finding similar tools."""
        tool_name = "python"
        expected_similar = [
            {'name': 'ruby', 'description': 'Programming language'},
            {'name': 'node', 'description': 'Runtime environment'}
        ]
        
        with patch.object(self.engine, 'vector_manager') as mock_vector:
            mock_vector.search.return_value = expected_similar
            
            similar = self.engine.find_similar_tools(tool_name)
            assert len(similar) == 2
    
    def test_get_tool_info(self):
        """Test getting tool information."""
        tool_name = "git"
        expected_info = {
            'name': 'git',
            'description': 'Version control system',
            'version': '2.39.2'
        }
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            mock_graph.get_tool_info.return_value = expected_info
            
            info = self.engine.get_tool_info(tool_name)
            assert info['name'] == 'git'
            assert info['description'] == 'Version control system'
    
    def test_query_graph(self):
        """Test graph querying."""
        query = "find tools related to python"
        expected_results = [
            {'tool': 'python', 'relationship': 'language'},
            {'tool': 'pip', 'relationship': 'package_manager'}
        ]
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            mock_graph.query.return_value = expected_results
            
            results = self.engine.query_graph(query)
            assert len(results) == 2
    
    def test_visualize_plan(self):
        """Test plan visualization."""
        plan_name = "web-stack"
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            mock_graph.visualize_plan.return_value = True
            
            result = self.engine.visualize_plan(plan_name)
            assert result is True
    
    def test_get_graph_stats(self):
        """Test getting graph statistics."""
        expected_stats = {
            'nodes': 10,
            'relationships': 15,
            'status': 'active'
        }
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            mock_graph.get_stats.return_value = expected_stats
            
            stats = self.engine.get_graph_stats()
            assert stats['nodes'] == 10
            assert stats['relationships'] == 15
    
    def test_get_vector_stats(self):
        """Test getting vector statistics."""
        expected_stats = {
            'documents': 100,
            'status': 'active'
        }
        
        with patch.object(self.engine, 'vector_manager') as mock_vector:
            mock_vector.get_stats.return_value = expected_stats
            
            stats = self.engine.get_vector_stats()
            assert stats['documents'] == 100
    
    def test_fallback_search(self):
        """Test fallback search functionality."""
        query = "git"
        results = self.engine._fallback_search(query, 5)
        
        assert len(results) > 0
        assert any('git' in result['name'].lower() for result in results)
    
    def test_add_installation_plan(self):
        """Test adding installation plan."""
        plan_name = "web-development"
        plan_data = {
            'environment': 'web development',
            'tools': ['git', 'node', 'npm']
        }
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            with patch.object(self.engine, 'vector_manager') as mock_vector:
                mock_graph.add_plan_node.return_value = True
                mock_vector.add_document.return_value = True
                
                result = self.engine.add_installation_plan(plan_name, plan_data)
                assert result is True
    
    def test_get_recommended_tools(self):
        """Test getting recommended tools."""
        environment_type = "web_development"
        
        with patch.object(self.engine, 'vector_manager') as mock_vector:
            mock_vector.search.return_value = [
                {'name': 'node', 'description': 'JavaScript runtime'},
                {'name': 'npm', 'description': 'Package manager'}
            ]
            
            recommendations = self.engine.get_recommended_tools(environment_type)
            assert len(recommendations) == 2
    
    def test_get_fallback_recommendations(self):
        """Test fallback recommendations."""
        environment_type = "python_development"
        recommendations = self.engine._get_fallback_recommendations(environment_type)
        
        assert len(recommendations) > 0
        assert any('python' in rec['name'].lower() for rec in recommendations)
    
    def test_backup_knowledge(self):
        """Test knowledge backup."""
        backup_path = "/tmp/configo_backup"
        
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            with patch.object(self.engine, 'vector_manager') as mock_vector:
                mock_graph.backup.return_value = True
                mock_vector.backup.return_value = True
                
                result = self.engine.backup_knowledge(backup_path)
                assert result is True
    
    def test_clear_knowledge(self):
        """Test clearing knowledge."""
        with patch.object(self.engine, 'graph_manager') as mock_graph:
            with patch.object(self.engine, 'vector_manager') as mock_vector:
                mock_graph.clear.return_value = True
                mock_vector.clear.return_value = True
                
                result = self.engine.clear_knowledge()
                assert result is True


if __name__ == '__main__':
    pytest.main([__file__]) 