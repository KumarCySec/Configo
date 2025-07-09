"""
CONFIGO Validation System
========================

Comprehensive validation system that checks installed tools and triggers self-healing
when issues are detected. Provides detailed reports and intelligent recommendations.

Features:
- 🔍 Tool installation verification
- 📊 Version detection and validation
- 🔄 Self-healing with LLM-powered fixes
- ⏱️ Performance monitoring
- 📈 Confidence scoring
- 🎯 Intelligent recommendations
"""

import subprocess
import logging
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from core.ai import Tool
from core.memory import AgentMemory
from core.enhanced_llm_agent import EnhancedLLMAgent

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a tool validation"""
    tool_name: str
    is_installed: bool
    check_command: str
    version: Optional[str] = None
    error_message: Optional[str] = None
    validation_time: float = 0.0
    confidence: float = 0.0

@dataclass
class ValidationReport:
    """Complete validation report."""
    total_tools: int
    successful_validations: int
    failed_validations: int
    skipped_validations: int
    validation_results: List[ValidationResult]
    overall_success_rate: float
    recommendations: List[str]

class ToolValidator:
    """
    Validates installed tools and triggers self-healing when issues are detected.
    """
    
    def __init__(self, memory: AgentMemory, llm_agent: EnhancedLLMAgent):
        self.memory = memory
        self.llm_agent = llm_agent
        self.validation_timeout = 10  # seconds
        
        # Version extraction patterns
        self.version_patterns = {
            "python": r"Python (\d+\.\d+\.\d+)",
            "node": r"v(\d+\.\d+\.\d+)",
            "git": r"git version (\d+\.\d+\.\d+)",
            "docker": r"Docker version (\d+\.\d+\.\d+)",
            "code": r"(\d+\.\d+\.\d+)",
            "cursor": r"(\d+\.\d+\.\d+)",
            "jupyter": r"(\d+\.\d+\.\d+)",
            "postman": r"(\d+\.\d+\.\d+)",
            "terraform": r"Terraform v(\d+\.\d+\.\d+)",
            "aws": r"aws-cli/(\d+\.\d+\.\d+)",
            "gcloud": r"(\d+\.\d+\.\d+)"
        }
        
        logger.info("Tool validator initialized")
    
    def validate_tool(self, tool: Tool) -> ValidationResult:
        """
        Validate a single tool by running its check command.
        
        Args:
            tool: Tool to validate
            
        Returns:
            ValidationResult: Validation result with status and details
        """
        start_time = time.time()
        
        try:
            logger.info(f"Validating tool: {tool.name}")
            
            # Run the check command
            result = subprocess.run(
                tool.check_command.split(),
                capture_output=True,
                text=True,
                timeout=self.validation_timeout
            )
            
            validation_time = time.time() - start_time
            
            if result.returncode == 0:
                # Tool is working, extract version if possible
                version = self._extract_version(result.stdout, tool)
                
                # Update memory with successful validation
                self.memory.record_tool_installation(
                    tool.name,
                    install_command="",  # We don't have the original install command here
                    check_command=tool.check_command,
                    success=True,
                    version=version
                )
                
                logger.info(f"✅ {tool.name} validation successful (v{version})")
                
                return ValidationResult(
                    tool_name=tool.name,
                    is_installed=True,
                    version=version,
                    check_command=tool.check_command,
                    validation_time=validation_time
                )
            else:
                # Tool failed validation
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                
                # Update memory with failure
                self.memory.record_tool_installation(
                    tool.name,
                    install_command="",  # We don't have the original install command here
                    check_command=tool.check_command,
                    success=False,
                    error=error_msg
                )
                
                logger.warning(f"❌ {tool.name} validation failed: {error_msg}")
                
                return ValidationResult(
                    tool_name=tool.name,
                    is_installed=False,
                    check_command=tool.check_command,
                    error_message=error_msg,
                    validation_time=validation_time
                )
                
        except subprocess.TimeoutExpired:
            validation_time = time.time() - start_time
            error_msg = f"Validation timed out after {self.validation_timeout}s"
            
            logger.error(f"⏰ {tool.name} validation timed out")
            
            return ValidationResult(
                tool_name=tool.name,
                is_installed=False,
                check_command=tool.check_command,
                error_message=error_msg,
                validation_time=validation_time
            )
            
        except Exception as e:
            validation_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"💥 {tool.name} validation error: {error_msg}")
            
            return ValidationResult(
                tool_name=tool.name,
                is_installed=False,
                check_command=tool.check_command,
                error_message=error_msg,
                validation_time=validation_time
            )
    
    def validate_tools_batch(self, tools: List[Tool]) -> List[ValidationResult]:
        """
        Validate multiple tools in batch.
        
        Args:
            tools: List of tools to validate
            
        Returns:
            List[ValidationResult]: List of validation results
        """
        results = []
        
        for tool in tools:
            result = self.validate_tool(tool)
            results.append(result)
            
            # Small delay between validations to avoid overwhelming the system
            time.sleep(0.1)
        
        return results
    
    def validate_environment(self, tools: List[Tool]) -> Dict[str, Any]:
        """
        Validate the entire environment and provide a summary.
        
        Args:
            tools: List of tools to validate
            
        Returns:
            Dict[str, Any]: Environment validation summary
        """
        logger.info("🔍 Starting environment validation...")
        
        validation_results = self.validate_tools_batch(tools)
        
        # Calculate statistics
        total_tools = len(validation_results)
        valid_tools = sum(1 for r in validation_results if r.is_installed)
        failed_tools = total_tools - valid_tools
        
        # Group results
        valid_results = [r for r in validation_results if r.is_installed]
        failed_results = [r for r in validation_results if not r.is_installed]
        
        # Calculate average validation time
        avg_validation_time = sum(r.validation_time for r in validation_results) / total_tools if total_tools > 0 else 0
        
        summary = {
            "total_tools": total_tools,
            "valid_tools": valid_tools,
            "failed_tools": failed_tools,
            "success_rate": (valid_tools / total_tools * 100) if total_tools > 0 else 0,
            "avg_validation_time": avg_validation_time,
            "valid_results": valid_results,
            "failed_results": failed_results,
            "overall_status": "healthy" if failed_tools == 0 else "issues_detected"
        }
        
        logger.info(f"📊 Environment validation complete: {valid_tools}/{total_tools} tools valid ({summary['success_rate']:.1f}%)")
        
        return summary
    
    def attempt_self_healing(self, failed_tools: List[ValidationResult]) -> List[Dict[str, Any]]:
        """
        Attempt to self-heal failed tools using LLM suggestions.
        
        Args:
            failed_tools: List of failed validation results
            
        Returns:
            List[Dict[str, Any]]: List of healing attempts and results
        """
        healing_results = []
        
        for failed_result in failed_tools:
            logger.info(f"🔧 Attempting to heal {failed_result.tool_name}...")
            
            # Get the original tool to find the install command
            tool_memory = self.memory.get_tool_memory(failed_result.tool_name)
            
            if tool_memory and tool_memory.install_command:
                # Use the original install command from memory
                healing_command = tool_memory.install_command
                healing_source = "memory"
            else:
                # Ask LLM for a fix
                healing_command = self.llm_agent.generate_command_fix(
                    failed_result.tool_name,
                    failed_result.error_message or "Validation failed",
                    failed_result.tool_name
                )
                healing_source = "llm"
            
            if healing_command:
                # Attempt the healing
                healing_success = self._execute_healing_command(failed_result.tool_name, healing_command)
                
                healing_results.append({
                    "tool_name": failed_result.tool_name,
                    "healing_command": healing_command,
                    "healing_source": healing_source,
                    "success": healing_success,
                    "original_error": failed_result.error_message
                })
                
                if healing_success:
                    logger.info(f"✅ Successfully healed {failed_result.tool_name}")
                else:
                    logger.warning(f"❌ Failed to heal {failed_result.tool_name}")
            else:
                logger.warning(f"⚠️ No healing suggestion available for {failed_result.tool_name}")
                healing_results.append({
                    "tool_name": failed_result.tool_name,
                    "healing_command": None,
                    "healing_source": None,
                    "success": False,
                    "original_error": failed_result.error_message
                })
        
        return healing_results
    
    def _execute_healing_command(self, tool_name: str, command: str) -> bool:
        """
        Execute a healing command for a failed tool.
        
        Args:
            tool_name: Name of the tool being healed
            command: Command to execute
            
        Returns:
            bool: True if healing was successful, False otherwise
        """
        try:
            logger.info(f"🔄 Executing healing command for {tool_name}: {command}")
            
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=60  # Longer timeout for installation commands
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Healing command successful for {tool_name}")
                return True
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logger.error(f"❌ Healing command failed for {tool_name}: {error_msg}")
                
                # Update memory with the failure
                self.memory.record_tool_installation(
                    tool_name,
                    install_command=command,
                    check_command="",
                    success=False,
                    error=error_msg
                )
                
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Healing command timed out for {tool_name}")
            return False
        except Exception as e:
            logger.error(f"💥 Healing command error for {tool_name}: {e}")
            return False
    
    def _extract_version(self, output: str, tool: Tool) -> Optional[str]:
        """
        Extract version information from tool output.
        
        Args:
            output: Tool output string
            tool: Tool object
            
        Returns:
            Optional[str]: Extracted version or None
        """
        if not output:
            return None
        
        # Try tool-specific patterns first
        tool_name = tool.name.lower()
        if tool_name in self.version_patterns:
            pattern = self.version_patterns[tool_name]
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Try generic version patterns
        generic_patterns = [
            r"(\d+\.\d+\.\d+)",  # x.y.z
            r"version (\d+\.\d+\.\d+)",  # version x.y.z
            r"v(\d+\.\d+\.\d+)",  # vx.y.z
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_validation_report(self, validation_summary: Dict[str, Any]) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            validation_summary: Validation summary dictionary
            
        Returns:
            str: Formatted validation report
        """
        report_lines = []
        report_lines.append("🔍 VALIDATION REPORT")
        report_lines.append("=" * 50)
        
        # Summary statistics
        total = validation_summary["total_tools"]
        valid = validation_summary["valid_tools"]
        failed = validation_summary["failed_tools"]
        success_rate = validation_summary["success_rate"]
        
        report_lines.append(f"📊 Summary:")
        report_lines.append(f"   Total tools: {total}")
        report_lines.append(f"   Valid tools: {valid}")
        report_lines.append(f"   Failed tools: {failed}")
        report_lines.append(f"   Success rate: {success_rate:.1f}%")
        report_lines.append(f"   Avg validation time: {validation_summary['avg_validation_time']:.2f}s")
        report_lines.append("")
        
        # Valid tools
        if validation_summary["valid_results"]:
            report_lines.append("✅ Valid Tools:")
            for result in validation_summary["valid_results"]:
                version_info = f" (v{result.version})" if result.version else ""
                report_lines.append(f"   • {result.tool_name}{version_info}")
            report_lines.append("")
        
        # Failed tools
        if validation_summary["failed_results"]:
            report_lines.append("❌ Failed Tools:")
            for result in validation_summary["failed_results"]:
                error_info = f" - {result.error_message}" if result.error_message else ""
                report_lines.append(f"   • {result.tool_name}{error_info}")
            report_lines.append("")
        
        # Overall status
        status = validation_summary["overall_status"]
        status_emoji = "🟢" if status == "healthy" else "🟡"
        report_lines.append(f"{status_emoji} Overall Status: {status.upper()}")
        
        return "\n".join(report_lines)
    
    def validate_tools(self, tools: List[Dict[str, Any]]) -> ValidationReport:
        """
        Validate a list of tools and generate a comprehensive report.
        
        Args:
            tools: List of tool dictionaries
            
        Returns:
            ValidationReport: Complete validation report
        """
        logger.info(f"🔍 Starting validation of {len(tools)} tools...")
        
        validation_results = []
        successful_validations = 0
        failed_validations = 0
        skipped_validations = 0
        
        for tool_data in tools:
            tool_name = tool_data.get('name', 'Unknown Tool')
            check_command = tool_data.get('check_command', tool_name.lower())
            is_extension = tool_data.get('is_extension', False)
            
            # Check if we should skip this tool
            if self.memory.should_skip_tool(tool_name):
                logger.info(f"⏭️ Skipping {tool_name} (already installed)")
                skipped_validations += 1
                validation_results.append(ValidationResult(
                    tool_name=tool_name,
                    is_installed=True,
                    check_command=check_command,
                    error_message="Skipped - already installed"
                ))
                continue
            
            # Validate the tool
            result = self._validate_single_tool(tool_name, check_command, is_extension)
            validation_results.append(result)
            
            if result.is_installed:
                successful_validations += 1
            else:
                failed_validations += 1
        
        # Calculate overall success rate
        total_validations = successful_validations + failed_validations
        overall_success_rate = (successful_validations / total_validations * 100) if total_validations > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_validation_recommendations(validation_results)
        
        report = ValidationReport(
            total_tools=len(tools),
            successful_validations=successful_validations,
            failed_validations=failed_validations,
            skipped_validations=skipped_validations,
            validation_results=validation_results,
            overall_success_rate=overall_success_rate,
            recommendations=recommendations
        )
        
        logger.info(f"📊 Validation complete: {successful_validations}/{total_validations} successful ({overall_success_rate:.1f}%)")
        return report
    
    def _validate_single_tool(self, tool_name: str, check_command: str, is_extension: bool) -> ValidationResult:
        """
        Validate a single tool.
        
        Args:
            tool_name: Name of the tool
            check_command: Command to check if tool is installed
            is_extension: Whether this is an extension
            
        Returns:
            ValidationResult: Validation result
        """
        if is_extension:
            return self._validate_extension(tool_name, check_command)
        else:
            return self._validate_regular_tool(tool_name, check_command)
    
    def _validate_regular_tool(self, tool_name: str, check_command: str) -> ValidationResult:
        """
        Validate a regular tool (not an extension).
        
        Args:
            tool_name: Name of the tool
            check_command: Command to check if tool is installed
            
        Returns:
            ValidationResult: Validation result
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Validating {tool_name}...")
            
            result = subprocess.run(
                check_command.split(),
                capture_output=True,
                text=True,
                timeout=self.validation_timeout
            )
            
            validation_time = time.time() - start_time
            
            if result.returncode == 0:
                # Extract version
                version = self._extract_version(result.stdout, Tool(name=tool_name, install_command="", check_command=check_command))
                
                # Calculate confidence
                confidence = self._calculate_validation_confidence(tool_name, result.stdout)
                
                logger.info(f"✅ {tool_name} is valid (v{version})")
                
                return ValidationResult(
                    tool_name=tool_name,
                    is_installed=True,
                    check_command=check_command,
                    version=version,
                    validation_time=validation_time,
                    confidence=confidence
                )
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Command failed"
                
                # Attempt smart recovery
                recovery_result = self._attempt_smart_recovery(tool_name, check_command, error_msg)
                
                if recovery_result:
                    logger.info(f"🔧 Smart recovery found for {tool_name}: {recovery_result}")
                    # Try the recovery command
                    return self._validate_regular_tool(tool_name, recovery_result)
                else:
                    logger.warning(f"❌ {tool_name} validation failed: {error_msg}")
                    
                    return ValidationResult(
                        tool_name=tool_name,
                        is_installed=False,
                        check_command=check_command,
                        error_message=error_msg,
                        validation_time=validation_time,
                        confidence=0.0
                    )
                
        except subprocess.TimeoutExpired:
            validation_time = time.time() - start_time
            error_msg = f"Validation timed out after {self.validation_timeout}s"
            logger.error(f"⏰ {tool_name} validation timed out")
            
            return ValidationResult(
                tool_name=tool_name,
                is_installed=False,
                check_command=check_command,
                error_message=error_msg,
                validation_time=validation_time,
                confidence=0.0
            )
            
        except Exception as e:
            validation_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"💥 {tool_name} validation error: {error_msg}")
            
            return ValidationResult(
                tool_name=tool_name,
                is_installed=False,
                check_command=check_command,
                error_message=error_msg,
                validation_time=validation_time,
                confidence=0.0
            )
    
    def _validate_extension(self, tool_name: str, check_command: str) -> ValidationResult:
        """
        Validate a VS Code/Cursor extension.
        
        Args:
            tool_name: Name of the extension
            check_command: Command to check if extension is installed
            
        Returns:
            ValidationResult: Validation result
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Validating extension {tool_name}...")
            
            # Get extension ID
            extension_id = self._get_extension_id(tool_name)
            if not extension_id:
                error_msg = f"Could not determine extension ID for {tool_name}"
                logger.warning(f"❌ {error_msg}")
                
                return ValidationResult(
                    tool_name=tool_name,
                    is_installed=False,
                    check_command=check_command,
                    error_message=error_msg,
                    validation_time=time.time() - start_time,
                    confidence=0.0
                )
            
            # Check if extension is installed
            result = subprocess.run(
                check_command.split(),
                capture_output=True,
                text=True,
                timeout=self.validation_timeout
            )
            
            validation_time = time.time() - start_time
            
            if result.returncode == 0:
                # Check if our extension is in the list
                installed_extensions = result.stdout.strip().split('\n')
                is_installed = extension_id in installed_extensions
                
                if is_installed:
                    logger.info(f"✅ Extension {tool_name} is installed")
                    
                    return ValidationResult(
                        tool_name=tool_name,
                        is_installed=True,
                        check_command=check_command,
                        validation_time=validation_time,
                        confidence=0.9
                    )
                else:
                    error_msg = f"Extension {tool_name} not found in installed extensions"
                    logger.warning(f"❌ {error_msg}")
                    
                    return ValidationResult(
                        tool_name=tool_name,
                        is_installed=False,
                        check_command=check_command,
                        error_message=error_msg,
                        validation_time=validation_time,
                        confidence=0.0
                    )
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Command failed"
                logger.warning(f"❌ Extension validation failed: {error_msg}")
                
                return ValidationResult(
                    tool_name=tool_name,
                    is_installed=False,
                    check_command=check_command,
                    error_message=error_msg,
                    validation_time=validation_time,
                    confidence=0.0
                )
                
        except Exception as e:
            validation_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"💥 Extension validation error: {error_msg}")
            
            return ValidationResult(
                tool_name=tool_name,
                is_installed=False,
                check_command=check_command,
                error_message=error_msg,
                validation_time=validation_time,
                confidence=0.0
            )
    
    def _get_extension_id(self, tool_name: str) -> Optional[str]:
        """
        Get the extension ID for a given tool name.
        
        Args:
            tool_name: Name of the extension
            
        Returns:
            Optional[str]: Extension ID or None
        """
        # Extension ID mappings
        extension_ids = {
            "GitHub Copilot": "GitHub.copilot",
            "Python Extension": "ms-python.python",
            "Jupyter Extension": "ms-toolsai.jupyter",
            "JavaScript Extension": "ms-vscode.vscode-typescript-next",
            "REST Client": "humao.rest-client",
            "YAML Extension": "redhat.vscode-yaml",
            "Markdownlint": "DavidAnson.vscode-markdownlint"
        }
        
        return extension_ids.get(tool_name)
    
    def _calculate_validation_confidence(self, tool_name: str, output: str) -> float:
        """
        Calculate confidence score for a validation result.
        
        Args:
            tool_name: Name of the tool
            output: Tool output
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        if not output:
            return 0.5
        
        # Base confidence
        confidence = 0.8
        
        # Increase confidence if version is found
        if self._extract_version(output, Tool(name=tool_name, install_command="", check_command="")):
            confidence += 0.1
        
        # Increase confidence if output contains expected keywords
        expected_keywords = {
            "python": ["python", "version"],
            "node": ["node", "version"],
            "git": ["git", "version"],
            "docker": ["docker", "version"],
            "code": ["code", "version"],
            "cursor": ["cursor", "version"]
        }
        
        tool_keywords = expected_keywords.get(tool_name.lower(), [])
        for keyword in tool_keywords:
            if keyword.lower() in output.lower():
                confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _generate_validation_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """
        Generate recommendations based on validation results.
        
        Args:
            results: List of validation results
            
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        failed_tools = [r for r in results if not r.is_installed]
        
        if failed_tools:
            recommendations.append(f"Found {len(failed_tools)} failed tools that may need attention.")
            
            # Check for common failure patterns
            timed_out_tools = [r for r in failed_tools if r.error_message and "timed out" in r.error_message]
            if timed_out_tools:
                recommendations.append("Some tools timed out during validation. Consider increasing timeout values.")
            
            command_failed_tools = [r for r in failed_tools if r.error_message and "Command failed" in r.error_message]
            if command_failed_tools:
                recommendations.append("Some tools failed command execution. Check if they are properly installed.")
        
        # Check success rate
        total_tools = len(results)
        successful_tools = len([r for r in results if r.is_installed])
        success_rate = (successful_tools / total_tools * 100) if total_tools > 0 else 0
        
        if success_rate < 80:
            recommendations.append("Low success rate detected. Consider reviewing installation procedures.")
        elif success_rate >= 95:
            recommendations.append("Excellent validation results! All tools are working correctly.")
        
        return recommendations
    
    def get_validation_summary(self, report: ValidationReport) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Args:
            report: Validation report
            
        Returns:
            Dict[str, Any]: Summary dictionary
        """
        return {
            "total_tools": report.total_tools,
            "successful_validations": report.successful_validations,
            "failed_validations": report.failed_validations,
            "skipped_validations": report.skipped_validations,
            "overall_success_rate": report.overall_success_rate,
            "recommendations": report.recommendations,
            "has_issues": report.failed_validations > 0,
            "status": "healthy" if report.failed_validations == 0 else "issues_detected"
        }
    
    def _attempt_smart_recovery(self, tool_name: str, original_command: str, error_msg: str) -> Optional[str]:
        """
        Attempt smart recovery for failed tool validation.
        
        Args:
            tool_name: Name of the tool that failed
            original_command: Original check command
            error_msg: Error message from failed validation
            
        Returns:
            Optional[str]: New command to try, or None if recovery failed
        """
        try:
            # Get recovery suggestions from LLM if available
            if self.llm_agent:
                recovery_command = self.llm_agent.generate_command_fix(
                    original_command, error_msg, tool_name
                )
                if recovery_command:
                    logger.info(f"🧠 LLM suggested recovery for {tool_name}: {recovery_command}")
                    return recovery_command
            
            # Fallback to common recovery patterns
            recovery_patterns = self._get_recovery_patterns(tool_name, error_msg)
            
            for pattern in recovery_patterns:
                if self._test_recovery_command(pattern):
                    logger.info(f"🔧 Found working recovery for {tool_name}: {pattern}")
                    return pattern
            
            logger.warning(f"❌ No recovery found for {tool_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error during smart recovery for {tool_name}: {e}")
            return None
    
    def _get_recovery_patterns(self, tool_name: str, error_msg: str) -> List[str]:
        """Get common recovery patterns for a tool."""
        tool_lower = tool_name.lower()
        patterns = []
        
        # Common recovery patterns based on tool and error
        if "command not found" in error_msg.lower():
            if "python" in tool_lower:
                patterns.extend([
                    "python3 --version",
                    "python --version",
                    "py --version"
                ])
            elif "node" in tool_lower:
                patterns.extend([
                    "node --version",
                    "nodejs --version"
                ])
            elif "git" in tool_lower:
                patterns.extend([
                    "git --version",
                    "git version"
                ])
            elif "docker" in tool_lower:
                patterns.extend([
                    "docker --version",
                    "docker version"
                ])
            elif "code" in tool_lower:
                patterns.extend([
                    "code --version",
                    "code -v"
                ])
        
        # Add tool-specific patterns
        if "python" in tool_lower:
            patterns.extend([
                "python3 -c 'import sys; print(sys.version)'",
                "python -c 'import sys; print(sys.version)'"
            ])
        elif "pip" in tool_lower:
            patterns.extend([
                "pip3 --version",
                "pip --version"
            ])
        elif "npm" in tool_lower:
            patterns.extend([
                "npm --version",
                "npm -v"
            ])
        
        return patterns
    
    def _test_recovery_command(self, command: str) -> bool:
        """Test if a recovery command works."""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False 