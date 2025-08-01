"""
CONFIGO Chat Agent
==================

Interactive conversational mode for CONFIGO that allows users to:
- Ask questions about tools, setup, and errors
- Run commands via natural language
- Get contextual recommendations based on memory and environment
"""

import logging
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from core.ai import LLMClient
from core.memory import AgentMemory
from core.enhanced_llm_agent import EnhancedLLMAgent

logger = logging.getLogger(__name__)

@dataclass
class ChatResponse:
    """Response from chat agent."""
    message: str
    action_type: str  # "info", "command", "question", "error"
    command: Optional[str] = None
    confidence: float = 0.8
    requires_confirmation: bool = False

class ChatAgent:
    """
    Interactive chat agent for CONFIGO.
    
    Handles natural language queries and converts them to actions.
    """
    
    def __init__(self, memory: AgentMemory, debug_mode: bool = False):
        self.memory = memory
        self.llm_client = LLMClient()
        self.enhanced_agent = EnhancedLLMAgent(memory)
        self.debug_mode = debug_mode
        
        # Chat history for context (last 5 messages)
        self.chat_history = []
        self.max_history = 5
        
        # Command patterns for natural language
        self.command_patterns = {
            r"install\s+(\w+)": "install_tool",
            r"setup\s+(\w+)": "install_tool", 
            r"add\s+(\w+)": "install_tool",
            r"check\s+(\w+)": "validate_tool",
            r"verify\s+(\w+)": "validate_tool",
            r"what\s+is\s+(\w+)": "explain_tool",
            r"how\s+to\s+(\w+)": "explain_tool",
            r"recommend\s+(\w+)": "recommend_tools",
            r"suggest\s+(\w+)": "recommend_tools",
        }
        
        logger.info("Chat agent initialized")
    
    def _get_chat_context(self) -> str:
        """Get recent chat history for context."""
        if not self.chat_history:
            return ""
        
        context_lines = []
        for i, (user_msg, agent_msg) in enumerate(self.chat_history[-3:], 1):  # Last 3 exchanges
            context_lines.append(f"Previous exchange {i}:")
            context_lines.append(f"User: {user_msg}")
            context_lines.append(f"CONFIGO: {agent_msg}")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def _add_to_history(self, user_input: str, agent_response: str) -> None:
        """Add message exchange to chat history."""
        self.chat_history.append((user_input, agent_response))
        
        # Keep only the last max_history exchanges
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
    
    def _show_debug_info(self, user_input: str, memory_context: str, chat_context: str, llm_response: str) -> None:
        """Show debug information for LLM input/output."""
        print("\n" + "="*60)
        print("🔍 DEBUG MODE - LLM Input/Output")
        print("="*60)
        print(f"📝 User Input: {user_input}")
        if memory_context:
            print(f"🧠 Memory Context: {memory_context[:200]}...")
        if chat_context:
            print(f"💬 Chat Context: {chat_context[:200]}...")
        print(f"🤖 LLM Response: {llm_response}")
        print("="*60 + "\n")
    
    def process_message(self, user_input: str) -> ChatResponse:
        """
        Process user input and return appropriate response using real LLM API calls.
        
        This method ensures the chat agent is truly AI-powered by calling the Gemini API
        instead of using fallback responses.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            ChatResponse: Structured response with action and message
        """
        try:
            # Validate input
            if not user_input or not user_input.strip():
                return ChatResponse(
                    message="I didn't catch that. Could you please repeat?",
                    action_type="error",
                    confidence=0.3
                )
            
            # Get memory context for better responses
            memory_context = self.memory.get_memory_context()
            
            # Add chat history context
            chat_context = self._get_chat_context()
            
            # Call the actual LLM API for intelligent responses
            logger.info(f"Calling LLM API for chat response to: {user_input[:50]}...")
            llm_response = self.llm_client.chat_response(user_input, memory_context, chat_context)
            
            # Show debug info if enabled
            if self.debug_mode:
                self._show_debug_info(user_input, memory_context, chat_context, llm_response)
            
            # Validate LLM response
            if not llm_response or not isinstance(llm_response, str) or len(llm_response.strip()) < 2:
                logger.error("Empty or invalid response from LLM API")
                return ChatResponse(
                    message="⚠️ I'm having trouble connecting to my AI brain right now. Please check your GEMINI_API_KEY and try again.",
                    action_type="error",
                    confidence=0.4
                )
            
            # Add to chat history
            self._add_to_history(user_input, llm_response)
            
            # Parse and categorize response
            response = self._parse_chat_response(llm_response, user_input)
            
            # Add memory context if relevant
            if response.action_type == "info":
                response.message = self._enhance_with_memory(response.message, user_input)
            
            logger.info(f"Chat response generated via LLM API: {response.action_type} - {response.message[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat message via LLM API: {e}")
            return ChatResponse(
                message="I'm having trouble connecting to my AI brain. Please check your GEMINI_API_KEY in the .env file and try again.",
                action_type="error",
                confidence=0.5
            )
    

    
    def _parse_chat_response(self, llm_response: str, original_input: str) -> ChatResponse:
        """Parse LLM response into structured ChatResponse."""
        if not llm_response:
            return ChatResponse(
                message="I didn't get a response. Could you try again?",
                action_type="error",
                confidence=0.3
            )
        
        # Check if the response contains installation commands
        user_input_lower = original_input.lower()
        llm_response_lower = llm_response.lower()
        
        # Look for installation patterns in the response
        if any(phrase in llm_response_lower for phrase in ["install", "setup", "add"]):
            # Extract potential command from response
            command = self._extract_command_from_response(llm_response)
            if command:
                return ChatResponse(
                    message=llm_response.strip(),
                    action_type="command",
                    command=command,
                    requires_confirmation=True,
                    confidence=0.7
                )
        
        # Check for actual error-related responses (more specific patterns)
        error_patterns = [
            r'\b(error|failed|failure)\b',
            r'\b(problem|issue)\s+(with|in)\b',
            r'\b(cannot|can\'t|unable)\s+to\b',
            r'\b(failed|failed to)\b'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, llm_response_lower):
                return ChatResponse(
                    message=llm_response.strip(),
                    action_type="error",
                    confidence=0.6
                )
        
        # Default: treat as informational response
        return ChatResponse(
            message=llm_response.strip(),
            action_type="info",
            confidence=0.8
        )
    
    def _extract_command_from_response(self, response: str) -> Optional[str]:
        """Extract installation command from response text."""
        # Look for common command patterns
        import re
        
        # Look for commands in backticks
        command_match = re.search(r'`([^`]+)`', response)
        if command_match:
            return command_match.group(1)
        
        # Look for sudo commands
        sudo_match = re.search(r'(sudo\s+[^\n]+)', response)
        if sudo_match:
            return sudo_match.group(1)
        
        # Look for apt commands
        apt_match = re.search(r'(apt\s+[^\n]+)', response)
        if apt_match:
            return apt_match.group(1)
        
        # Look for pip commands
        pip_match = re.search(r'(pip\s+[^\n]+)', response)
        if pip_match:
            return pip_match.group(1)
        
        return None
    
    def _enhance_with_memory(self, message: str, user_input: str) -> str:
        """Enhance response with memory context."""
        # Check if user is asking about a specific tool
        tool_pattern = r'\b(\w+)\b'
        matches = re.findall(tool_pattern, user_input.lower())
        
        for match in matches:
            tool_memory = self.memory.get_tool_memory(match)
            if tool_memory:
                if tool_memory.install_success:
                    message += f"\n\n📝 Memory: {match} was successfully installed previously."
                else:
                    message += f"\n\n⚠️ Memory: {match} failed installation before. You might need to try a different approach."
        
        return message
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """
        Execute a shell command safely.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Tuple[bool, str]: (success, output/error message)
        """
        try:
            # Basic safety check
            dangerous_patterns = [
                r'rm\s+-rf\s+/',
                r'dd\s+if=.*\s+of=/dev/',
                r':\(\)\{\s*:\|\:&\s*\};:',
                r'chmod\s+777\s+/',
                r'chown\s+root\s+/'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, command):
                    return False, "❌ This command is blocked for safety reasons."
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip() or "✅ Command executed successfully."
            else:
                return False, f"❌ Command failed: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return False, "⏰ Command timed out after 60 seconds."
        except Exception as e:
            return False, f"💥 Error executing command: {str(e)}"
    
    def get_quick_help(self) -> str:
        """Get quick help for chat mode."""
        return """
💬 CONFIGO Chat Mode - Quick Help

Try these commands:
• "Install Python 3.11"
• "What is Docker?"
• "Check if Git is installed"
• "Recommend tools for web development"
• "How to set up a Python environment?"

I remember your previous installations and can help with:
• Tool installation and setup
• Environment configuration
• Error troubleshooting
• Development recommendations

Type 'exit' to quit chat mode.
""" 