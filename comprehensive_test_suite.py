#!/usr/bin/env python3
"""
CONFIGO Comprehensive Test Suite
================================

Systematic testing of all CONFIGO features including:
- Environment detection and stack planning
- App installation via natural language
- Chat mode functionality
- Memory features
- Self-healing installation
- Tool detection
- Validation reports
- Edge cases and error handling
- Browser login prompts
- Terminal UI and readability
"""

import os
import sys
import subprocess
import time
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import CONFIGO components
from core.memory import AgentMemory
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.app_name_extractor import AppNameExtractor
from core.validator import ToolValidator
from core.project_scanner import ProjectScanner
from core.chat_agent import ChatAgent
from ui.enhanced_messages import EnhancedMessageDisplay
from rich.console import Console

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_suite.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CONFIGOTestSuite:
    """Comprehensive test suite for CONFIGO AI Agent."""
    
    def __init__(self):
        self.console = Console()
        self.messages = EnhancedMessageDisplay(self.console)
        self.memory = AgentMemory()
        self.llm_agent = EnhancedLLMAgent(self.memory)
        self.validator = ToolValidator(self.memory, self.llm_agent)
        self.project_scanner = ProjectScanner(self.memory)
        self.chat_agent = ChatAgent(self.memory)
        
        self.test_results = {
            'passed': [],
            'failed': [],
            'skipped': [],
            'total_tests': 0
        }
        
        logger.info("CONFIGO Test Suite initialized")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories and return comprehensive results."""
        logger.info("🚀 Starting CONFIGO Comprehensive Test Suite")
        
        test_categories = [
            ("Environment Detection & Stack Planning", self.test_environment_detection),
            ("App Name Extraction", self.test_app_name_extraction),
            ("Memory System", self.test_memory_system),
            ("Chat Mode", self.test_chat_mode),
            ("Project Scanning", self.test_project_scanning),
            ("Validation System", self.test_validation_system),
            ("Error Handling", self.test_error_handling),
            ("UI Components", self.test_ui_components),
            ("Integration Tests", self.test_integration),
        ]
        
        for category_name, test_func in test_categories:
            logger.info(f"\n📋 Testing: {category_name}")
            try:
                test_func()
            except Exception as e:
                logger.error(f"❌ Test category {category_name} failed: {e}")
                self.test_results['failed'].append({
                    'category': category_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return self.generate_test_report()
    
    def test_environment_detection(self):
        """Test environment detection and stack planning."""
        logger.info("🧠 Testing Environment Detection & Stack Planning")
        
        test_environments = [
            "Full Stack AI Developer on Linux",
            "Web Developer",
            "Data Scientist",
            "DevOps Engineer",
            "Mobile Developer"
        ]
        
        for env in test_environments:
            try:
                logger.info(f"Testing environment: {env}")
                
                # Test LLM agent response
                response = self.llm_agent.generate_enhanced_stack(env)
                
                # Validate response structure
                assert hasattr(response, 'tools'), "Response missing tools"
                assert hasattr(response, 'login_portals'), "Response missing login_portals"
                assert hasattr(response, 'confidence_score'), "Response missing confidence_score"
                
                # Check for reasonable tool count
                assert len(response.tools) > 0, f"No tools generated for {env}"
                assert response.confidence_score >= 0.0, "Invalid confidence score"
                assert response.confidence_score <= 1.0, "Invalid confidence score"
                
                # Test domain detection
                detected_domain = response.domain_completion.get("detected_domain", "unknown")
                assert detected_domain in ["ai_ml", "web_dev", "data_science", "devops", "unknown"], f"Invalid domain: {detected_domain}"
                
                self.test_results['passed'].append({
                    'test': f"Environment Detection - {env}",
                    'details': f"Generated {len(response.tools)} tools, confidence: {response.confidence_score:.2f}",
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"✅ Environment detection passed for: {env}")
                
            except Exception as e:
                logger.error(f"❌ Environment detection failed for {env}: {e}")
                self.test_results['failed'].append({
                    'test': f"Environment Detection - {env}",
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    def test_app_name_extraction(self):
        """Test app name extraction from natural language."""
        logger.info("📦 Testing App Name Extraction")
        
        test_cases = [
            ("Install Telegram", "Telegram"),
            ("Get me Slack", "Slack"),
            ("I need Chrome", "Google Chrome"),
            ("Please install VS Code", "VS Code"),
            ("Download Docker", "Docker"),
            ("Setup Python", "Python"),
            ("Add Node.js to my system", "Node.js"),
            ("Install the Postman app", "Postman"),
            ("Get Jupyter for me", "Jupyter"),
            ("I want to install Git", "Git")
        ]
        
        for input_text, expected_output in test_cases:
            try:
                extracted_name = AppNameExtractor.extract_app_name(input_text)
                
                # Validate extraction
                assert extracted_name, f"No app name extracted from: {input_text}"
                assert extracted_name.lower() in expected_output.lower() or expected_output.lower() in extracted_name.lower(), \
                    f"Extraction mismatch: expected '{expected_output}', got '{extracted_name}'"
                
                self.test_results['passed'].append({
                    'test': f"App Extraction - {input_text}",
                    'details': f"Extracted: {extracted_name}",
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"✅ App extraction passed: '{input_text}' -> '{extracted_name}'")
                
            except Exception as e:
                logger.error(f"❌ App extraction failed for '{input_text}': {e}")
                self.test_results['failed'].append({
                    'test': f"App Extraction - {input_text}",
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    def test_memory_system(self):
        """Test memory system functionality."""
        logger.info("🧠 Testing Memory System")
        
        try:
            # Test session management
            session_id = self.memory.start_session("Test Environment")
            assert session_id, "Failed to create session"
            
            # Test tool installation recording
            self.memory.record_tool_installation(
                tool_name="TestTool",
                install_command="echo 'test'",
                check_command="test --version",
                success=True,
                version="1.0.0"
            )
            
            # Test memory context retrieval
            context = self.memory.get_memory_context()
            assert context, "Failed to get memory context"
            
            # Test tool memory retrieval
            tool_memory = self.memory.get_tool_memory("TestTool")
            assert tool_memory, "Failed to retrieve tool memory"
            assert tool_memory.name == "TestTool", "Tool memory name mismatch"
            assert tool_memory.install_success, "Tool memory success flag incorrect"
            
            # Test session completion
            self.memory.end_session(session_id)
            
            # Test memory statistics
            stats = self.memory.get_memory_stats()
            assert 'total_tools' in stats, "Memory stats missing total_tools"
            assert 'successful_installations' in stats, "Memory stats missing successful_installations"
            
            self.test_results['passed'].append({
                'test': "Memory System - Core Functionality",
                'details': f"Session: {session_id}, Tools: {stats.get('total_tools', 0)}",
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("✅ Memory system tests passed")
            
        except Exception as e:
            logger.error(f"❌ Memory system test failed: {e}")
            self.test_results['failed'].append({
                'test': "Memory System - Core Functionality",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def test_chat_mode(self):
        """Test chat mode functionality."""
        logger.info("💬 Testing Chat Mode")
        
        test_questions = [
            "Who are you?",
            "What can you do?",
            "Do you know Python?",
            "What is Docker?",
            "How do I install Git?"
        ]
        
        for question in test_questions:
            try:
                # Test chat agent response
                response = self.chat_agent.process_message(question)
                
                # Validate response
                assert response, f"No response for question: {question}"
                assert hasattr(response, 'message'), "Response missing message attribute"
                assert len(response.message) > 10, f"Response too short: {response.message}"
                
                self.test_results['passed'].append({
                    'test': f"Chat Mode - {question}",
                    'details': f"Response length: {len(response.message)} chars, type: {response.action_type}",
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"✅ Chat response for '{question}': {response.message[:50]}...")
                
            except Exception as e:
                logger.error(f"❌ Chat mode failed for '{question}': {e}")
                self.test_results['failed'].append({
                    'test': f"Chat Mode - {question}",
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    def test_project_scanning(self):
        """Test project scanning functionality."""
        logger.info("🔍 Testing Project Scanning")
        
        try:
            # Test project scanning
            scan_result = self.project_scanner.scan_project()
            
            # Validate scan result
            assert scan_result is not None, "Project scan returned None"
            
            # Test scan result structure
            if isinstance(scan_result, dict):
                assert 'languages' in scan_result, "Scan result missing languages"
                assert 'frameworks' in scan_result, "Scan result missing frameworks"
                assert 'tools' in scan_result, "Scan result missing tools"
            
            self.test_results['passed'].append({
                'test': "Project Scanning",
                'details': f"Scan completed successfully",
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("✅ Project scanning test passed")
            
        except Exception as e:
            logger.error(f"❌ Project scanning test failed: {e}")
            self.test_results['failed'].append({
                'test': "Project Scanning",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def test_validation_system(self):
        """Test validation system functionality."""
        logger.info("✅ Testing Validation System")
        
        try:
            # Test validation with mock tools
            mock_tools = [
                {
                    'name': 'python',
                    'install_command': 'apt-get install python3',
                    'check_command': 'python3 --version',
                    'is_extension': False
                },
                {
                    'name': 'git',
                    'install_command': 'apt-get install git',
                    'check_command': 'git --version',
                    'is_extension': False
                }
            ]
            
            # Test validation report generation
            validation_report = self.validator.validate_tools(mock_tools)
            
            # Validate report structure
            assert hasattr(validation_report, 'total_tools'), "Validation report missing total_tools"
            assert hasattr(validation_report, 'validation_results'), "Validation report missing validation_results"
            assert hasattr(validation_report, 'overall_success_rate'), "Validation report missing overall_success_rate"
            
            self.test_results['passed'].append({
                'test': "Validation System",
                'details': f"Validated {validation_report.total_tools} tools",
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("✅ Validation system test passed")
            
        except Exception as e:
            logger.error(f"❌ Validation system test failed: {e}")
            self.test_results['failed'].append({
                'test': "Validation System",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        logger.info("🛡️ Testing Error Handling")
        
        try:
            # Test with invalid environment
            response = self.llm_agent.generate_enhanced_stack("")
            assert response is not None, "Should handle empty environment gracefully"
            
            # Test with invalid app name
            extracted_name = AppNameExtractor.extract_app_name("")
            assert extracted_name == "", "Should handle empty input gracefully"
            
            # Test memory with invalid data
            self.memory.record_tool_installation(
                tool_name="",
                install_command="",
                check_command="",
                success=False,
                error="Test error"
            )
            
            self.test_results['passed'].append({
                'test': "Error Handling",
                'details': "Handled edge cases gracefully",
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("✅ Error handling tests passed")
            
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            self.test_results['failed'].append({
                'test': "Error Handling",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def test_ui_components(self):
        """Test UI components and message display."""
        logger.info("🎨 Testing UI Components")
        
        try:
            # Test message display
            self.messages.show_autonomous_banner()
            
            # Test memory context display
            self.messages.show_memory_context(self.memory)
            
            # Test error message display
            self.messages.show_error_with_context("Test error message")
            
            self.test_results['passed'].append({
                'test': "UI Components",
                'details': "UI components rendered successfully",
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("✅ UI components test passed")
            
        except Exception as e:
            logger.error(f"❌ UI components test failed: {e}")
            self.test_results['failed'].append({
                'test': "UI Components",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def test_integration(self):
        """Test integration between components."""
        logger.info("🔗 Testing Integration")
        
        try:
            # Test full workflow simulation
            env = "Test Developer Environment"
            
            # 1. Start session
            session_id = self.memory.start_session(env)
            
            # 2. Generate stack
            response = self.llm_agent.generate_enhanced_stack(env)
            
            # 3. Extract app name
            app_name = AppNameExtractor.extract_app_name("Install TestApp")
            
            # 4. Record installation
            self.memory.record_tool_installation(
                tool_name=app_name,
                install_command="echo 'test install'",
                check_command="echo 'test check'",
                success=True
            )
            
            # 5. Validate
            validation_report = self.validator.validate_tools([{
                'name': app_name,
                'install_command': "echo 'test'",
                'check_command': "echo 'test'",
                'is_extension': False
            }])
            
            # 6. End session
            self.memory.end_session(session_id)
            
            self.test_results['passed'].append({
                'test': "Integration - Full Workflow",
                'details': f"Completed workflow with {len(response.tools)} tools",
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("✅ Integration test passed")
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            self.test_results['failed'].append({
                'test': "Integration - Full Workflow",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results['passed']) + len(self.test_results['failed']) + len(self.test_results['skipped'])
        success_rate = (len(self.test_results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': len(self.test_results['passed']),
                'failed': len(self.test_results['failed']),
                'skipped': len(self.test_results['skipped']),
                'success_rate': f"{success_rate:.1f}%",
                'timestamp': datetime.now().isoformat()
            },
            'passed_tests': self.test_results['passed'],
            'failed_tests': self.test_results['failed'],
            'skipped_tests': self.test_results['skipped']
        }
        
        # Save report to file
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary to console."""
        summary = report['summary']
        
        print("\n" + "="*60)
        print("🧪 CONFIGO COMPREHENSIVE TEST SUITE RESULTS")
        print("="*60)
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"📈 Success Rate: {summary['success_rate']}")
        print("="*60)
        
        if report['failed_tests']:
            print("\n❌ FAILED TESTS:")
            for test in report['failed_tests']:
                print(f"  • {test['test']}: {test['error']}")
        
        if report['passed_tests']:
            print(f"\n✅ PASSED TESTS ({len(report['passed_tests'])}):")
            for test in report['passed_tests'][:5]:  # Show first 5
                print(f"  • {test['test']}")
            if len(report['passed_tests']) > 5:
                print(f"  ... and {len(report['passed_tests']) - 5} more")
        
        print(f"\n📄 Detailed report saved to: test_report.json")
        print("="*60)

def main():
    """Main test execution function."""
    test_suite = CONFIGOTestSuite()
    
    try:
        report = test_suite.run_all_tests()
        test_suite.print_summary(report)
        
        # Exit with appropriate code
        if report['summary']['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 