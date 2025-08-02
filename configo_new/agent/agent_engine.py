"""
CONFIGO Agent Engine
====================

Core LLM-powered agent that handles intelligent planning, decision making,
and natural language interactions for CONFIGO.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentEngine:
    """
    Core agent engine for CONFIGO.
    
    Handles LLM interactions, planning, and intelligent decision making
    using memory and knowledge systems.
    """
    
    def __init__(self, memory_store, knowledge_engine):
        """Initialize the agent engine."""
        self.memory = memory_store
        self.knowledge = knowledge_engine
        self.llm_client = self._initialize_llm_client()
        
        logger.info("CONFIGO Agent Engine initialized")
    
    def _initialize_llm_client(self):
        """Initialize the LLM client (Gemini or fallback)."""
        try:
            import google.generativeai as genai
            from config import Config
            
            config = Config()
            api_key = config.get_api_key('gemini')
            
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini LLM client initialized")
                return model
            else:
                logger.warning("No Gemini API key found - using fallback responses")
                return None
        except ImportError:
            logger.warning("Google Generative AI not available - using fallback responses")
            return None
    
    def generate_installation_plan(self, environment_description: str, lite_mode: bool = False) -> Dict[str, Any]:
        """
        Generate an installation plan using LLM.
        
        Args:
            environment_description: User's environment description
            lite_mode: Whether to use lite mode
            
        Returns:
            Dict[str, Any]: Installation plan
        """
        logger.info(f"Generating installation plan for: {environment_description}")
        
        # Get memory context
        memory_context = self.memory.get_memory_context()
        
        # Get knowledge context
        knowledge_context = self._get_knowledge_context(environment_description)
        
        # Create prompt
        prompt = self._create_planning_prompt(environment_description, memory_context, knowledge_context, lite_mode)
        
        # Get LLM response
        response = self._get_llm_response(prompt)
        
        # Parse response
        plan = self._parse_plan_response(response, environment_description)
        
        # Store plan in knowledge base
        if self.knowledge:
            self.knowledge.add_installation_plan(f"plan_{environment_description.replace(' ', '_')}", plan)
        
        return plan
    
    def generate_quick_plan(self, tool_name: str) -> Dict[str, Any]:
        """
        Generate a quick installation plan for a single tool.
        
        Args:
            tool_name: Name of the tool to install
            
        Returns:
            Dict[str, Any]: Quick installation plan
        """
        logger.info(f"Generating quick plan for: {tool_name}")
        
        # Check memory for previous installations
        tool_memory = self.memory.get_tool_memory(tool_name)
        
        if tool_memory and tool_memory.install_success:
            # Use cached successful installation
            return {
                'name': f'Quick Install: {tool_name}',
                'command': tool_memory.install_command,
                'check_command': tool_memory.check_command,
                'description': f'Quick installation of {tool_name} using cached command'
            }
        
        # Generate new plan
        prompt = self._create_quick_plan_prompt(tool_name)
        response = self._get_llm_response(prompt)
        
        return self._parse_quick_plan_response(response, tool_name)
    
    def chat(self, user_input: str) -> str:
        """
        Handle chat interactions with the agent.
        
        Args:
            user_input: User's message
            
        Returns:
            str: Agent's response
        """
        logger.info(f"Processing chat input: {user_input}")
        
        # Get memory context
        memory_context = self.memory.get_memory_context()
        
        # Create chat prompt
        prompt = self._create_chat_prompt(user_input, memory_context)
        
        # Get LLM response
        response = self._get_llm_response(prompt)
        
        # Store in memory
        self.memory.save_to_memory(user_input, {'type': 'chat_input'})
        self.memory.save_to_memory(response, {'type': 'chat_response'})
        
        return response
    
    def scan_project(self, deep: bool = False) -> Dict[str, Any]:
        """
        Scan the current project for tools and technologies.
        
        Args:
            deep: Whether to perform deep scan
            
        Returns:
            Dict[str, Any]: Scan results
        """
        logger.info(f"Scanning project (deep: {deep})")
        
        # Get project context
        project_context = self._analyze_project_context(deep)
        
        # Create scan prompt
        prompt = self._create_scan_prompt(project_context, deep)
        
        # Get LLM response
        response = self._get_llm_response(prompt)
        
        # Parse scan results
        scan_results = self._parse_scan_response(response)
        
        return scan_results
    
    def get_available_portals(self) -> List[Dict[str, Any]]:
        """Get available login portals."""
        return [
            {
                'name': 'GitHub',
                'url': 'https://github.com',
                'description': 'Code hosting and collaboration'
            },
            {
                'name': 'GitLab',
                'url': 'https://gitlab.com',
                'description': 'Git repository management'
            },
            {
                'name': 'Docker Hub',
                'url': 'https://hub.docker.com',
                'description': 'Container registry'
            },
            {
                'name': 'PyPI',
                'url': 'https://pypi.org',
                'description': 'Python package index'
            },
            {
                'name': 'NPM',
                'url': 'https://www.npmjs.com',
                'description': 'Node.js package registry'
            }
        ]
    
    def launch_portals(self) -> None:
        """Launch relevant login portals."""
        import webbrowser
        
        portals = self.get_available_portals()
        
        for portal in portals:
            try:
                webbrowser.open(portal['url'])
                logger.info(f"Launched portal: {portal['name']}")
            except Exception as e:
                logger.error(f"Failed to launch portal {portal['name']}: {e}")
    
    def _get_knowledge_context(self, environment: str) -> str:
        """Get relevant knowledge context for planning."""
        if not self.knowledge:
            return ""
        
        try:
            # Search for similar environments
            similar_plans = self.knowledge.search_tools(f"{environment} development", 3)
            
            # Get recommended tools
            recommended_tools = self.knowledge.get_recommended_tools(environment.replace(' ', '_'))
            
            context_parts = []
            
            if similar_plans:
                context_parts.append("Similar environments found:")
                for plan in similar_plans:
                    context_parts.append(f"- {plan.get('name', 'Unknown')}: {plan.get('description', 'No description')}")
            
            if recommended_tools:
                context_parts.append("Recommended tools:")
                for tool in recommended_tools:
                    context_parts.append(f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            
            return "\n".join(context_parts) if context_parts else ""
        except Exception as e:
            logger.warning(f"Failed to get knowledge context: {e}")
            return ""
    
    def _create_planning_prompt(self, environment: str, memory_context: str, knowledge_context: str, lite_mode: bool) -> str:
                      """Create a prompt for installation planning."""
                      mode_text = "lite mode (minimal, essential tools only)" if lite_mode else "comprehensive mode"
                      
                      prompt = f"""
              You are CONFIGO, an intelligent development environment setup agent. Create an installation plan for the following environment:
              
              Environment: {environment}
              Mode: {mode_text}
              
              Previous installations and context:
              {memory_context}
              
              Knowledge base insights:
              {knowledge_context}
              
              Generate a JSON response with the following structure:
              {{
                  "name": "Plan name",
                  "description": "Plan description",
                  "steps": [
                      {{
                          "name": "Step name",
                          "command": "Installation command",
                          "description": "Step description",
                          "tool_name": "Tool name",
                          "is_extension": false,
                          "extension_id": null,
                          "dependencies": ["dependency1", "dependency2"],
                          "timeout": 300,
                          "priority": 1
                      }}
                  ]
              }}
              
              Focus on:
              - Essential tools for the environment
              - Proper installation order (dependencies first)
              - Platform-appropriate commands (Linux/Ubuntu)
              - Extensions and configurations
              - Validation commands
              
              Response (JSON only):
              """
                      return prompt
    
    def _create_quick_plan_prompt(self, tool_name: str) -> str:
        """Create a prompt for quick tool installation."""
        prompt = f"""
You are CONFIGO. Generate a quick installation command for {tool_name}.

Generate a JSON response with:
{{
    "name": "Quick Install: {tool_name}",
    "command": "Installation command for Linux/Ubuntu",
    "check_command": "Command to verify installation",
    "description": "Quick installation of {tool_name}"
}}

Focus on:
- Simple, reliable installation command
- Platform-appropriate (Linux/Ubuntu)
- Proper package manager usage
- Verification command

Response (JSON only):
"""
        return prompt
    
    def _create_chat_prompt(self, user_input: str, memory_context: str) -> str:
        """Create a prompt for chat interactions."""
        prompt = f"""
You are CONFIGO, an intelligent development environment setup agent. Help the user with their request.

User input: {user_input}

Previous context:
{memory_context}

Provide a helpful, informative response about development environment setup, tools, or CONFIGO features.
Be concise but thorough. If suggesting tools, mention installation commands.

Response:
"""
        return prompt
    
    def _create_scan_prompt(self, project_context: str, deep: bool) -> str:
        """Create a prompt for project scanning."""
        scan_type = "deep analysis" if deep else "basic analysis"
        
        prompt = f"""
You are CONFIGO. Analyze the following project context and identify tools, technologies, and recommendations.

Project context:
{project_context}

Scan type: {scan_type}

Generate a JSON response with:
{{
    "tools": [
        {{
            "name": "Tool name",
            "type": "language|framework|tool|database|service",
            "version": "Detected version",
            "confidence": 0.95,
            "recommendations": ["recommendation1", "recommendation2"]
        }}
    ],
    "missing_tools": [
        {{
            "name": "Tool name",
            "reason": "Why it's needed",
            "priority": "high|medium|low"
        }}
    ],
    "recommendations": ["recommendation1", "recommendation2"]
}}

Response (JSON only):
"""
        return prompt
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM or fallback."""
        if self.llm_client:
            try:
                response = self.llm_client.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"LLM request failed: {e}")
                return self._get_fallback_response(prompt)
        else:
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Get fallback response when LLM is not available."""
        if "installation plan" in prompt.lower():
            return self._get_fallback_plan()
        elif "quick install" in prompt.lower():
            return self._get_fallback_quick_plan()
        elif "chat" in prompt.lower():
            return "I'm CONFIGO, your development environment setup assistant. I can help you install tools, set up environments, and provide guidance. What would you like to do?"
        else:
            return "I'm here to help with development environment setup. Please try again or use a specific command."
    
    def _get_fallback_plan(self) -> str:
        """Get fallback installation plan."""
        return '''
{
    "name": "Basic Development Environment",
    "description": "Standard development environment setup",
    "steps": [
        {
            "name": "Install Git",
            "command": "sudo apt-get update && sudo apt-get install -y git",
            "description": "Install Git version control",
            "tool_name": "git",
            "is_extension": false,
            "extension_id": null,
            "dependencies": [],
            "timeout": 300,
            "priority": 1
        },
        {
            "name": "Install Python",
            "command": "sudo apt-get install -y python3 python3-pip",
            "description": "Install Python and pip",
            "tool_name": "python",
            "is_extension": false,
            "extension_id": null,
            "dependencies": [],
            "timeout": 300,
            "priority": 2
        }
    ]
}
'''
    
    def _get_fallback_quick_plan(self) -> str:
        """Get fallback quick installation plan."""
        return '''
{
    "name": "Quick Install",
    "command": "sudo apt-get install -y tool_name",
    "check_command": "tool_name --version",
    "description": "Quick installation"
}
'''
    
    def _parse_plan_response(self, response: str, environment: str) -> Dict[str, Any]:
        """Parse LLM response into installation plan."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                plan = json.loads(json_str)
                return plan
            else:
                logger.warning("No JSON found in LLM response")
                return self._get_fallback_plan_dict(environment)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_fallback_plan_dict(environment)
    
    def _parse_quick_plan_response(self, response: str, tool_name: str) -> Dict[str, Any]:
        """Parse LLM response into quick installation plan."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                plan = json.loads(json_str)
                return plan
            else:
                return {
                    'name': f'Quick Install: {tool_name}',
                    'command': f'sudo apt-get install -y {tool_name}',
                    'check_command': f'{tool_name} --version',
                    'description': f'Quick installation of {tool_name}'
                }
        except json.JSONDecodeError:
            return {
                'name': f'Quick Install: {tool_name}',
                'command': f'sudo apt-get install -y {tool_name}',
                'check_command': f'{tool_name} --version',
                'description': f'Quick installation of {tool_name}'
            }
    
    def _parse_scan_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into scan results."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                results = json.loads(json_str)
                return results
            else:
                return {
                    'tools': [],
                    'missing_tools': [],
                    'recommendations': ['Run a deep scan for more detailed analysis']
                }
        except json.JSONDecodeError:
            return {
                'tools': [],
                'missing_tools': [],
                'recommendations': ['Run a deep scan for more detailed analysis']
            }
    
    def _get_fallback_plan_dict(self, environment: str) -> Dict[str, Any]:
        """Get fallback plan as dictionary."""
        return {
            'name': f'Basic Plan for {environment}',
            'description': f'Basic installation plan for {environment}',
            'steps': [
                {
                    'name': 'Install Git',
                    'command': 'sudo apt-get update && sudo apt-get install -y git',
                    'description': 'Install Git version control',
                    'tool_name': 'git',
                    'is_extension': False,
                    'extension_id': None,
                    'dependencies': [],
                    'timeout': 300,
                    'priority': 1
                }
            ]
        }
    
    def _analyze_project_context(self, deep: bool) -> str:
        """Analyze the current project context."""
        import os
        import subprocess
        
        context = []
        
        # Check for common project files
        project_files = [
            'package.json', 'requirements.txt', 'pom.xml', 'build.gradle',
            'Cargo.toml', 'go.mod', 'Dockerfile', '.gitignore'
        ]
        
        for file in project_files:
            if os.path.exists(file):
                context.append(f"Found: {file}")
        
        # Check for Git repository
        try:
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                context.append("Git repository detected")
        except FileNotFoundError:
            pass
        
        # Deep analysis
        if deep:
            # Check for specific technologies
            tech_checks = [
                ('node', 'node --version'),
                ('python', 'python --version'),
                ('java', 'java -version'),
                ('docker', 'docker --version')
            ]
            
            for tech, cmd in tech_checks:
                try:
                    result = subprocess.run(cmd.split(), capture_output=True, text=True)
                    if result.returncode == 0:
                        context.append(f"{tech}: {result.stdout.strip()}")
                except FileNotFoundError:
                    pass
        
        return "\n".join(context) if context else "No specific project context detected" 