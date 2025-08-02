"""
CONFIGO Core Installer
======================

Handles tool installation, validation, and retry logic with intelligent
error handling and progress tracking.
"""

import logging
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class InstallationStep:
    """Represents a single installation step."""
    name: str
    command: str
    check_command: Optional[str] = None
    description: str = ""
    is_extension: bool = False
    extension_id: Optional[str] = None
    timeout: int = 300  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class InstallationResult:
    """Result of an installation operation."""
    success: bool
    tool_name: str
    version: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    command_output: str = ""


class Installer:
    """
    Core installer for CONFIGO tools and extensions.
    
    Handles installation planning, execution, validation, and retry logic.
    """
    
    def __init__(self, config=None, knowledge_engine=None):
        """Initialize the installer."""
        self.config = config
        self.knowledge = knowledge_engine
        self.installed_tools = {}
        self.failed_installations = {}
        
        # Package manager detection
        self.package_managers = self._detect_package_managers()
        
        logger.info("CONFIGO Installer initialized")
    
    def _detect_package_managers(self) -> Dict[str, bool]:
        """Detect available package managers on the system."""
        managers = {}
        
        # Check for common package managers
        package_managers = [
            ('apt-get', 'apt-get --version'),
            ('yum', 'yum --version'),
            ('dnf', 'dnf --version'),
            ('pacman', 'pacman --version'),
            ('brew', 'brew --version'),
            ('snap', 'snap --version'),
            ('flatpak', 'flatpak --version'),
            ('pip', 'pip --version'),
            ('npm', 'npm --version'),
            ('yarn', 'yarn --version'),
            ('cargo', 'cargo --version'),
            ('go', 'go version'),
        ]
        
        for manager, check_cmd in package_managers:
            try:
                result = subprocess.run(
                    check_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                managers[manager] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                managers[manager] = False
        
        logger.info(f"Detected package managers: {[k for k, v in managers.items() if v]}")
        return managers
    
    def install_tool(self, plan: Dict[str, Any], ui=None) -> InstallationResult:
        """
        Install a single tool based on a plan.
        
        Args:
            plan: Installation plan containing tool details
            ui: UI instance for progress display
            
        Returns:
            InstallationResult: Result of the installation
        """
        tool_name = plan.get('name', 'unknown')
        command = plan.get('command', '')
        check_command = plan.get('check_command')
        description = plan.get('description', f'Installing {tool_name}')
        
        step = InstallationStep(
            name=tool_name,
            command=command,
            check_command=check_command,
            description=description,
            is_extension=plan.get('is_extension', False),
            extension_id=plan.get('extension_id')
        )
        
        return self._execute_installation_step(step, ui)
    
    def execute_plan(self, plan: Dict[str, Any], ui=None) -> List[InstallationResult]:
        """
        Execute a complete installation plan.
        
        Args:
            plan: Complete installation plan
            ui: UI instance for progress display
            
        Returns:
            List[InstallationResult]: Results for all installation steps
        """
        steps = plan.get('steps', [])
        results = []
        
        if ui:
            ui.show_info_message(f"Executing installation plan with {len(steps)} steps")
        
        for i, step_data in enumerate(steps):
            step = InstallationStep(
                name=step_data.get('name', f'step_{i}'),
                command=step_data.get('command', ''),
                check_command=step_data.get('check_command'),
                description=step_data.get('description', f'Step {i+1}'),
                is_extension=step_data.get('is_extension', False),
                extension_id=step_data.get('extension_id'),
                timeout=step_data.get('timeout', 300)
            )
            
            if ui:
                ui.show_info_message(f"Step {i+1}/{len(steps)}: {step.description}")
            
            result = self._execute_installation_step(step, ui)
            results.append(result)
            
            # Store result
            if result.success:
                self.installed_tools[result.tool_name] = result
            else:
                self.failed_installations[result.tool_name] = result
            
            # Brief pause between installations
            time.sleep(1)
        
        return results
    
    def _log_installation_to_knowledge(self, result: InstallationResult, system_info: Dict[str, Any]) -> None:
        """
        Log installation result to knowledge base.
        
        Args:
            result: Installation result
            system_info: System information
        """
        if not self.knowledge:
            return
        
        try:
            # Add tool knowledge
            tool_metadata = {
                'description': f'Tool: {result.tool_name}',
                'category': 'development_tool',
                'version': result.version,
                'install_success': result.success,
                'error_message': result.error_message,
                'execution_time': result.execution_time,
                'retry_count': result.retry_count
            }
            
            self.knowledge.add_tool_knowledge(result.tool_name, tool_metadata)
            
            # Add installation result to graph
            if self.knowledge.graph_manager:
                self.knowledge.graph_manager.add_installation_result(
                    result.tool_name,
                    result.success,
                    system_info,
                    result.error_message
                )
            
            # Add error knowledge to vector store if failed
            if not result.success and result.error_message:
                self.knowledge.vector_manager.add_error_knowledge(
                    result.error_message,
                    "Retry installation or check system requirements",
                    result.tool_name,
                    system_info
                )
            
            logger.info(f"Logged installation result to knowledge base: {result.tool_name}")
        except Exception as e:
            logger.error(f"Failed to log installation to knowledge base: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        import platform
        import sys
        
        return {
            'os': platform.system(),
            'arch': platform.machine(),
            'python_version': sys.version,
            'platform': platform.platform()
        }
    
    def _execute_installation_step(self, step: InstallationStep, ui=None) -> InstallationResult:
        """
        Execute a single installation step with retry logic.
        
        Args:
            step: Installation step to execute
            ui: UI instance for progress display
            
        Returns:
            InstallationResult: Result of the installation
        """
        start_time = time.time()
        
        # Check if already installed
        if self._is_tool_installed(step.name, step.check_command):
            if ui:
                ui.show_info_message(f"{step.name} is already installed")
            return InstallationResult(
                success=True,
                tool_name=step.name,
                version=self._get_tool_version(step.name, step.check_command),
                execution_time=time.time() - start_time
            )
        
        # Execute installation with retry logic
        while step.retry_count <= step.max_retries:
            try:
                if ui:
                    progress = ui.show_installation_progress(step.name, 100)
                
                # Execute command
                result = subprocess.run(
                    step.command.split(),
                    capture_output=True,
                    text=True,
                    timeout=step.timeout
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    # Installation successful
                    version = self._get_tool_version(step.name, step.check_command)
                    
                    if ui:
                        ui.show_success_message(f"Successfully installed {step.name}")
                    
                    result_obj = InstallationResult(
                        success=True,
                        tool_name=step.name,
                        version=version,
                        execution_time=execution_time,
                        retry_count=step.retry_count,
                        command_output=result.stdout
                    )
                    
                    # Log to knowledge base
                    system_info = self._get_system_info()
                    self._log_installation_to_knowledge(result_obj, system_info)
                    
                    return result_obj
                else:
                    # Installation failed
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    step.retry_count += 1
                    
                    if ui:
                        ui.show_error_message(
                            f"Failed to install {step.name} (attempt {step.retry_count}/{step.max_retries})",
                            suggestion=error_msg
                        )
                    
                    if step.retry_count <= step.max_retries:
                        # Wait before retry
                        time.sleep(2 ** step.retry_count)  # Exponential backoff
                        continue
                    else:
                        # Max retries exceeded
                        result_obj = InstallationResult(
                            success=False,
                            tool_name=step.name,
                            error_message=error_msg,
                            execution_time=execution_time,
                            retry_count=step.retry_count,
                            command_output=result.stdout
                        )
                        
                        # Log to knowledge base
                        system_info = self._get_system_info()
                        self._log_installation_to_knowledge(result_obj, system_info)
                        
                        return result_obj
                        
            except subprocess.TimeoutExpired:
                step.retry_count += 1
                error_msg = f"Installation timed out after {step.timeout} seconds"
                
                if ui:
                    ui.show_error_message(
                        f"Timeout installing {step.name} (attempt {step.retry_count}/{step.max_retries})",
                        suggestion=error_msg
                    )
                
                if step.retry_count <= step.max_retries:
                    time.sleep(2 ** step.retry_count)
                    continue
                else:
                    return InstallationResult(
                        success=False,
                        tool_name=step.name,
                        error_message=error_msg,
                        execution_time=time.time() - start_time,
                        retry_count=step.retry_count
                    )
                
            except Exception as e:
                step.retry_count += 1
                error_msg = str(e)
                
                if ui:
                    ui.show_error_message(
                        f"Error installing {step.name} (attempt {step.retry_count}/{step.max_retries})",
                        suggestion=error_msg
                    )
                
                if step.retry_count <= step.max_retries:
                    time.sleep(2 ** step.retry_count)
                    continue
                else:
                    return InstallationResult(
                        success=False,
                        tool_name=step.name,
                        error_message=error_msg,
                        execution_time=time.time() - start_time,
                        retry_count=step.retry_count
                    )
        
        # Should not reach here, but just in case
        return InstallationResult(
            success=False,
            tool_name=step.name,
            error_message="Max retries exceeded",
            execution_time=time.time() - start_time,
            retry_count=step.retry_count
        )
    
    def _is_tool_installed(self, tool_name: str, check_command: Optional[str] = None) -> bool:
        """Check if a tool is already installed."""
        if not check_command:
            # Try common check commands
            check_commands = [
                f"{tool_name} --version",
                f"{tool_name} -v",
                f"{tool_name} version",
                f"which {tool_name}",
                f"command -v {tool_name}"
            ]
        else:
            check_commands = [check_command]
        
        for cmd in check_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return False
    
    def _get_tool_version(self, tool_name: str, check_command: Optional[str] = None) -> Optional[str]:
        """Get the version of an installed tool."""
        if not check_command:
            check_commands = [
                f"{tool_name} --version",
                f"{tool_name} -v",
                f"{tool_name} version"
            ]
        else:
            check_commands = [check_command]
        
        for cmd in check_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # Extract version from output
                    output = result.stdout.strip()
                    if output:
                        return output.split('\n')[0]  # First line
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def get_installation_stats(self) -> Dict[str, Any]:
        """Get statistics about installations."""
        total_installations = len(self.installed_tools) + len(self.failed_installations)
        success_rate = len(self.installed_tools) / total_installations if total_installations > 0 else 0
        
        return {
            'total_installations': total_installations,
            'successful_installations': len(self.installed_tools),
            'failed_installations': len(self.failed_installations),
            'success_rate': success_rate,
            'installed_tools': list(self.installed_tools.keys()),
            'failed_tools': list(self.failed_installations.keys())
        }
    
    def retry_failed_installations(self, ui=None) -> List[InstallationResult]:
        """Retry all failed installations."""
        results = []
        
        if not self.failed_installations:
            if ui:
                ui.show_info_message("No failed installations to retry")
            return results
        
        if ui:
            ui.show_info_message(f"Retrying {len(self.failed_installations)} failed installations")
        
        for tool_name, failed_result in self.failed_installations.items():
            if ui:
                ui.show_info_message(f"Retrying installation of {tool_name}")
            
            # Create a new plan for retry
            plan = {
                'name': tool_name,
                'command': failed_result.command_output,  # Use original command
                'check_command': None,
                'description': f'Retrying installation of {tool_name}'
            }
            
            result = self.install_tool(plan, ui)
            results.append(result)
            
            if result.success:
                # Remove from failed and add to installed
                del self.failed_installations[tool_name]
                self.installed_tools[tool_name] = result
        
        return results 