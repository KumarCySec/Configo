#!/usr/bin/env python3
"""
CONFIGO - Intelligent Development Environment Agent
===================================================

🚀 A professional AI-powered CLI tool that intelligently sets up development environments
with memory, planning, self-healing, and validation capabilities.

Features:
- 🧠 Memory-aware recommendations using mem0ai
- 🤖 LLM-powered stack generation via Gemini
- 🔧 Self-healing installation with retry logic
- ✅ Post-installation validation
- 🎯 Domain-aware tool recommendations
- 🌐 Browser-based login portal orchestration
- 💬 Interactive chat mode
- 🔍 Project scanning and analysis
- 📦 Natural language app installation

Usage:
    configo                    # Interactive mode with welcome screen
    configo setup             # Full development environment setup
    configo chat              # Interactive AI chat assistant
    configo scan              # Project analysis and recommendations
    configo install <app>     # Natural language app installation
    configo portals           # Login portal orchestration
    configo diagnostics       # System diagnostics and health check
    configo help              # Show detailed help
"""

import argparse
import logging
import os
import sys
import time
import webbrowser
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Core agent components
from core.memory import AgentMemory
from core.planner import PlanGenerator, PlanExecutor, InstallationPlan
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.validator import ToolValidator, ValidationReport
from core.project_scan import scan_project
from core.chat_agent import ChatAgent
from core.project_scanner import ProjectScanner
from core.portal_orchestrator import PortalOrchestrator
from core.system_inspector import SystemInspector, display_system_summary
from core.shell_executor import ShellExecutor
from core.app_name_extractor import AppNameExtractor

# UI components
from ui.modern_terminal_ui import ModernTerminalUI, UIConfig, Theme
from ui.settings_menu import SettingsMenu

# Installation utilities
from installers.base import install_tools


def setup_logging() -> None:
    """Configure logging for the autonomous agent."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('configo.log')
        ]
    )


def execute_tool_installation(step, ui: ModernTerminalUI) -> bool:
    """Execute a tool installation step."""
    try:
        # Execute the installation command using the installer utility
        result = install_tools([{
            'name': step.name,
            'install_command': step.install_command,
            'check_command': step.check_command
        }])
        
        # Extract results from installation
        success = result.get('success', False)
        version = result.get('version')
        error = result.get('error')
        
        # Record installation result in memory for future reference
        memory = AgentMemory()
        memory.record_tool_installation(
            tool_name=step.name,
            install_command=step.install_command,
            check_command=step.check_command,
            success=success,
            version=version,
            error=error
        )
        
        return success
        
    except Exception as e:
        logging.error(f"Error installing tool {step.name}: {e}")
        return False


def execute_extension_installation(step, ui: ModernTerminalUI) -> bool:
    """Execute a VS Code/Cursor extension installation step."""
    try:
        # For now, we'll use the same logic as tool installation
        return execute_tool_installation(step, ui)
        
    except Exception as e:
        logging.error(f"Error installing extension {step.name}: {e}")
        return False


def execute_login_portal(step, ui: ModernTerminalUI) -> bool:
    """Execute a login portal step by opening the browser."""
    try:
        # Extract URL from step data
        portal_data = step.data if hasattr(step, 'data') else {}
        url = portal_data.get('url', '')
        
        if url:
            # Open the URL in the default browser
            webbrowser.open(url)
            ui.show_info_message(f"Opened login portal for {step.name}", "🌐")
            return True
        else:
            logging.error(f"No URL found for login portal {step.name}")
            return False
            
    except Exception as e:
        logging.error(f"Error opening login portal {step.name}: {e}")
        return False


def execute_validation(step, ui: ModernTerminalUI) -> bool:
    """Execute a validation step to verify tool installation."""
    try:
        memory = AgentMemory()
        llm_agent = EnhancedLLMAgent(memory)
        validator = ToolValidator(memory, llm_agent)
        
        # Validate the tool using the check command
        result = validator._validate_regular_tool(step.name, step.check_command)
        return result.is_installed
        
    except Exception as e:
        logging.error(f"Error validating tool {step.name}: {e}")
        return False


def get_tool_version(tool_name: str, check_command: str) -> Optional[str]:
    """Get the version of an installed tool."""
    try:
        # Execute the check command with timeout
        result = subprocess.run(
            check_command.split(),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extract version from output (basic implementation)
            output = result.stdout.strip()
            if output:
                # Take the first word as version (can be enhanced)
                return output.split()[0] if output.split() else None
        return None
        
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout getting version for {tool_name}")
        return None
    except Exception as e:
        logging.error(f"Error getting version for {tool_name}: {e}")
        return None 


def run_full_setup(ui: ModernTerminalUI, debug: bool = False, lite_mode: bool = False) -> None:
    """Run the full development environment setup."""
    ui.show_banner()
    ui.show_mode_header('Full Setup', 'Complete development environment setup')
    
    try:
        # Initialize memory system
        ui.show_info_message("Initializing memory system...")
        memory = AgentMemory()
        
        # Perform system intelligence analysis
        ui.show_info_message("Analyzing system environment...")
        system_inspector = SystemInspector()
        system_info = system_inspector.analyze()
        
        # Display system information
        ui.show_system_info(system_info)
        
        # Save system intelligence to memory
        system_inspector.save_to_memory(system_info)
        
        # Display memory context and statistics
        memory_stats = memory.get_memory_stats()
        ui.show_memory_stats(memory_stats)
        
        # Get user environment requirements
        env = ui.get_user_input("What type of development environment do you need? (e.g., web development, data science, mobile development): ")
        if not env:
            ui.show_error_message("No environment specified. Exiting.")
            return
        
        # Start tracking this session
        session_id = memory.start_session(env)
        logging.info(f"Started session: {session_id}")
        
        # Scan current project for context
        logging.info("Performing project scan")
        stack_info = scan_project()
        
        # Initialize LLM agent for intelligent recommendations
        ui.show_info_message("Initializing AI agent...")
        llm_agent = EnhancedLLMAgent(memory)
        
        # Generate AI-powered stack recommendations
        ui.show_info_message("Generating AI-powered recommendations...")
        llm_response = llm_agent.generate_enhanced_stack(env, str(stack_info) if stack_info else "", debug=debug)
        
        # Convert LLM response to tool list format
        tools = []
        for tool in llm_response.tools:
            tool_dict = {
                'name': tool.name,
                'install_command': tool.install_command,
                'check_command': tool.check_command,
                'is_extension': tool.is_extension,
                'extension_id': tool.extension_id,
                'justification': tool.justification,
                'confidence_score': tool.confidence_score,
                'priority': tool.priority
            }
            tools.append(tool_dict)
        
        ui.show_success_message(f"Generated {len(tools)} tools and {len(llm_response.login_portals)} login portals")
        
        # Show domain detection results
        detected_domain = llm_response.domain_completion.get("detected_domain", "unknown")
        ui.show_ai_reasoning(
            f"Domain Detection: {detected_domain.title()}",
            f"Based on project analysis and AI reasoning, CONFIGO detected this as a {detected_domain} project.",
            llm_response.confidence_score
        )
        
        # Generate intelligent installation plan
        ui.show_info_message("Generating installation plan...")
        plan_generator = PlanGenerator()
        memory_context = memory.get_memory_context()
        plan = plan_generator.generate_plan(tools, env, memory_context)
        
        # Display the plan to user
        plan_steps = []
        for step in plan.steps:
            step_dict = {
                'name': step.name,
                'description': step.description,
                'sub_steps': [step.step_type.value] if step.step_type else []
            }
            plan_steps.append(step_dict)
        ui.show_planning_steps(plan_steps)
        
        # Show login portals that will be opened
        if llm_response.login_portals:
            ui.show_info_message(
                f"Will open {len(llm_response.login_portals)} login portal(s) during installation",
                "🌐"
            )
        
        # Display improvement suggestions
        if llm_response.improvement_suggestions:
            suggestions_text = "\n".join([f"• {suggestion}" for suggestion in llm_response.improvement_suggestions])
            ui.show_ai_reasoning(
                "Improvement Suggestions",
                suggestions_text,
                0.9
            )
        
        # Get user confirmation before proceeding
        if not ui.confirm_action("Proceed with installation?"):
            ui.show_info_message("Installation cancelled")
            memory.end_session(session_id)
            return
        
        # Initialize execution components
        executor = PlanExecutor(plan)
        validator = ToolValidator(memory, llm_agent)
        
        # Execute the installation plan
        logging.info("Starting plan execution")
        ui.show_info_message("Starting installation process...", "🚀")
        
        installed_tools = []
        failed_tools = []
        
        # Process each step in the plan
        while not executor.is_complete():
            step = executor.get_next_step()
            if not step:
                break
            
            # Skip if tool should be skipped based on memory
            if memory.should_skip_tool(step.name):
                executor.skip_step(step, "Already installed or max retries reached")
                continue
            
            # Start executing the step
            executor.start_step(step)
            current_step = executor.plan.completed_steps + executor.plan.failed_steps + 1
            
            # Show progress with enhanced UI
            ui.show_info_message(f"Installing {step.name}...", "🔧")
            
            try:
                # Execute based on step type
                if step.step_type.value == "tool_install":
                    success = execute_tool_installation(step, ui)
                elif step.step_type.value == "extension_install":
                    success = execute_extension_installation(step, ui)
                elif step.step_type.value == "login_portal":
                    success = execute_login_portal(step, ui)
                elif step.step_type.value == "validation":
                    success = execute_validation(step, ui)
                else:
                    success = False
                
                if success:
                    # Get version info and mark as complete
                    version = get_tool_version(step.name, step.check_command)
                    executor.complete_step(step, version)
                    installed_tools.append(step.name)
                    ui.show_success_message(f"{step.name} installed successfully", f"Version: {version}" if version else None)
                else:
                    # Mark as failed and attempt self-healing
                    executor.fail_step(step, "Installation failed")
                    failed_tools.append(step.name)
                    ui.show_error_message(f"Failed to install {step.name}", "Will attempt self-healing")
                    
                    # Attempt self-healing if retries are allowed
                    if memory.should_retry_tool(step.name):
                        ui.show_info_message(f"Retrying {step.name} (attempt {step.retry_count + 1}/{step.max_retries})", "🔄")
                        if executor.retry_step(step):
                            continue
                
            except Exception as e:
                logging.error(f"Error executing step {step.name}: {e}")
                executor.fail_step(step, str(e))
                failed_tools.append(step.name)
                ui.show_error_message(f"Step failed", str(e))
        
        # Update session with final results
        memory.update_session_tools(session_id, installed_tools, failed_tools)
        memory.update_session_portals(session_id, [portal["name"] for portal in llm_response.login_portals])
        
        # Perform post-installation validation
        logging.info("Performing post-installation validation")
        validation_report = validator.validate_tools(tools)
        
        # Convert validation results to UI format
        validation_results = []
        for result in validation_report.validation_results:
            result_dict = {
                'name': result.tool_name,
                'valid': result.is_installed,
                'version': result.version if hasattr(result, 'version') else 'N/A',
                'details': result.error_message if hasattr(result, 'error_message') else ''
            }
            validation_results.append(result_dict)
        
        ui.show_validation_results(validation_results)
        
        # Attempt self-healing for failed tools
        healing_results = []
        if failed_tools:
            logging.info("Attempting self-healing for failed tools")
            ui.show_info_message(f"Attempting to fix {len(failed_tools)} failed installation(s)...", "🔧")
            
            # Use LLM agent to generate fixes
            for failed_tool in failed_tools:
                fix_command = llm_agent.generate_command_fix(failed_tool, "Installation failed", failed_tool)
                if fix_command:
                    ui.show_info_message(f"Trying LLM-generated fix for {failed_tool}", "🤖")
                    # Create a temporary step for the fix command
                    temp_step = type('Step', (), {
                        'name': failed_tool,
                        'install_command': fix_command,
                        'check_command': f"{failed_tool} --version" if failed_tool else "echo 'check'"
                    })()
                    success = execute_tool_installation(temp_step, ui)
                    healing_results.append({
                        'tool': failed_tool,
                        'fix_command': fix_command,
                        'success': success
                    })
                    if success:
                        ui.show_success_message(f"Fixed {failed_tool} with LLM-generated command")
                    else:
                        ui.show_error_message(f"Failed to fix {failed_tool}", "Manual intervention may be required")
        
        # Show final completion summary
        summary = {
            'tools_installed': len(installed_tools),
            'validations_passed': len([r for r in validation_results if r['valid']]),
            'portals_opened': len(llm_response.login_portals),
            'total_time': 'N/A',  # Could be calculated if we track start time
            'suggestions': llm_response.improvement_suggestions if hasattr(llm_response, 'improvement_suggestions') else []
        }
        ui.show_completion_summary(summary)
        
        # End the session
        memory.end_session(session_id)
        
        logging.info("CONFIGO setup completed successfully")
        
    except Exception as e:
        logging.error(f"Error in full setup: {e}")
        ui.show_error_message("Setup failed", str(e))


def run_chat_mode(ui: ModernTerminalUI, debug: bool = False) -> None:
    """Run interactive chat mode."""
    ui.show_banner()
    ui.show_mode_header('Chat', 'Interactive AI chat assistant')
    
    try:
        # Initialize components
        memory = AgentMemory()
        chat_agent = ChatAgent(memory, debug_mode=debug)
        
        # Show chat interface
        ui.show_chat_interface("Chat with CONFIGO - Ask me anything about development tools and setup!")
        
        if debug:
            ui.show_info_message("🔍 Debug mode enabled - LLM input/output will be shown")
        
        # Chat loop
        while True:
            try:
                user_input = ui.get_user_input("💬 You: ")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    ui.show_success_message("Goodbye! Thanks for using CONFIGO.")
                    break
                
                # Process message
                response = chat_agent.process_message(user_input)
                ui.show_chat_response(response.message if hasattr(response, 'message') else str(response), is_ai=True)
                
                # Execute command if needed
                if hasattr(response, 'action_type') and response.action_type == "command" and hasattr(response, 'command') and response.command:
                    if hasattr(response, 'requires_confirmation') and response.requires_confirmation:
                        if not ui.confirm_action(f"Execute: {response.command}?"):
                            continue
                    
                    success, output = chat_agent.execute_command(response.command)
                    if success:
                        ui.show_success_message("Command executed successfully!")
                    else:
                        ui.show_error_message("Command failed", output)
                
            except KeyboardInterrupt:
                ui.show_success_message("Goodbye! Thanks for using CONFIGO.")
                break
            except Exception as e:
                ui.show_error_message("Error processing message", str(e))
                
    except Exception as e:
        logging.error(f"Chat mode failed: {e}")
        ui.show_error_message("Chat mode failed", str(e))


def run_scan_mode(ui: ModernTerminalUI, debug: bool = False) -> None:
    """Run project scanning mode."""
    ui.show_banner()
    ui.show_mode_header('Scan', 'Project analysis and recommendations')
    
    try:
        # Initialize components
        memory = AgentMemory()
        project_scanner = ProjectScanner(memory)
        
        # Scan project
        ui.show_info_message("Scanning project for technologies and frameworks...")
        analysis = project_scanner.scan_project(".")
        
        # Show results
        ui.show_ai_reasoning(
            f"Project Analysis: {analysis.project_type.title()}",
            f"Detected frameworks: {', '.join(analysis.detected_frameworks) if analysis.detected_frameworks else 'None'}\n"
            f"Languages: {', '.join(analysis.languages) if analysis.languages else 'None'}\n"
            f"Confidence: {analysis.confidence:.1%}",
            analysis.confidence
        )
        
        # Show recommendations
        if analysis.recommendations:
            recommendations_text = "\n".join([f"• {rec}" for rec in analysis.recommendations])
            ui.show_ai_reasoning("Recommendations", recommendations_text, 0.9)
        
    except Exception as e:
        logging.error(f"Scan mode failed: {e}")
        ui.show_error_message("Scan mode failed", str(e))


def run_portal_mode(ui: ModernTerminalUI, debug: bool = False) -> None:
    """Run portal orchestration mode."""
    ui.show_banner()
    ui.show_mode_header('Portal', 'Login portal orchestration')
    
    try:
        # Initialize portal orchestrator
        memory = AgentMemory()
        orchestrator = PortalOrchestrator(memory)
        
        # Get available portals
        portals = orchestrator.get_available_portals()
        
        if not portals:
            ui.show_info_message("No portals available")
            return
        
        # Show portal options
        ui.show_info_message("Available development portals:")
        for i, portal in enumerate(portals, 1):
            ui.show_info_message(f"{i}. {portal['name']} - {portal['description']}")
        
        # Get user choice
        choice = ui.get_user_input("Select portal to open (or 'all' for all): ")
        
        if choice.lower() == 'all':
            for portal in portals:
                ui.show_info_message(f"Opening {portal['name']}...")
                orchestrator.open_portal(portal['name'])
        else:
            try:
                portal_idx = int(choice) - 1
                if 0 <= portal_idx < len(portals):
                    portal = portals[portal_idx]
                    ui.show_info_message(f"Opening {portal['name']}...")
                    orchestrator.open_portal(portal['name'])
                else:
                    ui.show_error_message("Invalid portal selection")
            except ValueError:
                ui.show_error_message("Invalid input")
        
    except Exception as e:
        logging.error(f"Portal mode failed: {e}")
        ui.show_error_message("Portal mode failed", str(e))


def run_install_mode(ui: ModernTerminalUI, app_name: str = None, debug: bool = False) -> None:
    """Run natural language app installation mode."""
    ui.show_banner()
    ui.show_mode_header('Install', 'Natural language app installation')
    
    try:
        # Initialize components
        memory = AgentMemory()
        llm_agent = EnhancedLLMAgent(memory)
        app_extractor = AppNameExtractor()
        system_inspector = SystemInspector()
        
        # Get app name from user if not provided
        if not app_name:
            app_input = ui.get_user_input("What app would you like to install? (e.g., 'install vscode' or 'I need a text editor'): ")
        else:
            app_input = app_name
        
        if not app_input:
            ui.show_error_message("No app specified")
            return
        
        # Extract app name
        app_name = app_extractor.extract_app_name(app_input)
        ui.show_info_message(f"Extracted app name: {app_name}")
        
        # Get system information
        system_info = system_inspector.analyze()
        
        # Generate installation plan
        ui.show_info_message(f"Generating installation plan for {app_name}...")
        plan = llm_agent.get_install_plan(app_name, system_info)
        
        if not plan:
            ui.show_error_message("Could not generate installation plan", "Check your internet connection and try again")
            return
        
        # Show plan and confirm
        ui.show_info_message("Installation plan generated:")
        for step in plan.get('steps', []):
            ui.show_info_message(f"• {step}")
        
        if not ui.confirm_action("Proceed with installation?"):
            ui.show_info_message("Installation cancelled")
            return
        
        # Execute installation
        ui.show_info_message("Executing installation...")
        executor = ShellExecutor(max_retries=3)
        result = executor.execute_install_plan(plan, llm_agent, ui)
        
        # Record installation in memory
        memory.record_app_install(app_name, plan, result)
        
        # Show result
        if result.get('success', False):
            ui.show_success_message(f"{app_name} installed successfully!")
        else:
            error = result.get('error', 'Unknown error')
            ui.show_error_message(f"Installation failed", error)
        
    except Exception as e:
        logging.error(f"Install mode failed: {e}")
        ui.show_error_message("Install mode failed", str(e))


def run_diagnostics_mode(ui: ModernTerminalUI, debug: bool = False) -> None:
    """Run system diagnostics mode."""
    ui.show_banner()
    ui.show_mode_header('Diagnostics', 'System health and diagnostics')
    
    try:
        # Import diagnostics module
        from scripts.diagnostics import run_diagnostics
        
        # Run diagnostics
        ui.show_info_message("Running system diagnostics...")
        results = run_diagnostics()
        
        # Display results
        ui.show_info_message("Diagnostics completed")
        for category, status in results.items():
            if status:
                ui.show_success_message(f"{category}: OK")
            else:
                ui.show_error_message(f"{category}: Failed")
        
    except Exception as e:
        logging.error(f"Diagnostics mode failed: {e}")
        ui.show_error_message("Diagnostics mode failed", str(e))


def run_settings_mode(ui: ModernTerminalUI) -> None:
    """Run settings menu."""
    ui.show_banner()
    ui.show_mode_header('Settings', 'CONFIGO configuration and preferences')
    
    try:
        settings_menu = SettingsMenu(ui)
        settings_menu.show_settings_menu()
    except Exception as e:
        logging.error(f"Settings mode failed: {e}")
        ui.show_error_message("Settings mode failed", str(e))


def show_welcome_screen(ui: ModernTerminalUI) -> str:
    """Show welcome screen and get mode choice."""
    ui.show_welcome_animation()
    ui.show_banner()
    
    # Show welcome screen and get mode choice
    mode_choice = ui.show_welcome_screen()
    mode_map = {
        1: 'setup',
        2: 'chat',
        3: 'scan',
        4: 'install',
        5: 'portals',
        6: 'diagnostics',
        7: 'settings',
    }
    return mode_map.get(mode_choice, 'setup')


def main():
    """Main entry point for CONFIGO."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="CONFIGO - Intelligent Development Environment Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  configo                    # Interactive mode with welcome screen
  configo setup             # Full development environment setup
  configo chat              # Interactive AI chat assistant
  configo scan              # Project analysis and recommendations
  configo install vscode    # Install specific application
  configo portals           # Login portal orchestration
  configo diagnostics       # System diagnostics and health check
        """
    )
    
    parser.add_argument('command', nargs='?', default='interactive',
                       choices=['setup', 'chat', 'scan', 'install', 'portals', 'diagnostics', 'settings', 'help'],
                       help='Command to execute')
    
    parser.add_argument('app_name', nargs='?', help='Application name for install command')
    
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--lite', action='store_true', help='Minimal output for low-speed terminals')
    parser.add_argument('--theme', choices=['default', 'minimal', 'developer', 'verbose', 'dark', 'light'],
                       default='default', help='UI theme to use')
    
    args = parser.parse_args()
    
    # Initialize UI with configuration
    ui_config = UIConfig()
    ui_config.theme = Theme(args.theme)
    
    if args.lite:
        ui_config.use_animations = False
        ui_config.use_emoji = False
    
    ui = ModernTerminalUI(ui_config)
    
    try:
        if args.command == 'help':
            parser.print_help()
            return
        
        if args.command == 'interactive':
            # Show welcome screen and get mode
            mode = show_welcome_screen(ui)
            
            # Execute the selected mode
            if mode == 'setup':
                run_full_setup(ui, args.debug, args.lite)
            elif mode == 'chat':
                run_chat_mode(ui, args.debug)
            elif mode == 'scan':
                run_scan_mode(ui, args.debug)
            elif mode == 'install':
                run_install_mode(ui, args.app_name, args.debug)
            elif mode == 'portals':
                run_portal_mode(ui, args.debug)
            elif mode == 'diagnostics':
                run_diagnostics_mode(ui, args.debug)
            elif mode == 'settings':
                run_settings_mode(ui)
            else:
                ui.show_error_message(f"Unknown mode: {mode}")
        
        elif args.command == 'setup':
            run_full_setup(ui, args.debug, args.lite)
        
        elif args.command == 'chat':
            run_chat_mode(ui, args.debug)
        
        elif args.command == 'scan':
            run_scan_mode(ui, args.debug)
        
        elif args.command == 'install':
            run_install_mode(ui, args.app_name, args.debug)
        
        elif args.command == 'portals':
            run_portal_mode(ui, args.debug)
        
        elif args.command == 'diagnostics':
            run_diagnostics_mode(ui, args.debug)
        
        elif args.command == 'settings':
            run_settings_mode(ui)
        
    except KeyboardInterrupt:
        ui.show_success_message("Goodbye! (Interrupted)")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        if args.debug:
            import traceback
            ui.show_error_message("Fatal error", suggestion=str(e), retry_info=traceback.format_exc())
        else:
            ui.show_error_message("An unexpected error occurred. Use --debug for details.")


if __name__ == "__main__":
    main() 