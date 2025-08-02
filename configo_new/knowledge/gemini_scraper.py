"""
CONFIGO Gemini Intelligence Scraper
==================================

Uses Google Gemini API to autonomously gather real-time information
about developer tools, installation methods, and error fixes.
"""

import logging
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class GeminiScraper:
    """
    Gemini-powered intelligence scraper for CONFIGO.
    
    Uses Google Gemini API to gather real-time information about:
    - Developer tools and their latest versions
    - Installation methods and best practices
    - Common errors and their fixes
    - Tool relationships and dependencies
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini scraper."""
        self.api_key = api_key
        self.client = None
        self.connected = False
        
        self._initialize_gemini_client()
        logger.info("CONFIGO Gemini Scraper initialized")
    
    def _initialize_gemini_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-pro')
                self.connected = True
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("No Gemini API key provided - scraper will be disabled")
                self.connected = False
        except ImportError:
            logger.warning("Google Generative AI not available - scraper will be disabled")
            self.connected = False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.connected = False
    
    def search_tools_for_domain(self, domain: str) -> Dict[str, Any]:
        """
        Search for tools commonly used in a specific domain.
        
        Args:
            domain: Development domain (e.g., 'full stack ai', 'web development')
            
        Returns:
            Dict[str, Any]: Tools and their information
        """
        if not self.connected:
            return self._get_fallback_tools(domain)
        
        try:
            prompt = f"""
            Search for the most popular and essential developer tools for {domain} development.
            
            Return a JSON response with this structure:
            {{
                "domain": "{domain}",
                "tools": [
                    {{
                        "name": "tool_name",
                        "description": "What this tool does",
                        "category": "language|framework|tool|database|service",
                        "official_install_command": "Installation command for Ubuntu/Linux",
                        "version_check_command": "Command to check if installed",
                        "common_errors": [
                            {{
                                "error": "Error message",
                                "fix": "How to fix it"
                            }}
                        ],
                        "dependencies": ["dependency1", "dependency2"],
                        "related_tools": ["related_tool1", "related_tool2"]
                    }}
                ],
                "recommended_stack": [
                    "essential_tool1",
                    "essential_tool2"
                ]
            }}
            
            Focus on:
            - Current, popular tools (2024-2025)
            - Official installation methods
            - Common Ubuntu/Linux installation issues
            - Tool relationships and dependencies
            """
            
            response = self._get_gemini_response(prompt)
            return self._parse_tools_response(response, domain)
            
        except Exception as e:
            logger.error(f"Failed to search tools for domain {domain}: {e}")
            return self._get_fallback_tools(domain)
    
    def search_error_fix(self, error_message: str, tool_name: str = None) -> Dict[str, Any]:
        """
        Search for fixes for a specific error.
        
        Args:
            error_message: The error message
            tool_name: Name of the tool (optional)
            
        Returns:
            Dict[str, Any]: Error fix information
        """
        if not self.connected:
            return self._get_fallback_error_fix(error_message)
        
        try:
            context = f" for {tool_name}" if tool_name else ""
            prompt = f"""
            Search for how to fix this error{context}:
            "{error_message}"
            
            Return a JSON response with this structure:
            {{
                "error": "{error_message}",
                "tool": "{tool_name or 'unknown'}",
                "root_cause": "What causes this error",
                "fixes": [
                    {{
                        "description": "Fix description",
                        "command": "Command to run",
                        "explanation": "Why this works"
                    }}
                ],
                "prevention": "How to prevent this error in the future",
                "related_errors": [
                    "similar_error1",
                    "similar_error2"
                ]
            }}
            
            Focus on:
            - Linux/Ubuntu specific solutions
            - Step-by-step fix commands
            - Root cause analysis
            - Prevention strategies
            """
            
            response = self._get_gemini_response(prompt)
            return self._parse_error_response(response, error_message)
            
        except Exception as e:
            logger.error(f"Failed to search error fix: {e}")
            return self._get_fallback_error_fix(error_message)
    
    def search_installation_method(self, tool_name: str) -> Dict[str, Any]:
        """
        Search for the best installation method for a tool.
        
        Args:
            tool_name: Name of the tool to install
            
        Returns:
            Dict[str, Any]: Installation information
        """
        if not self.connected:
            return self._get_fallback_installation(tool_name)
        
        try:
            prompt = f"""
            Search for the best way to install {tool_name} on Ubuntu/Linux.
            
            Return a JSON response with this structure:
            {{
                "tool": "{tool_name}",
                "installation_methods": [
                    {{
                        "method": "package_manager|source|docker|snap",
                        "description": "Method description",
                        "command": "Installation command",
                        "check_command": "Command to verify installation",
                        "pros": ["advantage1", "advantage2"],
                        "cons": ["disadvantage1", "disadvantage2"]
                    }}
                ],
                "recommended_method": "package_manager",
                "dependencies": ["dependency1", "dependency2"],
                "post_install_steps": [
                    "step1",
                    "step2"
                ],
                "common_issues": [
                    {{
                        "issue": "Common problem",
                        "solution": "How to solve it"
                    }}
                ]
            }}
            
            Focus on:
            - Official installation methods
            - Ubuntu/Linux compatibility
            - Latest stable versions
            - Common installation issues
            """
            
            response = self._get_gemini_response(prompt)
            return self._parse_installation_response(response, tool_name)
            
        except Exception as e:
            logger.error(f"Failed to search installation method for {tool_name}: {e}")
            return self._get_fallback_installation(tool_name)
    
    def search_tool_relationships(self, tool_name: str) -> Dict[str, Any]:
        """
        Search for tools that are commonly used with a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dict[str, Any]: Tool relationships
        """
        if not self.connected:
            return self._get_fallback_relationships(tool_name)
        
        try:
            prompt = f"""
            Search for tools that are commonly used with {tool_name}.
            
            Return a JSON response with this structure:
            {{
                "tool": "{tool_name}",
                "relationships": [
                    {{
                        "related_tool": "tool_name",
                        "relationship_type": "dependency|complementary|alternative",
                        "description": "How they work together",
                        "use_case": "When to use them together"
                    }}
                ],
                "ecosystem": [
                    "tool1",
                    "tool2"
                ],
                "common_stacks": [
                    {{
                        "name": "stack_name",
                        "tools": ["tool1", "tool2"],
                        "description": "What this stack is used for"
                    }}
                ]
            }}
            
            Focus on:
            - Current development practices (2024-2025)
            - Real-world usage patterns
            - Tool compatibility
            - Popular development stacks
            """
            
            response = self._get_gemini_response(prompt)
            return self._parse_relationships_response(response, tool_name)
            
        except Exception as e:
            logger.error(f"Failed to search relationships for {tool_name}: {e}")
            return self._get_fallback_relationships(tool_name)
    
    def _get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini API."""
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return ""
    
    def _parse_tools_response(self, response: str, domain: str) -> Dict[str, Any]:
        """Parse Gemini response for tools search."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._get_fallback_tools(domain)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tools response: {e}")
            return self._get_fallback_tools(domain)
    
    def _parse_error_response(self, response: str, error_message: str) -> Dict[str, Any]:
        """Parse Gemini response for error fix search."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._get_fallback_error_fix(error_message)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse error response: {e}")
            return self._get_fallback_error_fix(error_message)
    
    def _parse_installation_response(self, response: str, tool_name: str) -> Dict[str, Any]:
        """Parse Gemini response for installation search."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._get_fallback_installation(tool_name)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse installation response: {e}")
            return self._get_fallback_installation(tool_name)
    
    def _parse_relationships_response(self, response: str, tool_name: str) -> Dict[str, Any]:
        """Parse Gemini response for relationships search."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._get_fallback_relationships(tool_name)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse relationships response: {e}")
            return self._get_fallback_relationships(tool_name)
    
    def _get_fallback_tools(self, domain: str) -> Dict[str, Any]:
        """Get fallback tools when Gemini is not available."""
        fallback_tools = {
            'full stack ai': {
                'domain': domain,
                'tools': [
                    {
                        'name': 'python',
                        'description': 'Programming language for AI development',
                        'category': 'language',
                        'official_install_command': 'sudo apt-get install python3 python3-pip',
                        'version_check_command': 'python3 --version',
                        'common_errors': [],
                        'dependencies': [],
                        'related_tools': ['pip', 'jupyter', 'tensorflow']
                    },
                    {
                        'name': 'docker',
                        'description': 'Container platform for AI development',
                        'category': 'tool',
                        'official_install_command': 'sudo apt-get install docker.io',
                        'version_check_command': 'docker --version',
                        'common_errors': [],
                        'dependencies': [],
                        'related_tools': ['docker-compose', 'kubernetes']
                    }
                ],
                'recommended_stack': ['python', 'docker', 'git']
            }
        }
        
        return fallback_tools.get(domain, {
            'domain': domain,
            'tools': [],
            'recommended_stack': []
        })
    
    def _get_fallback_error_fix(self, error_message: str) -> Dict[str, Any]:
        """Get fallback error fix when Gemini is not available."""
        return {
            'error': error_message,
            'tool': 'unknown',
            'root_cause': 'Unknown',
            'fixes': [
                {
                    'description': 'Check system requirements',
                    'command': 'echo "Check system requirements"',
                    'explanation': 'Verify that all dependencies are installed'
                }
            ],
            'prevention': 'Install dependencies before installing tools',
            'related_errors': []
        }
    
    def _get_fallback_installation(self, tool_name: str) -> Dict[str, Any]:
        """Get fallback installation method when Gemini is not available."""
        return {
            'tool': tool_name,
            'installation_methods': [
                {
                    'method': 'package_manager',
                    'description': f'Install {tool_name} using package manager',
                    'command': f'sudo apt-get install {tool_name}',
                    'check_command': f'{tool_name} --version',
                    'pros': ['Simple', 'Official'],
                    'cons': ['May not be latest version']
                }
            ],
            'recommended_method': 'package_manager',
            'dependencies': [],
            'post_install_steps': [],
            'common_issues': []
        }
    
    def _get_fallback_relationships(self, tool_name: str) -> Dict[str, Any]:
        """Get fallback relationships when Gemini is not available."""
        return {
            'tool': tool_name,
            'relationships': [],
            'ecosystem': [],
            'common_stacks': []
        }
    
    def is_connected(self) -> bool:
        """Check if Gemini is connected."""
        return self.connected
    
    def get_status(self) -> Dict[str, Any]:
        """Get scraper status."""
        return {
            'connected': self.connected,
            'api_key_configured': bool(self.api_key),
            'client_initialized': bool(self.client)
        } 