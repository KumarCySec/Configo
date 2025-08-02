"""
Tests for CONFIGO Installer Module
==================================

Tests the core installer functionality including tool installation,
validation, and retry logic.
"""

import pytest
from unittest.mock import Mock, patch
from core.installer import Installer, InstallationStep, InstallationResult


class TestInstaller:
    """Test cases for the Installer class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.installer = Installer()
    
    def test_initialization(self):
        """Test installer initialization."""
        assert self.installer is not None
        assert hasattr(self.installer, 'installed_tools')
        assert hasattr(self.installer, 'failed_installations')
        assert hasattr(self.installer, 'package_managers')
    
    def test_detect_package_managers(self):
        """Test package manager detection."""
        managers = self.installer._detect_package_managers()
        assert isinstance(managers, dict)
        assert 'apt-get' in managers or 'yum' in managers or 'dnf' in managers
    
    @patch('subprocess.run')
    def test_is_tool_installed_success(self, mock_run):
        """Test tool installation check - success case."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "git version 2.39.2"
        
        result = self.installer._is_tool_installed('git')
        assert result is True
    
    @patch('subprocess.run')
    def test_is_tool_installed_failure(self, mock_run):
        """Test tool installation check - failure case."""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.installer._is_tool_installed('nonexistent-tool')
        assert result is False
    
    @patch('subprocess.run')
    def test_get_tool_version(self, mock_run):
        """Test getting tool version."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "git version 2.39.2"
        
        version = self.installer._get_tool_version('git')
        assert version == "git version 2.39.2"
    
    def test_install_tool_basic(self):
        """Test basic tool installation."""
        plan = {
            'name': 'test-tool',
            'command': 'echo "test"',
            'description': 'Test tool installation'
        }
        
        with patch.object(self.installer, '_execute_installation_step') as mock_execute:
            mock_execute.return_value = InstallationResult(
                success=True,
                tool_name='test-tool',
                version='1.0.0'
            )
            
            result = self.installer.install_tool(plan)
            assert result.success is True
            assert result.tool_name == 'test-tool'
    
    def test_execute_plan(self):
        """Test executing installation plan."""
        plan = {
            'steps': [
                {
                    'name': 'step1',
                    'command': 'echo "step1"',
                    'description': 'First step'
                },
                {
                    'name': 'step2',
                    'command': 'echo "step2"',
                    'description': 'Second step'
                }
            ]
        }
        
        with patch.object(self.installer, '_execute_installation_step') as mock_execute:
            mock_execute.return_value = InstallationResult(
                success=True,
                tool_name='test-tool'
            )
            
            results = self.installer.execute_plan(plan)
            assert len(results) == 2
            assert all(r.success for r in results)
    
    def test_get_installation_stats(self):
        """Test getting installation statistics."""
        # Add some mock data
        self.installer.installed_tools['git'] = InstallationResult(
            success=True, tool_name='git'
        )
        self.installer.failed_installations['failed-tool'] = InstallationResult(
            success=False, tool_name='failed-tool'
        )
        
        stats = self.installer.get_installation_stats()
        assert stats['total_installations'] == 2
        assert stats['successful_installations'] == 1
        assert stats['failed_installations'] == 1
        assert stats['success_rate'] == 0.5
    
    def test_retry_failed_installations(self):
        """Test retrying failed installations."""
        # Add a failed installation
        self.installer.failed_installations['failed-tool'] = InstallationResult(
            success=False,
            tool_name='failed-tool',
            command_output='echo "retry"'
        )
        
        with patch.object(self.installer, 'install_tool') as mock_install:
            mock_install.return_value = InstallationResult(
                success=True,
                tool_name='failed-tool'
            )
            
            results = self.installer.retry_failed_installations()
            assert len(results) == 1
            assert results[0].success is True


class TestInstallationStep:
    """Test cases for InstallationStep dataclass."""
    
    def test_installation_step_creation(self):
        """Test creating an installation step."""
        step = InstallationStep(
            name='test-step',
            command='echo "test"',
            description='Test step'
        )
        
        assert step.name == 'test-step'
        assert step.command == 'echo "test"'
        assert step.description == 'Test step'
        assert step.timeout == 300  # Default value
        assert step.retry_count == 0  # Default value
        assert step.max_retries == 3  # Default value
    
    def test_installation_step_with_dependencies(self):
        """Test installation step with dependencies."""
        step = InstallationStep(
            name='test-step',
            command='echo "test"',
            description='Test step',
            dependencies=['dep1', 'dep2']
        )
        
        assert 'dep1' in step.dependencies
        assert 'dep2' in step.dependencies


class TestInstallationResult:
    """Test cases for InstallationResult dataclass."""
    
    def test_installation_result_success(self):
        """Test successful installation result."""
        result = InstallationResult(
            success=True,
            tool_name='test-tool',
            version='1.0.0',
            execution_time=5.0
        )
        
        assert result.success is True
        assert result.tool_name == 'test-tool'
        assert result.version == '1.0.0'
        assert result.execution_time == 5.0
        assert result.error_message is None
    
    def test_installation_result_failure(self):
        """Test failed installation result."""
        result = InstallationResult(
            success=False,
            tool_name='test-tool',
            error_message='Package not found',
            retry_count=2
        )
        
        assert result.success is False
        assert result.tool_name == 'test-tool'
        assert result.error_message == 'Package not found'
        assert result.retry_count == 2


if __name__ == '__main__':
    pytest.main([__file__]) 