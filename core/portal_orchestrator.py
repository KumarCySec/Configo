"""
CONFIGO Portal Orchestrator
===========================

Handles browser-based logins for AI services and CLI tool installations:
- Claude, Gemini, Grok, ChatGPT
- Shows friendly UI to track login status
- Auto-installs CLI tools
- Remembers login status per profile
"""

import logging
import subprocess
import webbrowser
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from core.memory import AgentMemory
from core.ai import LLMClient

logger = logging.getLogger(__name__)

@dataclass
class PortalStatus:
    """Status of a login portal."""
    name: str
    url: str
    cli_tool: Optional[str] = None
    is_logged_in: bool = False
    last_check: Optional[float] = None
    installation_status: str = "not_installed"  # not_installed, installing, installed, failed

@dataclass
class PortalConfig:
    """Configuration for a login portal."""
    name: str
    url: str
    cli_tool: Optional[str] = None
    install_command: Optional[str] = None
    check_command: Optional[str] = None
    description: str = ""

class PortalOrchestrator:
    """
    Orchestrates login portals and CLI tool installations.
    """
    
    def __init__(self, memory: AgentMemory):
        self.memory = memory
        self.llm_client = LLMClient()
        
        # Portal configurations
        self.portals = {
            "claude": PortalConfig(
                name="Claude",
                url="https://claude.ai",
                cli_tool="claude",
                install_command="npm install -g @anthropic-ai/claude",
                check_command="claude --version",
                description="Anthropic's Claude AI assistant"
            ),
            "gemini": PortalConfig(
                name="Gemini",
                url="https://aistudio.google.com/app/apikey",
                cli_tool="gemini",
                install_command="pip install google-generativeai",
                check_command="python -c 'import google.generativeai; print(\"Gemini available\")'",
                description="Google's Gemini AI model"
            ),
            "grok": PortalConfig(
                name="Grok",
                url="https://grok.x.ai",
                cli_tool="grok",
                install_command="pip install grok-sdk",
                check_command="python -c 'import grok; print(\"Grok available\")'",
                description="xAI's Grok AI assistant"
            ),
            "chatgpt": PortalConfig(
                name="ChatGPT",
                url="https://chat.openai.com",
                cli_tool="openai",
                install_command="pip install openai",
                check_command="python -c 'import openai; print(\"OpenAI available\")'",
                description="OpenAI's ChatGPT"
            ),
            "cursor": PortalConfig(
                name="Cursor",
                url="https://cursor.sh",
                cli_tool="cursor",
                install_command="curl -L https://cursor.sh/install.sh | sh",
                check_command="cursor --version",
                description="AI-powered code editor"
            ),
            "github": PortalConfig(
                name="GitHub",
                url="https://github.com",
                cli_tool="gh",
                install_command="curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && sudo apt update && sudo apt install gh",
                check_command="gh --version",
                description="GitHub CLI tool"
            )
        }
        
        # Current portal statuses
        self.portal_statuses: Dict[str, PortalStatus] = {}
        self._load_portal_statuses()
        
        logger.info("Portal orchestrator initialized")
    
    def open_login_portal(self, portal_name: str) -> bool:
        """
        Open a login portal in the browser.
        
        Args:
            portal_name: Name of the portal to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if portal_name not in self.portals:
                logger.error(f"Unknown portal: {portal_name}")
                return False
            
            portal_config = self.portals[portal_name]
            
            # Open browser
            logger.info(f"🌐 Opening {portal_config.name} login portal...")
            webbrowser.open(portal_config.url)
            
            # Update status
            self._update_portal_status(portal_name, is_logged_in=False, last_check=time.time())
            
            # Record in memory
            self.memory.record_login_portal_visit(portal_name, portal_config.url)
            
            logger.info(f"✅ Opened {portal_config.name} login portal")
            return True
            
        except Exception as e:
            logger.error(f"Error opening portal {portal_name}: {e}")
            return False
    
    def install_cli_tool(self, portal_name: str) -> Tuple[bool, str]:
        """
        Install CLI tool for a portal.
        
        Args:
            portal_name: Name of the portal
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if portal_name not in self.portals:
                return False, f"Unknown portal: {portal_name}"
            
            portal_config = self.portals[portal_name]
            
            if not portal_config.cli_tool or not portal_config.install_command:
                return False, f"No CLI tool available for {portal_config.name}"
            
            # Update status to installing
            self._update_portal_status(portal_name, installation_status="installing")
            
            logger.info(f"🔧 Installing {portal_config.name} CLI tool...")
            
            # Execute install command
            result = subprocess.run(
                portal_config.install_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                # Verify installation
                if self._verify_cli_installation(portal_name):
                    self._update_portal_status(portal_name, installation_status="installed")
                    logger.info(f"✅ {portal_config.name} CLI tool installed successfully")
                    return True, f"{portal_config.name} CLI tool installed successfully"
                else:
                    self._update_portal_status(portal_name, installation_status="failed")
                    return False, f"{portal_config.name} CLI tool installed but verification failed"
            else:
                self._update_portal_status(portal_name, installation_status="failed")
                error_msg = result.stderr.strip() or result.stdout.strip() or "Installation failed"
                logger.error(f"❌ {portal_config.name} CLI tool installation failed: {error_msg}")
                return False, f"Installation failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            self._update_portal_status(portal_name, installation_status="failed")
            return False, "Installation timed out after 5 minutes"
        except Exception as e:
            self._update_portal_status(portal_name, installation_status="failed")
            return False, f"Installation error: {str(e)}"
    
    def check_login_status(self, portal_name: str) -> bool:
        """
        Check if user is logged in to a portal.
        
        Args:
            portal_name: Name of the portal
            
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            if portal_name not in self.portals:
                return False
            
            portal_config = self.portals[portal_name]
            
            # For now, we'll use a simple heuristic based on CLI tool availability
            # In a real implementation, you might check API keys or tokens
            if portal_config.cli_tool and portal_config.check_command:
                result = subprocess.run(
                    portal_config.check_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                is_logged_in = result.returncode == 0
                self._update_portal_status(portal_name, is_logged_in=is_logged_in, last_check=time.time())
                
                return is_logged_in
            
            # For portals without CLI tools, assume not logged in
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status for {portal_name}: {e}")
            return False
    
    def get_portal_status(self, portal_name: str) -> Optional[PortalStatus]:
        """Get status of a specific portal."""
        return self.portal_statuses.get(portal_name)
    
    def get_all_portal_statuses(self) -> Dict[str, PortalStatus]:
        """Get status of all portals."""
        return self.portal_statuses.copy()
    
    def list_available_portals(self) -> List[PortalConfig]:
        """Get list of available portals."""
        return list(self.portals.values())
    
    def get_portal_summary(self) -> Dict[str, Any]:
        """Get summary of all portal statuses."""
        total_portals = len(self.portals)
        installed_tools = sum(1 for status in self.portal_statuses.values() 
                            if status.installation_status == "installed")
        logged_in = sum(1 for status in self.portal_statuses.values() 
                       if status.is_logged_in)
        
        return {
            "total_portals": total_portals,
            "installed_cli_tools": installed_tools,
            "logged_in_portals": logged_in,
            "installation_rate": (installed_tools / total_portals * 100) if total_portals > 0 else 0,
            "login_rate": (logged_in / total_portals * 100) if total_portals > 0 else 0
        }
    
    def _verify_cli_installation(self, portal_name: str) -> bool:
        """Verify that CLI tool was installed correctly."""
        try:
            if portal_name not in self.portals:
                return False
            
            portal_config = self.portals[portal_name]
            
            if not portal_config.check_command:
                return True  # No check command, assume success
            
            result = subprocess.run(
                portal_config.check_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _update_portal_status(self, portal_name: str, **updates) -> None:
        """Update portal status."""
        if portal_name not in self.portal_statuses:
            portal_config = self.portals[portal_name]
            self.portal_statuses[portal_name] = PortalStatus(
                name=portal_config.name,
                url=portal_config.url,
                cli_tool=portal_config.cli_tool
            )
        
        status = self.portal_statuses[portal_name]
        
        for key, value in updates.items():
            if hasattr(status, key):
                setattr(status, key, value)
        
        self._save_portal_statuses()
    
    def _load_portal_statuses(self) -> None:
        """Load portal statuses from memory."""
        try:
            # Load from memory system
            portal_data = self.memory.get_login_portals_memory()
            
            for portal_name, data in portal_data.items():
                if portal_name in self.portals:
                    portal_config = self.portals[portal_name]
                    
                    self.portal_statuses[portal_name] = PortalStatus(
                        name=portal_config.name,
                        url=portal_config.url,
                        cli_tool=portal_config.cli_tool,
                        is_logged_in=data.get('is_logged_in', False),
                        last_check=data.get('last_check'),
                        installation_status=data.get('installation_status', 'not_installed')
                    )
                    
        except Exception as e:
            logger.error(f"Error loading portal statuses: {e}")
            self.portal_statuses = {}
    
    def _save_portal_statuses(self) -> None:
        """Save portal statuses to memory."""
        try:
            for portal_name, status in self.portal_statuses.items():
                self.memory.record_login_portal_status(
                    portal_name,
                    is_logged_in=status.is_logged_in,
                    last_check=status.last_check,
                    installation_status=status.installation_status
                )
                
        except Exception as e:
            logger.error(f"Error saving portal statuses: {e}")
    
    def get_portal_recommendations(self) -> List[str]:
        """Get recommendations for portal setup."""
        recommendations = []
        
        # Check which portals are missing CLI tools
        for portal_name, status in self.portal_statuses.items():
            if status.installation_status == "not_installed" and self.portals[portal_name].cli_tool:
                recommendations.append(f"Install {self.portals[portal_name].name} CLI tool")
        
        # Check which portals need login
        for portal_name, status in self.portal_statuses.items():
            if not status.is_logged_in:
                recommendations.append(f"Login to {self.portals[portal_name].name}")
        
        return recommendations 