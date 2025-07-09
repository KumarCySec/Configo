"""
Shell Executor for CONFIGO - handles YAML installation plans with error handling and retry logic.
"""

import subprocess
import logging
import os
import shutil
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ShellExecutor:
    """
    Executes shell commands from YAML installation plans with error handling and retry logic.
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    def execute_install_plan(self, plan: Dict[str, Any], llm_agent, messages=None) -> Dict[str, Any]:
        """
        Execute a complete installation plan with enhanced progress tracking.
        
        Args:
            plan: YAML installation plan
            llm_agent: LLM agent for error fixes
            messages: UI message display for progress updates
            
        Returns:
            Dict[str, Any]: Installation result with success status and details
        """
        app_name = plan.get('app', 'Unknown App')
        method = plan.get('method', 'unknown')
        
        logger.info(f"Executing install plan for {app_name} using {method}")
        
        result = {
            'app_name': app_name,
            'method': method,
            'success': False,
            'error': None,
            'version': None,
            'launch_command': plan.get('launch', ''),
            'desktop_entry': plan.get('desktop_entry', {}),
            'install_commands': [],
            'desktop_entry_created': False
        }
        
        try:
            # Show progress message
            if messages:
                messages.show_install_progress(app_name, "Fetching installation commands...", 1)
            
            # Execute installation commands
            install_commands = plan.get('install', '').strip().split('\n')
            install_commands = [cmd.strip() for cmd in install_commands if cmd.strip()]
            
            for i, cmd in enumerate(install_commands):
                if messages:
                    messages.show_install_progress(app_name, f"Running command {i+1}/{len(install_commands)}", i+1)
                
                success, output, error = self._execute_command_with_retry(cmd, app_name, llm_agent, messages)
                result['install_commands'].append({
                    'command': cmd,
                    'success': success,
                    'output': output,
                    'error': error
                })
                
                if not success:
                    result['error'] = f"Installation command failed: {error}"
                    return result
            
            # Verify installation
            check_command = plan.get('check', '')
            if check_command:
                if messages:
                    messages.show_install_progress(app_name, "Verifying installation...", len(install_commands) + 1)
                
                success, output, error = self._execute_command(check_command)
                if success:
                    result['version'] = output.strip()
                    result['success'] = True
                else:
                    result['error'] = f"Installation verification failed: {error}"
                    return result
            else:
                result['success'] = True
            
            # Create desktop entry if specified and installation was successful
            if result['success'] and plan.get('desktop_entry'):
                if messages:
                    messages.show_install_progress(app_name, "Creating desktop shortcut...", len(install_commands) + 2)
                
                desktop_created = self._create_desktop_entry(plan['desktop_entry'], app_name, plan.get('launch', ''))
                result['desktop_entry_created'] = desktop_created
                
                # Update desktop menu cache
                if desktop_created:
                    self._update_desktop_menu()
            
            logger.info(f"Successfully installed {app_name}")
            return result
            
        except Exception as e:
            result['error'] = f"Installation failed: {str(e)}"
            logger.error(f"Error installing {app_name}: {e}")
            return result
    
    def _execute_command_with_retry(self, command: str, app_name: str, llm_agent, messages=None) -> Tuple[bool, str, str]:
        """
        Execute a command with retry logic and LLM-powered error fixes.
        
        Args:
            command: Command to execute
            app_name: Name of the app being installed
            llm_agent: LLM agent for generating fixes
            messages: UI message display for progress updates
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        for attempt in range(self.max_retries):
            if messages and attempt > 0:
                messages.show_install_error(app_name, f"Retry attempt {attempt + 1}/{self.max_retries}", attempt)
            
            success, output, error = self._execute_command(command)
            
            if success:
                return True, output, error
            
            logger.warning(f"Command failed (attempt {attempt + 1}/{self.max_retries}): {command}")
            logger.warning(f"Error: {error}")
            
            # Try to get a fix from LLM
            if attempt < self.max_retries - 1 and llm_agent:
                if messages:
                    messages.show_install_progress(app_name, "Generating fix with AI...", attempt + 1)
                
                fixed_command = llm_agent.get_error_fix(command, error, app_name)
                if fixed_command and fixed_command != command:
                    logger.info(f"Trying LLM fix: {fixed_command}")
                    command = fixed_command
                    continue
            
            # If no fix available or all retries exhausted
            if attempt == self.max_retries - 1:
                logger.error(f"All retry attempts failed for command: {command}")
        
        return False, output, error
    
    def _execute_command(self, command: str) -> Tuple[bool, str, str]:
        """
        Execute a single shell command with enhanced error handling.
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        try:
            # Add a small delay to show progress
            time.sleep(0.5)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out after 5 minutes"
        except Exception as e:
            return False, "", str(e)
    
    def _create_desktop_entry(self, desktop_info: Dict[str, str], app_name: str, launch_command: str) -> bool:
        """
        Create a desktop entry file for the installed app with enhanced integration.
        
        Args:
            desktop_info: Desktop entry information from plan
            app_name: Name of the app
            launch_command: Command to launch the app
            
        Returns:
            bool: True if desktop entry was created successfully
        """
        try:
            # Determine desktop entry path
            desktop_path = desktop_info.get('path', '')
            if not desktop_path:
                # Create default path in user's local applications directory
                desktop_dir = Path.home() / '.local' / 'share' / 'applications'
                desktop_dir.mkdir(parents=True, exist_ok=True)
                desktop_path = str(desktop_dir / f"{app_name.lower().replace(' ', '-')}.desktop")
            
            # Create desktop entry content with enhanced metadata
            icon_path = desktop_info.get('icon', '')
            if not icon_path:
                # Try to find icon in common locations
                icon_path = self._find_app_icon(app_name)
            
            # Determine categories based on app name
            categories = self._determine_app_categories(app_name)
            
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={app_name} application
Exec={launch_command}
Icon={icon_path}
Terminal=false
Categories={categories}
Keywords={app_name.lower()}
StartupWMClass={app_name.lower().replace(' ', '')}
"""
            
            # Write desktop entry file
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            
            # Make it executable
            os.chmod(desktop_path, 0o755)
            
            logger.info(f"Created desktop entry: {desktop_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create desktop entry for {app_name}: {e}")
            return False
    
    def _find_app_icon(self, app_name: str) -> str:
        """
        Try to find an icon for the app in common locations.
        
        Args:
            app_name: Name of the app
            
        Returns:
            str: Path to icon or empty string if not found
        """
        # Common icon locations
        icon_dirs = [
            '/usr/share/icons/hicolor/128x128/apps/',
            '/usr/share/icons/hicolor/64x64/apps/',
            '/usr/share/icons/hicolor/48x48/apps/',
            '/usr/share/pixmaps/',
            '/usr/share/applications/',
            '/usr/share/icons/',
            '/usr/share/icons/ubuntu-mono-dark/apps/',
            '/usr/share/icons/ubuntu-mono-light/apps/'
        ]
        
        # Common icon extensions
        extensions = ['.png', '.svg', '.xpm', '.ico']
        
        # App-specific icon mappings
        icon_mappings = {
            'telegram': 'telegram',
            'discord': 'discord',
            'slack': 'slack',
            'chrome': 'google-chrome',
            'firefox': 'firefox',
            'zoom': 'zoom',
            'spotify': 'spotify',
            'steam': 'steam',
            'vscode': 'code',
            'vs code': 'code',
            'visual studio code': 'code'
        }
        
        # Try mapped icon name first
        mapped_name = icon_mappings.get(app_name.lower(), app_name.lower().replace(' ', ''))
        
        # Try to find icon
        for icon_dir in icon_dirs:
            if os.path.exists(icon_dir):
                for ext in extensions:
                    # Try mapped name first
                    icon_path = os.path.join(icon_dir, f"{mapped_name}{ext}")
                    if os.path.exists(icon_path):
                        return icon_path
                    
                    # Try original app name
                    icon_path = os.path.join(icon_dir, f"{app_name.lower().replace(' ', '')}{ext}")
                    if os.path.exists(icon_path):
                        return icon_path
        
        return ""
    
    def _determine_app_categories(self, app_name: str) -> str:
        """
        Determine appropriate desktop categories for the app.
        
        Args:
            app_name: Name of the app
            
        Returns:
            str: Desktop categories string
        """
        app_lower = app_name.lower()
        
        # Define category mappings
        if any(word in app_lower for word in ['telegram', 'discord', 'slack', 'zoom', 'teams']):
            return "Network;InstantMessaging;"
        elif any(word in app_lower for word in ['chrome', 'firefox', 'browser']):
            return "Network;WebBrowser;"
        elif any(word in app_lower for word in ['spotify', 'vlc', 'media']):
            return "AudioVideo;Audio;Video;"
        elif any(word in app_lower for word in ['steam', 'game']):
            return "Game;"
        elif any(word in app_lower for word in ['code', 'editor', 'ide', 'studio']):
            return "Development;IDE;TextEditor;"
        elif any(word in app_lower for word in ['office', 'libreoffice', 'document']):
            return "Office;"
        elif any(word in app_lower for word in ['gimp', 'inkscape', 'blender', 'krita']):
            return "Graphics;"
        elif any(word in app_lower for word in ['terminal', 'console']):
            return "System;TerminalEmulator;"
        else:
            return "Utility;Application;"
    
    def _update_desktop_menu(self) -> bool:
        """
        Update the desktop menu cache to refresh application launcher.
        
        Returns:
            bool: True if update was successful
        """
        try:
            # Try different desktop menu update commands
            update_commands = [
                "xdg-desktop-menu forceupdate",
                "update-desktop-database ~/.local/share/applications",
                "gtk-update-icon-cache -f -t ~/.local/share/icons"
            ]
            
            for cmd in update_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        logger.info(f"Desktop menu updated with: {cmd}")
                        return True
                except Exception as e:
                    logger.debug(f"Desktop menu update command failed: {cmd} - {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update desktop menu: {e}")
            return False 