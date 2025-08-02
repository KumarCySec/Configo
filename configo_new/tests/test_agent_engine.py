"""
Tests for CONFIGO Agent Engine
==============================

Tests the agent engine functionality including LLM integration and planning.
"""

import pytest
from unittest.mock import Mock, patch
from agent.agent_engine import AgentEngine


class TestAgentEngine:
    """Test cases for the AgentEngine class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.memory_mock = Mock()
        self.knowledge_mock = Mock()
        self.agent = AgentEngine(self.memory_mock, self.knowledge_mock)
    
    def test_initialization(self):
        """Test agent engine initialization."""
        assert self.agent is not None
        assert hasattr(self.agent, 'memory')
        assert hasattr(self.agent, 'knowledge')
        assert hasattr(self.agent, 'llm_client')
    
    @patch('agent.agent_engine.genai')
    def test_initialize_llm_client_success(self, mock_genai):
        """Test LLM client initialization with API key."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            agent = AgentEngine(Mock(), Mock())
            assert agent.llm_client is not None
    
    def test_initialize_llm_client_no_key(self):
        """Test LLM client initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            agent = AgentEngine(Mock(), Mock())
            assert agent.llm_client is None
    
    def test_generate_installation_plan(self):
        """Test installation plan generation."""
        environment = "python web development"
        memory_context = "Previous installations: git, python"
        
        self.memory_mock.get_memory_context.return_value = memory_context
        
        with patch.object(self.agent, '_get_llm_response') as mock_llm:
            mock_llm.return_value = '''
            {
                "name": "Python Web Development",
                "description": "Setup for Python web development",
                "steps": [
                    {
                        "name": "Install Python",
                        "command": "sudo apt-get install python3",
                        "description": "Install Python",
                        "tool_name": "python",
                        "is_extension": false,
                        "extension_id": null,
                        "dependencies": [],
                        "timeout": 300,
                        "priority": 1
                    }
                ]
            }
            '''
            
            plan = self.agent.generate_installation_plan(environment)
            assert plan['name'] == "Python Web Development"
            assert len(plan['steps']) == 1
            assert plan['steps'][0]['tool_name'] == "python"
    
    def test_generate_quick_plan(self):
        """Test quick plan generation."""
        tool_name = "git"
        
        # Test with cached memory
        self.memory_mock.get_tool_memory.return_value = Mock(
            install_success=True,
            install_command="sudo apt-get install git",
            check_command="git --version"
        )
        
        plan = self.agent.generate_quick_plan(tool_name)
        assert plan['name'] == "Quick Install: git"
        assert "sudo apt-get install git" in plan['command']
    
    def test_generate_quick_plan_new_tool(self):
        """Test quick plan generation for new tool."""
        tool_name = "new-tool"
        
        # No cached memory
        self.memory_mock.get_tool_memory.return_value = None
        
        with patch.object(self.agent, '_get_llm_response') as mock_llm:
            mock_llm.return_value = '''
            {
                "name": "Quick Install: new-tool",
                "command": "sudo apt-get install new-tool",
                "check_command": "new-tool --version",
                "description": "Quick installation of new-tool"
            }
            '''
            
            plan = self.agent.generate_quick_plan(tool_name)
            assert plan['name'] == "Quick Install: new-tool"
    
    def test_chat(self):
        """Test chat functionality."""
        user_input = "How do I install Python?"
        memory_context = "Previous chat about Python"
        
        self.memory_mock.get_memory_context.return_value = memory_context
        
        with patch.object(self.agent, '_get_llm_response') as mock_llm:
            mock_llm.return_value = "To install Python, use: sudo apt-get install python3"
            
            response = self.agent.chat(user_input)
            assert "sudo apt-get install python3" in response
            
            # Check that memory was saved
            self.memory_mock.save_to_memory.assert_called()
    
    def test_scan_project(self):
        """Test project scanning."""
        project_context = "Found: requirements.txt, package.json"
        
        with patch.object(self.agent, '_analyze_project_context') as mock_analyze:
            with patch.object(self.agent, '_get_llm_response') as mock_llm:
                mock_analyze.return_value = project_context
                mock_llm.return_value = '''
                {
                    "tools": [
                        {
                            "name": "python",
                            "type": "language",
                            "version": "3.11.0",
                            "confidence": 0.95,
                            "recommendations": ["Install virtual environment"]
                        }
                    ],
                    "missing_tools": [],
                    "recommendations": ["Use virtual environment"]
                }
                '''
                
                results = self.agent.scan_project()
                assert len(results['tools']) == 1
                assert results['tools'][0]['name'] == "python"
    
    def test_get_available_portals(self):
        """Test getting available portals."""
        portals = self.agent.get_available_portals()
        
        assert len(portals) > 0
        assert any(portal['name'] == 'GitHub' for portal in portals)
        assert any(portal['name'] == 'Docker Hub' for portal in portals)
    
    @patch('webbrowser.open')
    def test_launch_portals(self, mock_open):
        """Test portal launching."""
        self.agent.launch_portals()
        
        # Should have called webbrowser.open for each portal
        assert mock_open.call_count > 0
    
    def test_create_planning_prompt(self):
        """Test planning prompt creation."""
        environment = "web development"
        memory_context = "Previous installations"
        lite_mode = False
        
        prompt = self.agent._create_planning_prompt(environment, memory_context, lite_mode)
        
        assert environment in prompt
        assert memory_context in prompt
        assert "JSON" in prompt
        assert "steps" in prompt
    
    def test_create_quick_plan_prompt(self):
        """Test quick plan prompt creation."""
        tool_name = "git"
        
        prompt = self.agent._create_quick_plan_prompt(tool_name)
        
        assert tool_name in prompt
        assert "JSON" in prompt
        assert "Installation command" in prompt
    
    def test_create_chat_prompt(self):
        """Test chat prompt creation."""
        user_input = "How do I install Python?"
        memory_context = "Previous context"
        
        prompt = self.agent._create_chat_prompt(user_input, memory_context)
        
        assert user_input in prompt
        assert memory_context in prompt
        assert "CONFIGO" in prompt
    
    def test_create_scan_prompt(self):
        """Test scan prompt creation."""
        project_context = "Found: requirements.txt"
        deep = True
        
        prompt = self.agent._create_scan_prompt(project_context, deep)
        
        assert project_context in prompt
        assert "deep analysis" in prompt
        assert "JSON" in prompt
    
    def test_get_llm_response_with_client(self):
        """Test LLM response with client available."""
        prompt = "Test prompt"
        expected_response = "Test response"
        
        # Mock LLM client
        mock_client = Mock()
        mock_client.generate_content.return_value.text = expected_response
        self.agent.llm_client = mock_client
        
        response = self.agent._get_llm_response(prompt)
        assert response == expected_response
    
    def test_get_llm_response_fallback(self):
        """Test LLM response fallback."""
        prompt = "installation plan"
        
        # No LLM client
        self.agent.llm_client = None
        
        response = self.agent._get_llm_response(prompt)
        assert "Basic Development Environment" in response
    
    def test_get_fallback_response(self):
        """Test fallback response generation."""
        # Test installation plan fallback
        response = self.agent._get_fallback_response("installation plan")
        assert "Basic Development Environment" in response
        
        # Test quick install fallback
        response = self.agent._get_fallback_response("quick install")
        assert "Quick Install" in response
        
        # Test chat fallback
        response = self.agent._get_fallback_response("chat")
        assert "CONFIGO" in response
    
    def test_parse_plan_response(self):
        """Test plan response parsing."""
        response = '''
        {
            "name": "Test Plan",
            "description": "Test description",
            "steps": [
                {
                    "name": "Install Git",
                    "command": "sudo apt-get install git",
                    "tool_name": "git"
                }
            ]
        }
        '''
        
        plan = self.agent._parse_plan_response(response, "test environment")
        assert plan['name'] == "Test Plan"
        assert len(plan['steps']) == 1
        assert plan['steps'][0]['tool_name'] == "git"
    
    def test_parse_plan_response_invalid_json(self):
        """Test plan response parsing with invalid JSON."""
        response = "Invalid JSON response"
        
        plan = self.agent._parse_plan_response(response, "test environment")
        assert plan['name'] == "Basic Plan for test environment"
    
    def test_parse_quick_plan_response(self):
        """Test quick plan response parsing."""
        response = '''
        {
            "name": "Quick Install: git",
            "command": "sudo apt-get install git",
            "check_command": "git --version",
            "description": "Quick installation of git"
        }
        '''
        
        plan = self.agent._parse_quick_plan_response(response, "git")
        assert plan['name'] == "Quick Install: git"
        assert "sudo apt-get install git" in plan['command']
    
    def test_parse_scan_response(self):
        """Test scan response parsing."""
        response = '''
        {
            "tools": [
                {
                    "name": "python",
                    "type": "language",
                    "version": "3.11.0"
                }
            ],
            "missing_tools": [],
            "recommendations": ["Use virtual environment"]
        }
        '''
        
        results = self.agent._parse_scan_response(response)
        assert len(results['tools']) == 1
        assert results['tools'][0]['name'] == "python"
    
    def test_analyze_project_context(self):
        """Test project context analysis."""
        # Test basic analysis
        context = self.agent._analyze_project_context(deep=False)
        assert isinstance(context, str)
        
        # Test deep analysis
        context = self.agent._analyze_project_context(deep=True)
        assert isinstance(context, str)


if __name__ == '__main__':
    pytest.main([__file__]) 