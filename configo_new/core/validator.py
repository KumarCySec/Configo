"""
CONFIGO Core Validator
======================

Handles post-installation validation and testing of installed tools.
Provides comprehensive validation reports and error diagnostics.
"""

import logging
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ValidationTest:
    """Represents a validation test for a tool."""
    name: str
    command: str
    expected_output: Optional[str] = None
    timeout: int = 30
    description: str = ""


@dataclass
class ValidationResult:
    """Result of a validation test."""
    test_name: str
    tool_name: str
    passed: bool
    output: str = ""
    error_message: Optional[str] = None
    execution_time: float = 0.0
    severity: str = "info"  # info, warning, error


class Validator:
    """
    Core validator for CONFIGO tools and installations.
    
    Performs comprehensive validation of installed tools and provides
    detailed reports with error diagnostics.
    """
    
    def __init__(self, config=None, knowledge_engine=None):
        """Initialize the validator."""
        self.config = config
        self.knowledge = knowledge_engine
        self.validation_tests = self._load_validation_tests()
        
        logger.info("CONFIGO Validator initialized")
    
    def _load_validation_tests(self) -> Dict[str, List[ValidationTest]]:
        """Load predefined validation tests for common tools."""
        tests = {
            'python': [
                ValidationTest(
                    name="python_version",
                    command="python --version",
                    description="Check Python version"
                ),
                ValidationTest(
                    name="pip_available",
                    command="pip --version",
                    description="Check pip availability"
                )
            ],
            'node': [
                ValidationTest(
                    name="node_version",
                    command="node --version",
                    description="Check Node.js version"
                ),
                ValidationTest(
                    name="npm_available",
                    command="npm --version",
                    description="Check npm availability"
                )
            ],
            'git': [
                ValidationTest(
                    name="git_version",
                    command="git --version",
                    description="Check Git version"
                ),
                ValidationTest(
                    name="git_config",
                    command="git config --list",
                    description="Check Git configuration"
                )
            ],
            'docker': [
                ValidationTest(
                    name="docker_version",
                    command="docker --version",
                    description="Check Docker version"
                ),
                ValidationTest(
                    name="docker_running",
                    command="docker ps",
                    description="Check Docker daemon"
                )
            ],
            'vscode': [
                ValidationTest(
                    name="code_version",
                    command="code --version",
                    description="Check VS Code CLI"
                )
            ],
            'java': [
                ValidationTest(
                    name="java_version",
                    command="java -version",
                    description="Check Java version"
                ),
                ValidationTest(
                    name="javac_available",
                    command="javac -version",
                    description="Check Java compiler"
                )
            ],
            'gcc': [
                ValidationTest(
                    name="gcc_version",
                    command="gcc --version",
                    description="Check GCC version"
                )
            ],
            'make': [
                ValidationTest(
                    name="make_version",
                    command="make --version",
                    description="Check Make version"
                )
            ]
        }
        
        return tests
    
    def validate_tool(self, tool_name: str) -> ValidationResult:
        """
        Validate a single tool.
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            ValidationResult: Validation result
        """
        # Get validation tests for this tool
        tests = self.validation_tests.get(tool_name.lower(), [])
        
        if not tests:
            # Create a basic test
            tests = [
                ValidationTest(
                    name="basic_check",
                    command=f"{tool_name} --version",
                    description=f"Basic validation for {tool_name}"
                )
            ]
        
        # Run all tests for the tool
        results = []
        for test in tests:
            result = self._run_validation_test(test, tool_name)
            results.append(result)
        
        # Aggregate results
        all_passed = all(r.passed for r in results)
        failed_tests = [r for r in results if not r.passed]
        
        if failed_tests:
            error_message = f"Validation failed for {tool_name}: {len(failed_tests)} tests failed"
        else:
            error_message = None
        
        return ValidationResult(
            test_name="comprehensive",
            tool_name=tool_name,
            passed=all_passed,
            error_message=error_message,
            execution_time=sum(r.execution_time for r in results)
        )
    
    def validate_installation(self, installation_results: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate a complete installation.
        
        Args:
            installation_results: Results from installation process
            
        Returns:
            List[ValidationResult]: Validation results for all tools
        """
        validation_results = []
        
        for result in installation_results:
            if result.get('success', False):
                tool_name = result.get('tool_name', 'unknown')
                validation_result = self.validate_tool(tool_name)
                validation_results.append(validation_result)
        
        return validation_results
    
    def _run_validation_test(self, test: ValidationTest, tool_name: str) -> ValidationResult:
        """
        Run a single validation test.
        
        Args:
            test: Validation test to run
            tool_name: Name of the tool being tested
            
        Returns:
            ValidationResult: Result of the test
        """
        start_time = time.time()
        
        try:
            # Execute the test command
            result = subprocess.run(
                test.command.split(),
                capture_output=True,
                text=True,
                timeout=test.timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # Test passed
                return ValidationResult(
                    test_name=test.name,
                    tool_name=tool_name,
                    passed=True,
                    output=result.stdout.strip(),
                    execution_time=execution_time
                )
            else:
                # Test failed
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                return ValidationResult(
                    test_name=test.name,
                    tool_name=tool_name,
                    passed=False,
                    output=result.stdout.strip(),
                    error_message=error_msg,
                    execution_time=execution_time,
                    severity="error"
                )
                
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ValidationResult(
                test_name=test.name,
                tool_name=tool_name,
                passed=False,
                error_message=f"Test timed out after {test.timeout} seconds",
                execution_time=execution_time,
                severity="error"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ValidationResult(
                test_name=test.name,
                tool_name=tool_name,
                passed=False,
                error_message=str(e),
                execution_time=execution_time,
                severity="error"
            )
    
    def validate_system_requirements(self) -> List[ValidationResult]:
        """Validate system requirements and dependencies."""
        system_tests = [
            ValidationTest(
                name="disk_space",
                command="df -h .",
                description="Check available disk space"
            ),
            ValidationTest(
                name="memory_usage",
                command="free -h",
                description="Check available memory"
            ),
            ValidationTest(
                name="network_connectivity",
                command="ping -c 1 8.8.8.8",
                description="Check network connectivity"
            ),
            ValidationTest(
                name="sudo_privileges",
                command="sudo -n true",
                description="Check sudo privileges"
            )
        ]
        
        results = []
        for test in system_tests:
            result = self._run_validation_test(test, "system")
            results.append(result)
        
        return results
    
    def validate_development_environment(self) -> List[ValidationResult]:
        """Validate common development environment components."""
        env_tests = [
            ValidationTest(
                name="python_environment",
                command="python --version",
                description="Check Python installation"
            ),
            ValidationTest(
                name="git_environment",
                command="git --version",
                description="Check Git installation"
            ),
            ValidationTest(
                name="package_manager",
                command="which apt-get || which yum || which dnf || which pacman",
                description="Check package manager availability"
            )
        ]
        
        results = []
        for test in env_tests:
            result = self._run_validation_test(test, "environment")
            results.append(result)
        
        return results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate a summary of validation results."""
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = len([r for r in results if not r.passed])
        
        # Group by tool
        tool_results = {}
        for result in results:
            tool_name = result.tool_name
            if tool_name not in tool_results:
                tool_results[tool_name] = []
            tool_results[tool_name].append(result)
        
        # Calculate success rates
        tool_success_rates = {}
        for tool_name, tool_tests in tool_results.items():
            passed = len([t for t in tool_tests if t.passed])
            total = len(tool_tests)
            tool_success_rates[tool_name] = passed / total if total > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'tool_results': tool_results,
            'tool_success_rates': tool_success_rates,
            'failed_tools': [tool for tool, rate in tool_success_rates.items() if rate < 1.0]
        }
    
    def diagnose_failures(self, results: List[ValidationResult]) -> List[Dict[str, Any]]:
        """Diagnose validation failures and provide suggestions."""
        failures = [r for r in results if not r.passed]
        diagnoses = []
        
        for failure in failures:
            # Get knowledge-based suggestions
            knowledge_suggestions = self._get_knowledge_suggestions(failure)
            
            diagnosis = {
                'tool_name': failure.tool_name,
                'test_name': failure.test_name,
                'error_message': failure.error_message,
                'suggestions': self._generate_suggestions(failure),
                'knowledge_suggestions': knowledge_suggestions
            }
            diagnoses.append(diagnosis)
        
        return diagnoses
    
    def _get_knowledge_suggestions(self, failure: ValidationResult) -> List[str]:
        """Get suggestions from knowledge base."""
        if not self.knowledge or not failure.error_message:
            return []
        
        try:
            # Search for similar errors in knowledge base
            error_results = self.knowledge.vector_manager.search_error(failure.error_message, 3)
            
            suggestions = []
            for result in error_results:
                content = result.get('content', '')
                if 'Solution:' in content:
                    # Extract solution from content
                    solution_start = content.find('Solution:')
                    if solution_start != -1:
                        solution = content[solution_start:].split('\n')[0].replace('Solution:', '').strip()
                        if solution:
                            suggestions.append(solution)
            
            return suggestions
        except Exception as e:
            logger.warning(f"Failed to get knowledge suggestions: {e}")
            return []
    
    def _generate_suggestions(self, failure: ValidationResult) -> List[str]:
        """Generate suggestions for fixing validation failures."""
        suggestions = []
        
        if "command not found" in failure.error_message.lower():
            suggestions.append(f"Install {failure.tool_name} using your package manager")
            suggestions.append(f"Check if {failure.tool_name} is in your PATH")
        
        elif "permission denied" in failure.error_message.lower():
            suggestions.append("Run the command with sudo privileges")
            suggestions.append("Check file permissions")
        
        elif "timeout" in failure.error_message.lower():
            suggestions.append("Check system resources (CPU, memory, disk)")
            suggestions.append("Verify network connectivity")
        
        elif "version" in failure.test_name.lower():
            suggestions.append(f"Update {failure.tool_name} to a newer version")
            suggestions.append("Check if the tool is properly installed")
        
        else:
            suggestions.append("Check the tool installation")
            suggestions.append("Verify system requirements")
            suggestions.append("Check for conflicting installations")
        
        return suggestions 