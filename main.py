#!/usr/bin/env python3
"""
CONFIGO - Intelligent Development Environment Agent
===================================================

An autonomous LLM-powered agent that intelligently installs tools,
handles extensions, performs validation, and uses memory + Gemini
to automate development environment setup.

🚀 UPGRADED FEATURES:
- Interactive Chat Mode (configo chat)
- Project-Aware Stack Detection
- Smart Tool Validation + Recovery
- User Profiles with Memory
- Extension + Login Portal Orchestration
- Modern Terminal UI/UX
"""
"""
CONFIGO: Autonomous AI Setup Agent
==================================

A fully autonomous LLM agent that intelligently sets up development environments
with memory, planning, self-healing, and validation capabilities.

Features:
- 🧠 Memory-aware recommendations using mem0ai
- 🤖 LLM-powered stack generation via Gemini
- 🔧 Self-healing installation with retry logic
- ✅ Post-installation validation
- 🎯 Domain-aware tool recommendations
- 🌐 Browser-based login portal orchestration

Usage:
    python main.py
"""

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

# UI components
from ui.layout import ConfigoLayout
from ui.enhanced_messages import EnhancedMessageDisplay
from ui.modern_ui import ModernUI
from ui.enhanced_terminal_ui import EnhancedTerminalUI, UIConfig
from rich.console import Console
from rich.live import Live

# Installation utilities
from installers.base import install_tools


def setup_logging() -> None:
    """
    Configure logging for the autonomous agent.
    
    Sets up file-based logging with configurable log level
    from environment variable LOG_LEVEL (defaults to INFO).
    Creates a log file named 'ai_setup_agent.log' in the current directory.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ai_setup_agent.log')
        ]
    )


def execute_tool_installation(step, messages: EnhancedMessageDisplay) -> bool:
    """
    Execute a tool installation step.
    
    Args:
        step: The planning step containing tool installation details
        messages: UI message display instance for user feedback
        
    Returns:
        bool: True if installation succeeded, False otherwise
        
    Note:
        Records installation results in memory for future reference
        and learning purposes.
    """
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


def execute_extension_installation(step, messages: EnhancedMessageDisplay) -> bool:
    """
    Execute a VS Code/Cursor extension installation step.
    
    Args:
        step: The planning step containing extension details
        messages: UI message display instance for user feedback
        
    Returns:
        bool: True if installation succeeded, False otherwise
        
    Note:
        Currently uses the same logic as tool installation.
        Future versions may include extension-specific installation logic.
    """
    try:
        # For now, we'll use the same logic as tool installation
        # In the future, this could be enhanced with extension-specific logic
        return execute_tool_installation(step, messages)
        
    except Exception as e:
        logging.error(f"Error installing extension {step.name}: {e}")
        return False


def execute_login_portal(step, messages: EnhancedMessageDisplay) -> bool:
    """
    Execute a login portal step by opening the browser.
    
    Args:
        step: The planning step containing portal details
        messages: UI message display instance for user feedback
        
    Returns:
        bool: True if portal opened successfully, False otherwise
        
    Note:
        Extracts URL from step data and opens it in the default browser.
        Records the portal visit in memory for future reference.
    """
    try:
        # Extract URL from step data
        portal_data = step.data if hasattr(step, 'data') else {}
        url = portal_data.get('url', '')
        
        if url:
            # Open the URL in the default browser
            webbrowser.open(url)
            messages.show_login_portal_prompt(step.name, url, step.description)
            return True
        else:
            logging.error(f"No URL found for login portal {step.name}")
            return False
            
    except Exception as e:
        logging.error(f"Error opening login portal {step.name}: {e}")
        return False


def execute_validation(step, messages: EnhancedMessageDisplay) -> bool:
    """
    Execute a validation step to verify tool installation.
    
    Args:
        step: The planning step containing validation details
        messages: UI message display instance for user feedback
        
    Returns:
        bool: True if validation passed, False otherwise
        
    Note:
        Uses the ToolValidator to check if the tool is properly installed
        and functioning correctly.
    """
    try:
        # Import here to avoid circular imports
        from core.validator import ToolValidator
        from core.memory import AgentMemory
        
        memory = AgentMemory()
        # Create a minimal LLM agent for validation
        from core.enhanced_llm_agent import EnhancedLLMAgent
        llm_agent = EnhancedLLMAgent(memory)
        validator = ToolValidator(memory, llm_agent)
        
        # Validate the tool using the check command
        result = validator._validate_regular_tool(step.name, step.check_command)
        return result.is_installed
        
    except Exception as e:
        logging.error(f"Error validating tool {step.name}: {e}")
        return False


def get_tool_version(tool_name: str, check_command: str) -> Optional[str]:
    """
    Get the version of an installed tool.
    
    Args:
        tool_name: Name of the tool to check
        check_command: Command to check tool version
        
    Returns:
        Optional[str]: Version string if found, None otherwise
        
    Note:
        Executes the check command and extracts version information
        from the output. Handles timeouts and command failures gracefully.
    """
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


def main(debug: bool = False, lite_mode: bool = False) -> None:
    """
    Main entry point for the autonomous AI setup agent.
    
    Orchestrates the complete workflow:
    1. Initialize UI and memory systems
    2. Get user environment requirements
    3. Generate AI-powered recommendations
    4. Create and execute installation plan
    5. Validate results and perform self-healing
    
    The function handles the entire setup process from user input
    to final validation, including error recovery and user feedback.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialize enhanced UI components
    ui_config = UIConfig()
    if lite_mode:
        ui_config.use_animations = False
        ui_config.use_emoji = False
    
    ui = EnhancedTerminalUI(ui_config)
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    try:
        # Show enhanced banner
        ui.show_banner()
        
        if lite_mode:
            ui.show_lite_mode_notice()
        
        # Initialize memory system for persistent state
        logger.info("Initializing memory system")
        memory = AgentMemory()
        
        # Perform advanced system intelligence analysis
        logger.info("Performing system intelligence analysis")
        system_inspector = SystemInspector()
        system_info = system_inspector.analyze()
        
        # Display system intelligence summary
        display_system_summary(system_info)
        
        # Save system intelligence to memory
        system_inspector.save_to_memory(system_info)
        
        # Display memory context and statistics
        memory_stats = memory.get_memory_stats()
        ui.show_memory_context(memory_stats)
        
        # Get user environment requirements
        env = messages.show_environment_prompt()
        if not env:
            messages.show_error_with_context("No environment specified. Exiting.")
            sys.exit(1)
        
        # Start tracking this session
        session_id = memory.start_session(env)
        logger.info(f"Started session: {session_id}")
        
        # Scan current project for context
        logger.info("Performing project scan")
        stack_info = scan_project()
        
        # Initialize LLM agent for intelligent recommendations
        logger.info("Initializing enhanced LLM agent")
        llm_agent = EnhancedLLMAgent(memory)
        
        # Generate AI-powered stack recommendations with system intelligence
        logger.info("Generating enhanced stack recommendations with system intelligence")
        
        # Create system context for LLM
        system_context = f"""
System Environment:
- OS: {system_info.os_name} {system_info.os_version}
- Architecture: {system_info.arch}
- Package Managers: {', '.join(system_info.package_managers)}
- GPU: {system_info.gpu or 'None'}
- RAM: {system_info.ram_gb} GB
- Virtualization: {system_info.virtualization}
- Sudo Access: {'Yes' if system_info.has_sudo else 'No'}
"""
        
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
        
        # Display generation results
        print(f"✅ Generated {len(tools)} tools and {len(llm_response.login_portals)} login portals")
        
        # Show domain detection results
        detected_domain = llm_response.domain_completion.get("detected_domain", "unknown")
        ui.show_ai_reasoning(
            f"Domain Detection: {detected_domain.title()}",
            f"Based on project analysis and AI reasoning, CONFIGO detected this as a {detected_domain} project.",
            llm_response.confidence_score
        )
        
        # Generate intelligent installation plan
        logger.info("Generating installation plan")
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
        if not messages.show_installation_prompt():
            messages.show_aborted_message()
            memory.end_session(session_id)
            sys.exit(0)
        
        # Initialize execution components
        executor = PlanExecutor(plan)
        validator = ToolValidator(memory, llm_agent)
        
        # Execute the installation plan
        logger.info("Starting plan execution")
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
                    success = execute_tool_installation(step, messages)
                elif step.step_type.value == "extension_install":
                    success = execute_extension_installation(step, messages)
                elif step.step_type.value == "login_portal":
                    success = execute_login_portal(step, messages)
                elif step.step_type.value == "validation":
                    success = execute_validation(step, messages)
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
                logger.error(f"Error executing step {step.name}: {e}")
                executor.fail_step(step, str(e))
                failed_tools.append(step.name)
                messages.show_step_result(step, False, error=str(e))
        
        # Update session with final results
        memory.update_session_tools(session_id, installed_tools, failed_tools)
        memory.update_session_portals(session_id, [portal["name"] for portal in llm_response.login_portals])
        
        # Perform post-installation validation
        logger.info("Performing post-installation validation")
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
            logger.info("Attempting self-healing for failed tools")
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
                    success = execute_tool_installation(temp_step, messages)
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
        
        logger.info("CONFIGO setup completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        ui.show_info_message("Setup interrupted by user", "⏹️")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        ui.show_error_message(str(e), "An unexpected error occurred", "Check the logs for more details")
        sys.exit(1)


def chat_mode() -> None:
    """
    Interactive chat mode for CONFIGO.
    
    Provides a conversational interface where users can:
    - Ask questions about tools and setup
    - Execute commands using natural language
    - Get recommendations and help
    - Interact with the AI agent conversationally
    
    The chat mode uses the ChatAgent for processing messages
    and the ModernUI for the interface.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        memory = AgentMemory()
        chat_agent = ChatAgent(memory, debug_mode=False)
        ui = EnhancedTerminalUI()
        
        # Show banner
        ui.show_banner()
        
        # Show chat interface
        ui.show_chat_interface("Chat with CONFIGO - Ask me anything about development tools and setup!")
        
        # Debug mode can be enabled via environment variable
        if os.getenv('CONFIGO_DEBUG', 'false').lower() == 'true':
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
                if response.action_type == "command" and response.command:
                    if response.requires_confirmation:
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
        logger.error(f"Chat mode failed: {e}")
        print(f"\n💥 Chat mode failed: {e}")
        sys.exit(1)


def scan_mode() -> None:
    """
    Project scanning mode for CONFIGO.
    
    Automatically scans the current project directory to:
    - Detect programming languages and frameworks
    - Identify configuration files
    - Provide tailored tool recommendations
    - Show project analysis and insights
    
    Uses the ProjectScanner for analysis and ModernUI for display.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        memory = AgentMemory()
        project_scanner = ProjectScanner(memory)
        ui = EnhancedTerminalUI()
        
        # Show banner
        ui.show_banner()
        
        # Scan project
        logger.info("Scanning project...")
        ui.show_info_message("Scanning project for technologies and frameworks...", "🔍")
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
        logger.error(f"Scan mode failed: {e}")
        print(f"\n💥 Scan mode failed: {e}")
        sys.exit(1)


def portal_mode() -> None:
    """
    Portal orchestration mode for opening login portals.
    
    Allows users to open various development service portals
    for authentication and account setup.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialize UI components
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    try:
        # Show portal mode banner
        messages.show_autonomous_banner()
        
        # Initialize memory and portal orchestrator
        memory = AgentMemory()
        orchestrator = PortalOrchestrator(memory)
        
        # Get available portals
        available_portals = orchestrator.get_available_portals()
        
        if not available_portals:
            messages.show_error_with_context("No portals available. Please configure portals first.")
            return
        
        # Display portal options
        messages.show_portal_options(available_portals)
        
        # Get user selection
        console.print("[bold cyan]Enter portal name to open: [/bold cyan]", end="")
        portal_name = input().strip()
        
        if portal_name in available_portals:
            # Open the selected portal
            success = orchestrator.open_portal(portal_name)
            if success:
                messages.show_portal_opened(portal_name, available_portals[portal_name]['url'])
            else:
                messages.show_error_with_context(f"Failed to open {portal_name}")
        else:
            messages.show_error_with_context(f"Portal '{portal_name}' not found")
            
    except KeyboardInterrupt:
        messages.show_aborted_message()
    except Exception as e:
        logger.error(f"Error in portal mode: {e}")
        messages.show_error_with_context(f"Portal mode error: {e}")

def app_install_mode() -> None:
    """
    Natural language app installation mode.
    
    Allows users to install applications using natural language:
    "Install Discord", "I need Chrome", etc.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialize UI components
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    try:
        # Show app installer banner
        messages.show_autonomous_banner()
        
        # Initialize memory and LLM agent
        memory = AgentMemory()
        llm_agent = EnhancedLLMAgent(memory)
        
        # Get system information
        from core.system import get_system_info
        system_info = get_system_info()
        
        # Get app name from user using natural language
        user_input = messages.show_app_install_prompt()
        if not user_input:
            messages.show_error_with_context("No app specified. Exiting.")
            return
        
        # Extract clean app name using intelligent NLP
        from core.app_name_extractor import AppNameExtractor
        app_name = AppNameExtractor.extract_app_name(user_input)
        
        # Show app name extraction result
        messages.show_app_name_extraction(user_input, app_name)
        
        # Validate extracted app name
        if not AppNameExtractor.validate_app_name(app_name):
            messages.show_error_with_context(f"Could not extract a valid app name from '{user_input}'. Please try again with a clearer request.")
            return
        
        # Check if already installed
        if memory.is_app_installed(app_name):
            messages.show_already_installed(app_name)
            return
        
        # Show installation start with system information
        messages.show_app_install_start(app_name, system_info)
        
        # Generate installation plan using LLM
        logger.info(f"Generating install plan for {app_name}")
        messages.show_install_progress(app_name, "Generating installation plan with AI...", 1)
        
        plan = llm_agent.get_install_plan(app_name, system_info)
        
        if not plan:
            messages.show_installation_failed(app_name, "Could not generate installation plan", [
                "Check your internet connection",
                "Verify the app name is correct",
                "Try a different app name"
            ])
            return
        
        # Show the plan and ask for confirmation
        if not messages.show_install_confirmation(app_name, plan):
            messages.show_aborted_message()
            return
        
        # Execute the installation plan with enhanced progress tracking
        from core.shell_executor import ShellExecutor
        executor = ShellExecutor(max_retries=3)
        
        logger.info(f"Executing install plan for {app_name}")
        result = executor.execute_install_plan(plan, llm_agent, messages)
        
        # Record installation in memory
        memory.record_app_install(app_name, plan, result)
        
        # Show comprehensive result
        if result['success']:
            messages.show_installation_complete(app_name, result)
        else:
            # Generate helpful suggestions based on the error
            suggestions = []
            error = result.get('error', 'Unknown error')
            
            if 'not found' in error.lower() or 'package' in error.lower():
                suggestions.append("The package might not be available in your distribution's repositories")
                suggestions.append("Try using a different package manager (snap, flatpak)")
                suggestions.append("Check if the app name is spelled correctly")
            elif 'permission' in error.lower():
                suggestions.append("Try running with sudo or check your user permissions")
            elif 'network' in error.lower() or 'connection' in error.lower():
                suggestions.append("Check your internet connection")
                suggestions.append("Try updating your package lists first")
            
            messages.show_installation_failed(app_name, error, suggestions)
            
    except KeyboardInterrupt:
        messages.show_aborted_message()
    except Exception as e:
        logger.error(f"Error in app install mode: {e}")
        messages.show_error_with_context(f"App installation error: {e}")

if __name__ == "__main__":
    import sys
    
    # Check for flags first
    debug = "--debug" in sys.argv
    lite_mode = "--lite" in sys.argv
    
    # Remove flags from argv for mode detection
    if debug:
        sys.argv = [arg for arg in sys.argv if arg != "--debug"]
    if lite_mode:
        sys.argv = [arg for arg in sys.argv if arg != "--lite"]
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "chat":
            chat_mode()
        elif mode == "scan":
            scan_mode()
        elif mode == "portal":
            portal_mode()
        elif mode == "install":
            app_install_mode()
        elif mode == "help":
            print("CONFIGO - Autonomous AI Setup Agent")
            print("\nAvailable modes:")
            print("  main.py          - Full development environment setup")
            print("  main.py chat     - Interactive chat mode")
            print("  main.py scan     - Project scanning mode")
            print("  main.py portal   - Login portal orchestration")
            print("  main.py install  - Natural language app installation")
            print("  main.py help     - Show this help")
            print("\nOptions:")
            print("  --debug          - Enable debug logging and LLM response logging")
            print("  --lite           - Minimal output for low-speed terminals")
        else:
            print(f"Unknown mode: {mode}")
            print("Use 'main.py help' for available modes")
    else:
        # Default mode - full development environment setup
        main(debug, lite_mode) 