"""
File: core/ai.py
Purpose: Handles the core LLM logic for stack recommendations and reasoning.
Maintainer: Kishore Kumar S
Description: Provides AI-powered tool recommendations, chat functionality, and YAML parsing
             for the CONFIGO development environment setup agent.
"""

import yaml
import logging
import os
import time
import requests
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Log API key status for debugging
api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
if api_key and api_key != "your_gemini_api_key_here":
    logger.info(f"API key found: {api_key[:10]}...")
else:
    logger.warning("No valid API key found in .env file - LLM features will be limited")
    logger.warning("Please set GEMINI_API_KEY in your .env file to enable AI features")


@dataclass
class Tool:
    """
    Tool configuration dataclass.
    
    Represents a development tool with installation and validation commands.
    """
    name: str
    install_command: str
    check_command: str
    is_extension: bool = False
    extension_id: str = ""


@dataclass
class LoginPortal:
    """
    Login portal configuration dataclass.
    
    Represents a web portal that users need to log into for development services.
    """
    name: str
    url: str
    description: str = ""


class LLMClient:
    """
    Enhanced LLM client for Gemini API integration with proper validation.
    
    This class handles all communication with Google's Gemini API, including
    error handling, fallback responses, and proper authentication.
    """
    
    # System prompts for different modes
    CHAT_AGENT_PROMPT = """
You are CONFIGO — a smart, helpful AI assistant that helps developers set up their environments, fix errors, install tools, and troubleshoot issues.

Your personality:
- Friendly, helpful, and concise
- You have a personality — you are encouraging, supportive, and always stay helpful
- Use emojis naturally but sparingly
- Be conversational and engaging
- Show enthusiasm for helping developers

Your capabilities:
- Help with tool installation and setup
- Explain development concepts and tools
- Suggest appropriate tools for projects
- Help troubleshoot errors and issues
- Provide guidance on best practices
- Answer questions about yourself and your capabilities

You can answer questions like:
• "Who are you?"
• "Where are you?"
• "How do I install Python?"
• "What is Docker?"
• "What can you do?"

Your goal is to act like a real-time assistant — respond naturally to any question, provide helpful information, and NEVER show raw YAML or code unless the user explicitly asks for it.

Keep responses conversational, helpful, and focused on the user's needs. You're running right here in their terminal, ready to help!
"""
    
    def __init__(self):
        """
        Initialize the LLM client with API configuration.
        
        Sets up API key, URL, model, and timeout settings.
        Validates the API key and logs initialization status.
        """
        # Try GEMINI_API_KEY first, then fallback to GOOGLE_API_KEY
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.api_url = os.getenv('GEMINI_API_URL', "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent")
        self.model = os.getenv('GEMINI_MODEL', "gemini-2.0-flash-exp")
        self.timeout = int(os.getenv('LLM_TIMEOUT', 30))
        
        # Validate API key
        self._validate_api_key()
        
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            logger.info(f"LLMClient initialized with model: {self.model}")
            logger.info(f"API key found: {self.api_key[:10]}...")
        else:
            logger.error("No valid API key found - LLM features will be limited")
            logger.error("Please set GEMINI_API_KEY in your .env file")
    
    def _validate_api_key(self) -> bool:
        """
        Validate that we have a proper API key.
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.error("Invalid or missing GEMINI_API_KEY")
            logger.error("Please get your API key from: https://makersuite.google.com/app/apikey")
            logger.error("Then add it to your .env file as: GEMINI_API_KEY=your_actual_key")
            return False
        return True
    
    def generate_config(self, prompt: str) -> str:
        """
        Generate configuration using Gemini API.
        
        Args:
            prompt: The prompt to send to the Gemini API
            
        Returns:
            str: Generated configuration or fallback response
        """
        if not self._validate_api_key():
            logger.error("Cannot generate config without valid API key")
            return self._get_fallback_response()
        
        try:
            logger.info("Calling Gemini API for configuration generation...")
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    response_text = result['candidates'][0]['content']['parts'][0]['text']
                    logger.info("Successfully received response from Gemini API")
                    return response_text
                else:
                    logger.error("Unexpected response format from Gemini API")
                    logger.error(f"Response: {result}")
                    return self._get_fallback_response()
            elif response.status_code == 503:
                logger.warning("Gemini API is currently overloaded (503 error)")
                logger.warning("This is a temporary issue with Google's servers, not your API key")
                logger.warning("Using fallback response for now - try again later for AI-powered recommendations")
                return self._get_fallback_response()
            elif response.status_code == 429:
                logger.warning("Gemini API rate limit exceeded (429 error)")
                logger.warning("Too many requests - using fallback response")
                return self._get_fallback_response()
            elif response.status_code == 401:
                logger.error("Gemini API authentication failed (401 error)")
                logger.error("Please check your GEMINI_API_KEY is correct")
                return self._get_fallback_response()
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._get_fallback_response()
                
        except requests.exceptions.Timeout:
            logger.warning("Gemini API request timed out")
            logger.warning("Using fallback response - try again later")
            return self._get_fallback_response()
        except requests.exceptions.ConnectionError:
            logger.warning("Gemini API connection error")
            logger.warning("Check your internet connection - using fallback response")
            return self._get_fallback_response()
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._get_fallback_response()
    
    def chat_response(self, user_input: str, memory_context: str = "", chat_context: str = "") -> str:
        """
        Generate a chat response using the chat system prompt.
        
        Args:
            user_input: The user's input message
            memory_context: Optional memory context to include
            chat_context: Optional chat history context
            
        Returns:
            str: Generated chat response or fallback response
        """
        if not self._validate_api_key():
            logger.error("Cannot generate chat response without valid API key")
            return self._get_fallback_chat_response(user_input)
        
        try:
            logger.info("Calling Gemini API for chat response...")
            
            # Create the full prompt with system prompt and context
            full_prompt = f"{self.CHAT_AGENT_PROMPT}\n\n"
            
            if memory_context:
                full_prompt += f"Memory Context:\n{memory_context}\n\n"
            
            if chat_context:
                full_prompt += f"Recent Chat History:\n{chat_context}\n"
            
            full_prompt += f"User: {user_input}\n\nCONFIGO:"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }]
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    response_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    logger.info("Successfully received chat response from Gemini API")
                    return response_text
                else:
                    logger.error("Unexpected response format from Gemini API")
                    logger.error(f"Response: {result}")
                    return self._get_fallback_chat_response(user_input)
            elif response.status_code == 503:
                logger.warning("Gemini API is currently overloaded (503 error)")
                logger.warning("This is a temporary issue with Google's servers, not your API key")
                logger.warning("Using fallback response for now - try again later for AI-powered chat")
                return self._get_fallback_chat_response(user_input)
            elif response.status_code == 429:
                logger.warning("Gemini API rate limit exceeded (429 error)")
                logger.warning("Too many requests - using fallback response")
                return self._get_fallback_chat_response(user_input)
            elif response.status_code == 401:
                logger.error("Gemini API authentication failed (401 error)")
                logger.error("Please check your GEMINI_API_KEY is correct")
                return self._get_fallback_chat_response(user_input)
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._get_fallback_chat_response(user_input)
                
        except requests.exceptions.Timeout:
            logger.warning("Gemini API request timed out")
            logger.warning("Using fallback response - try again later")
            return self._get_fallback_chat_response(user_input)
        except requests.exceptions.ConnectionError:
            logger.warning("Gemini API connection error")
            logger.warning("Check your internet connection - using fallback response")
            return self._get_fallback_chat_response(user_input)
        except Exception as e:
            logger.error(f"Error calling Gemini API for chat: {e}")
            return self._get_fallback_chat_response(user_input)
    
    def _get_fallback_chat_response(self, user_input: str) -> str:
        """
        Return a fallback chat response with dynamic, conversational replies.
        
        Args:
            user_input: The user's input message
            
        Returns:
            str: A conversational fallback response
        """
        user_input_lower = user_input.lower()
        
        # Handle common identity questions with personality
        if any(phrase in user_input_lower for phrase in ["who are you", "what are you", "your name", "what's your name"]):
            return "I'm CONFIGO — your intelligent environment setup agent! 🤖 I help you install tools, configure your stack, and solve dev issues using AI. Think of me as your personal DevOps assistant running right here in your terminal!"
        
        elif any(phrase in user_input_lower for phrase in ["where are you", "where do you live", "where do you run"]):
            return "I'm running right here in your terminal, always ready to help with your setup! 🖥️ I'm your local AI assistant, so I can directly interact with your system and help you get things done."
        
        elif any(phrase in user_input_lower for phrase in ["what do you do", "what can you do", "help me", "capabilities", "what are your features"]):
            return "I'm your development environment wizard! 🧙‍♂️ I can install tools, fix errors, suggest tech stacks, scan your projects, and even help you log into development portals. Just tell me what you're working on and I'll guide you through it!"
        
        elif any(phrase in user_input_lower for phrase in ["hello", "hi", "hey", "greetings"]):
            return "Hello there! 👋 I'm CONFIGO, your development assistant. I'm excited to help you set up your environment and get coding! What would you like to work on today?"
        
        elif "install" in user_input_lower:
            return "Absolutely! I love helping with installations! 🛠️ Just tell me what you need — like 'Install Python', 'Install Docker', or 'Install VS Code'. I'll handle the setup and make sure everything works perfectly."
        
        elif "error" in user_input_lower or "problem" in user_input_lower or "issue" in user_input_lower:
            return "I'm here to help troubleshoot! 🔧 Describe the error or problem you're facing, and I'll analyze it and suggest solutions. I can even try to fix things automatically!"
        
        elif "git" in user_input_lower:
            return "Git is a version control system that helps you track changes in your code! 📝 Want me to check if it's installed on your system, or help you set it up?"
        
        elif "python" in user_input_lower:
            return "Python is a powerful programming language! 🐍 I can help you install it, check your version, or explain how to use it. What would you like to know about Python?"
        
        elif "docker" in user_input_lower:
            return "Docker is a containerization platform that makes it easy to package and run applications! 🐳 I can help you install Docker, explain how it works, or help you get started with containers."
        
        elif "thank" in user_input_lower or "thanks" in user_input_lower:
            return "You're very welcome! 😊 I'm here to make your development setup as smooth as possible. Don't hesitate to ask if you need anything else!"
        
        elif "bye" in user_input_lower or "goodbye" in user_input_lower or "exit" in user_input_lower:
            return "Goodbye! 👋 It was great helping you today. Come back anytime you need assistance with your development setup!"
        
        else:
            return "I'm CONFIGO, your intelligent development assistant! 🚀 I can help with tool installation, environment setup, error troubleshooting, tech stack recommendations, and much more. What would you like to work on today?"
    
    def _get_fallback_response(self) -> str:
        """
        Return a fallback YAML configuration.
        
        Returns:
            str: A basic YAML configuration for common development tools
        """
        return """
base_tools:
  - name: "Git"
    install_command: "sudo apt-get update && sudo apt-get install -y git"
    check_command: "git --version"
  - name: "Python 3"
    install_command: "sudo apt-get update && sudo apt-get install -y python3 python3-pip"
    check_command: "python3 --version"

editor:
  - name: "VS Code"
    install_command: "sudo snap install code --classic"
    check_command: "code --version"

extensions:
  - name: "Python Extension"
    type: "vscode-extension"
    id: "ms-python.python"

login_portals:
  - name: "GitHub"
    url: "https://github.com"
    description: "Version control and collaboration"
"""


def suggest_stack(env: str, stack_info: Optional[str] = None, message_display=None, debug: bool = False, ui=None) -> Tuple[List[Dict[str, str]], List[Any]]:
    """
    Generate a tech stack suggestion using enhanced LLM agent based on environment description.
    
    Args:
        env: Environment description from user input
        stack_info: Optional project scan information
        message_display: Optional MessageDisplay instance for user-friendly output
        debug: Enable debug mode for detailed logging
        ui: Optional UI instance for progress display
        
    Returns:
        Tuple[List[Dict[str, str]], List[Any]]: List of tools and login portals
    """
    try:
        # Initialize memory and enhanced LLM agent
        from core.memory import AgentMemory
        from core.enhanced_llm_agent import EnhancedLLMAgent
        
        memory = AgentMemory()
        llm_agent = EnhancedLLMAgent(memory)
        
        # Log to file only, not console
        logger.info(f"Querying enhanced LLM agent for tech stack: {env}")
        
        # Show user-friendly message if message_display is provided
        if message_display:
            message_display.show_ai_query_start(env)
        
        # Show enhanced UI for LLM API call if available
        if ui:
            from rich.live import Live
            progress = ui.show_llm_api_call("Generating AI-powered stack recommendations...")
            with Live(progress, console=ui.console, refresh_per_second=10):
                # Simulate progress for better UX
                for i in range(100):
                    progress.update(0, completed=i)
                    time.sleep(0.02)  # Quick animation
        
        # Generate enhanced stack using the enhanced LLM agent
        llm_response = llm_agent.generate_enhanced_stack(env, str(stack_info) if stack_info else "", debug=debug)
        
        # Convert enhanced response to the format expected by the UI
        tool_list = []
        for tool in llm_response.tools:
            tool_dict = {
                'name': tool.name,
                'status': '⬇️ To be installed',
                'detect_cmd': tool.check_command
            }
            tool_list.append(tool_dict)
        
        # Convert login portals to the expected format
        login_portals = []
        for portal in llm_response.login_portals:
            login_portals.append({
                'name': portal['name'],
                'url': portal['url'],
                'description': portal['description']
            })
        
        # Log to file only
        logger.info(f"Enhanced stack received: {len(llm_response.tools)} components")
        logger.info(f"Confidence score: {llm_response.confidence_score}")
        logger.info(f"Domain completion: {llm_response.domain_completion}")
        
        # Show user-friendly success message
        if message_display:
            message_display.show_ai_query_success(len(llm_response.tools), len(login_portals))
        
        # Warn if <3 tools or only base tools
        tool_names = [t['name'].lower() for t in tool_list]
        base_tools = set(["python", "python 3", "git"])
        only_base = set(tool_names).issubset(base_tools)
        if len(tool_list) < 3 or only_base:
            print("\n⚠️  Warning: Incomplete stack generated. Using fallback knowledge.\n")
        
        return tool_list, login_portals
        
    except Exception as e:
        logger.error(f"Failed to generate enhanced stack: {e}")
        
        # Show user-friendly fallback message
        if message_display:
            message_display.show_ai_query_fallback()
        
        # Fallback to domain-specific tools based on environment
        logger.info("Using fallback tools due to enhanced LLM error")
        tools, login_portals = add_missing_recommendations([], [], env)
        
        # Convert to the format expected by the UI
        tool_list = []
        for tool in tools:
            tool_dict = {
                'name': tool.name,
                'status': '⬇️ To be installed',
                'detect_cmd': tool.check_command
            }
            tool_list.append(tool_dict)
        
        return tool_list, login_portals


def parse_llm_config(yaml_config: str, environment: str = "") -> Tuple[List[Tool], List[LoginPortal]]:
    """
    Parse the YAML configuration returned by the LLM and validate completeness.
    
    Args:
        yaml_config: YAML string from LLM
        environment: Original environment description for validation
        
    Returns:
        Tuple[List[Tool], List[LoginPortal]]: Parsed tools and login portals
    """
    try:
        config = yaml.safe_load(yaml_config)
        tools = []
        login_portals = []
        
        if not config:
            logger.warning("Empty config received from LLM")
            return [], []
        
        # Parse base tools
        if isinstance(config, dict):
            # Parse base_tools
            base_tools = config.get('base_tools', [])
            for item in base_tools:
                if isinstance(item, dict):
                    name = item.get('name', 'Unknown Tool')
                    install_command = item.get('install_command', '')
                    check_command = item.get('check_command', name.lower())
                    
                    tool = Tool(
                        name=name,
                        install_command=install_command,
                        check_command=check_command
                    )
                    tools.append(tool)
            
            # Parse editor
            editor = config.get('editor', [])
            if isinstance(editor, list):
                for item in editor:
                    if isinstance(item, dict):
                        name = item.get('name', 'Unknown Editor')
                        install_command = item.get('install_command', '')
                        check_command = item.get('check_command', name.lower())
                        
                        tool = Tool(
                            name=name,
                            install_command=install_command,
                            check_command=check_command
                        )
                        tools.append(tool)
            
            # Parse extensions
            extensions = config.get('extensions', [])
            for item in extensions:
                if isinstance(item, dict):
                    name = item.get('name', 'Unknown Extension')
                    extension_id = item.get('id', '')
                    
                    tool = Tool(
                        name=name,
                        install_command="",
                        check_command='code',
                        is_extension=True,
                        extension_id=extension_id
                    )
                    tools.append(tool)
            
            # Parse CLI tools
            cli_tools = config.get('cli_tools', [])
            for item in cli_tools:
                if isinstance(item, dict):
                    name = item.get('name', 'Unknown CLI Tool')
                    install_command = item.get('install_command', '')
                    check_command = item.get('check_command', name.lower())
                    
                    tool = Tool(
                        name=name,
                        install_command=install_command,
                        check_command=check_command
                    )
                    tools.append(tool)
            
            # Parse login portals
            portals = config.get('login_portals', [])
            for portal in portals:
                if isinstance(portal, dict):
                    login_portal = LoginPortal(
                        name=portal.get('name', 'Unknown Portal'),
                        url=portal.get('url', ''),
                        description=portal.get('description', '')
                    )
                    login_portals.append(login_portal)
        
        # Handle legacy list format
        elif isinstance(config, list):
            for item in config:
                if not isinstance(item, dict):
                    continue
                    
                name = item.get('name', 'Unknown Tool')
                install_command = item.get('install_command', '')
                check_command = item.get('check_command', name.lower())
                
                # Handle VS Code extensions
                if item.get('type') == 'vscode-extension':
                    extension_id = item.get('id', '')
                    tool = Tool(
                        name=name,
                        install_command=install_command,
                        check_command='code',
                        is_extension=True,
                        extension_id=extension_id
                    )
                else:
                    tool = Tool(
                        name=name,
                        install_command=install_command,
                        check_command=check_command
                    )
                
                tools.append(tool)
        
        # Post-validation: Add missing recommendations based on environment
        tools, login_portals = add_missing_recommendations(tools, login_portals, environment)
        
        logger.info(f"Parsed {len(tools)} tools and {len(login_portals)} login portals")
        return tools, login_portals
        
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML config: {e}")
        logger.error(f"Raw YAML: {yaml_config}")
        # Try to extract valid YAML from the response
        try:
            # Look for YAML content between ```yaml and ``` markers
            yaml_match = re.search(r'```yaml\s*(.*?)\s*```', yaml_config, re.DOTALL)
            if yaml_match:
                cleaned_yaml = yaml_match.group(1)
                logger.info("Attempting to parse cleaned YAML")
                config = yaml.safe_load(cleaned_yaml)
                # Process the cleaned config...
                tools, login_portals = add_missing_recommendations([], [], environment)
                return tools, login_portals
        except Exception as cleanup_error:
            logger.error(f"Failed to clean YAML: {cleanup_error}")
        
        # Fallback: return basic tools based on environment
        logger.info("Using fallback tools due to YAML parsing error")
        tools, login_portals = add_missing_recommendations([], [], environment)
        return tools, login_portals
    except Exception as e:
        logger.error(f"Error parsing LLM config: {e}")
        return [], []


def add_missing_recommendations(tools: List[Tool], login_portals: List[LoginPortal], environment: str) -> Tuple[List[Tool], List[LoginPortal]]:
    """
    Add missing recommendations based on the environment type.
    
    Args:
        tools: Current list of tools
        login_portals: Current list of login portals
        environment: Environment description
        
    Returns:
        Tuple[List[Tool], List[LoginPortal]]: Enhanced tools and login portals
    """
    env_lower = environment.lower()
    
    # AI/ML Environment recommendations
    if any(keyword in env_lower for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'full stack ai']):
        logger.info("Adding AI/ML environment recommendations")
        
        # Check if Cursor is included as editor
        cursor_included = any(tool.name.lower() == 'cursor' for tool in tools)
        if not cursor_included:
            tools.append(Tool(
                name="Cursor Editor",
                install_command="curl -L https://download.cursor.sh/linux/appImage/x64/cursor-latest.AppImage -o cursor && chmod +x cursor && sudo mv cursor /usr/local/bin/",
                check_command="cursor"
            ))
        
        # Add missing AI extensions
        ai_extensions = [
            ("GitHub Copilot", "github.copilot"),
            ("Gemini Code Assist", "google.gemini-code-assist"),
            ("RoCode", "rocode.rocode"),
            ("Cline", "cline.cline"),
            ("Augment", "augment.augment"),
            ("KiloCode", "kilocode.kilocode")
        ]
        
        existing_extensions = [tool.name.lower() for tool in tools if tool.is_extension]
        for ext_name, ext_id in ai_extensions:
            if not any(ext_name.lower() in existing for existing in existing_extensions):
                tools.append(Tool(
                    name=ext_name,
                    install_command="",
                    check_command="code",
                    is_extension=True,
                    extension_id=ext_id
                ))
        
        # Add missing CLI tools
        cli_tools = [
            ("Gemini CLI", "pip install google-generativeai", "gemini"),
            ("Claude Code CLI", "pip install anthropic", "claude")
        ]
        
        existing_cli = [tool.name.lower() for tool in tools]
        for cli_name, cli_install, cli_check in cli_tools:
            if not any(cli_name.lower() in existing for existing in existing_cli):
                tools.append(Tool(
                    name=cli_name,
                    install_command=cli_install,
                    check_command=cli_check
                ))
        
        # Add missing login portals
        ai_portals = [
            ("ChatGPT", "https://chat.openai.com", "OpenAI's ChatGPT"),
            ("Claude", "https://claude.ai", "Anthropic's Claude"),
            ("Gemini", "https://gemini.google.com", "Google's Gemini"),
            ("Grok", "https://x.ai", "xAI's Grok"),
            ("Hugging Face", "https://huggingface.co", "AI model repository")
        ]
        
        existing_portals = [portal.name.lower() for portal in login_portals]
        for portal_name, portal_url, portal_desc in ai_portals:
            if not any(portal_name.lower() in existing for existing in existing_portals):
                login_portals.append(LoginPortal(
                    name=portal_name,
                    url=portal_url,
                    description=portal_desc
                ))
    
    # Web Development recommendations
    elif any(keyword in env_lower for keyword in ['web', 'frontend', 'backend', 'full stack']):
        logger.info("Adding Web Development recommendations")
        
        # Add missing web extensions
        web_extensions = [
            ("JavaScript Extension", "ms-vscode.vscode-typescript-next"),
            ("ES7+ React/Redux/React-Native snippets", "dsznajder.es7-react-js-snippets"),
            ("Prettier", "esbenp.prettier-vscode")
        ]
        
        existing_extensions = [tool.name.lower() for tool in tools if tool.is_extension]
        for ext_name, ext_id in web_extensions:
            if not any(ext_name.lower() in existing for existing in existing_extensions):
                tools.append(Tool(
                    name=ext_name,
                    install_command="",
                    check_command="code",
                    is_extension=True,
                    extension_id=ext_id
                ))
        
        # Add missing web portals
        web_portals = [
            ("GitHub", "https://github.com", "Code repository"),
            ("Netlify", "https://netlify.com", "Web hosting platform"),
            ("Vercel", "https://vercel.com", "Web deployment platform")
        ]
        
        existing_portals = [portal.name.lower() for portal in login_portals]
        for portal_name, portal_url, portal_desc in web_portals:
            if not any(portal_name.lower() in existing for existing in existing_portals):
                login_portals.append(LoginPortal(
                    name=portal_name,
                    url=portal_url,
                    description=portal_desc
                ))
    
    # Data Science recommendations
    elif any(keyword in env_lower for keyword in ['data', 'science', 'data science', 'ml', 'machine learning']):
        logger.info("Adding Data Science recommendations")
        
        # Add missing data science extensions
        ds_extensions = [
            ("Jupyter Extension", "ms-toolsai.jupyter"),
            ("Python Extension", "ms-python.python")
        ]
        
        existing_extensions = [tool.name.lower() for tool in tools if tool.is_extension]
        for ext_name, ext_id in ds_extensions:
            if not any(ext_name.lower() in existing for existing in existing_extensions):
                tools.append(Tool(
                    name=ext_name,
                    install_command="",
                    check_command="code",
                    is_extension=True,
                    extension_id=ext_id
                ))
        
        # Add missing data science portals
        ds_portals = [
            ("Kaggle", "https://kaggle.com", "AI model repository"),
            ("Google Colab", "https://colab.research.google.com", "Cloud notebooks"),
            ("Hugging Face", "https://huggingface.co", "AI model repository")
        ]
        
        existing_portals = [portal.name.lower() for portal in login_portals]
        for portal_name, portal_url, portal_desc in ds_portals:
            if not any(portal_name.lower() in existing for existing in existing_portals):
                login_portals.append(LoginPortal(
                    name=portal_name,
                    url=portal_url,
                    description=portal_desc
                ))
    
    return tools, login_portals


# CLI entry point (add --debug flag support)
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CONFIGO AI Stack Suggestion")
    parser.add_argument("env", type=str, help="Environment description")
    parser.add_argument("--debug", action="store_true", help="Print Gemini prompt and response")
    args = parser.parse_args()
    suggest_stack(args.env, debug=args.debug) 