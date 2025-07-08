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
import webbrowser
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional

# Core agent components
from core.memory import AgentMemory
from core.planner import PlanGenerator, PlanExecutor, InstallationPlan
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.validator import ToolValidator, ValidationReport
from core.project_scan import scan_project
from core.chat_agent import ChatAgent
from core.project_scanner import ProjectScanner
from core.portal_orchestrator import PortalOrchestrator

# UI components
from ui.layout import ConfigoLayout
from ui.enhanced_messages import EnhancedMessageDisplay
from ui.modern_ui import ModernUI
from rich.console import Console

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


def main() -> None:
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
    
    # Initialize UI components
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    try:
        # Show autonomous agent banner
        messages.show_autonomous_banner()
        
        # Initialize memory system for persistent state
        logger.info("Initializing memory system")
        memory = AgentMemory()
        
        # Display memory context and statistics
        messages.show_memory_context(memory)
        
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
        
        # Generate AI-powered stack recommendations
        logger.info("Generating enhanced stack recommendations")
        llm_response = llm_agent.generate_enhanced_stack(env, str(stack_info) if stack_info else "")
        
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
        messages.show_domain_detection(detected_domain, llm_response.confidence_score)
        
        # Generate intelligent installation plan
        logger.info("Generating installation plan")
        plan_generator = PlanGenerator()
        memory_context = memory.get_memory_context()
        plan = plan_generator.generate_plan(tools, env, memory_context)
        
        # Display the plan to user
        messages.show_planning_steps(plan)
        
        # Show login portals that will be opened
        messages.show_login_portals(llm_response.login_portals)
        
        # Display improvement suggestions
        if llm_response.improvement_suggestions:
            messages.show_improvement_suggestions(llm_response.improvement_suggestions)
        
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
        messages.show_installation_start()
        
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
            messages.show_step_progress(step, current_step, plan.total_steps)
            
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
                    messages.show_step_result(step, True, version)
                else:
                    # Mark as failed and attempt self-healing
                    executor.fail_step(step, "Installation failed")
                    failed_tools.append(step.name)
                    messages.show_step_result(step, False)
                    
                    # Attempt self-healing if retries are allowed
                    if memory.should_retry_tool(step.name):
                        messages.show_retry_attempt(step.name, step.retry_count + 1, step.max_retries)
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
        messages.show_validation_results(validation_report)
        
        # Attempt self-healing for failed tools
        healing_results = []
        if failed_tools:
            logger.info("Attempting self-healing for failed tools")
            messages.show_self_healing_progress([result for result in validation_report.validation_results if not result.is_installed])
            
            # Use LLM agent to generate fixes
            for failed_tool in failed_tools:
                fix_command = llm_agent.generate_command_fix(failed_tool, "Installation failed", failed_tool)
                if fix_command:
                    messages.show_healing_attempt(failed_tool, fix_command, "LLM-generated fix")
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
                    messages.show_healing_result(failed_tool, success, fix_command)
        
        # Show final completion summary
        messages.show_completion_summary(plan, validation_report, healing_results)
        
        # End the session
        memory.end_session(session_id)
        
        logger.info("CONFIGO setup completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        messages.show_aborted_message()
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        messages.show_error_with_context(str(e))
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
        chat_agent = ChatAgent(memory, debug_mode=args.debug)
        ui = ModernUI()
        
        # Show banner
        ui.show_banner()
        
        # Show chat interface
        ui.show_chat_interface(chat_agent)
        
        if args.debug:
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
                ui.show_chat_response(response)
                
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
        ui = ModernUI()
        
        # Show banner
        ui.show_banner()
        
        # Scan project
        logger.info("Scanning project...")
        analysis = project_scanner.scan_project(".")
        
        # Show results
        ui.show_project_analysis(analysis)
        
        # Show recommendations
        if analysis.recommendations:
            ui.show_success_message(f"Found {len(analysis.recommendations)} recommendations for your project!")
        
    except Exception as e:
        logger.error(f"Scan mode failed: {e}")
        print(f"\n💥 Scan mode failed: {e}")
        sys.exit(1)


def portal_mode() -> None:
    """
    Portal management mode for CONFIGO.
    
    Manages AI service login portals and CLI tools:
    - Opens browser portals for service logins
    - Installs CLI tools for various services
    - Checks login status across services
    - Manages portal history and preferences
    
    Uses the PortalOrchestrator for portal management and ModernUI for interface.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        memory = AgentMemory()
        portal_orchestrator = PortalOrchestrator(memory)
        ui = ModernUI()
        
        # Show banner
        ui.show_banner()
        
        # Show portal status
        ui.show_portal_status(portal_orchestrator)
        
        # Get user action
        action = ui.get_user_input("Choose action (open/install/check/exit): ").lower()
        
        if action == "open":
            portal_name = ui.get_user_input("Enter portal name (claude/gemini/grok/chatgpt/cursor/github): ")
            if portal_orchestrator.open_login_portal(portal_name):
                ui.show_success_message(f"Opened {portal_name} login portal!")
            else:
                ui.show_error_message(f"Failed to open {portal_name} portal")
        
        elif action == "install":
            portal_name = ui.get_user_input("Enter portal name to install CLI tool: ")
            success, message = portal_orchestrator.install_cli_tool(portal_name)
            if success:
                ui.show_success_message(message)
            else:
                ui.show_error_message("Installation failed", message)
        
        elif action == "check":
            portal_name = ui.get_user_input("Enter portal name to check login status: ")
            is_logged_in = portal_orchestrator.check_login_status(portal_name)
            if is_logged_in:
                ui.show_success_message(f"Logged in to {portal_name}!")
            else:
                ui.show_error_message(f"Not logged in to {portal_name}")
        
    except Exception as e:
        logger.error(f"Portal mode failed: {e}")
        print(f"\n💥 Portal mode failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CONFIGO - Intelligent Development Environment Agent")
    parser.add_argument("mode", nargs="?", default="setup", 
                       choices=["setup", "chat", "scan", "portal"],
                       help="Mode to run CONFIGO in")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug mode for chat (shows LLM input/output)")
    
    args = parser.parse_args()
    
    if args.mode == "chat":
        chat_mode()
    elif args.mode == "scan":
        scan_mode()
    elif args.mode == "portal":
        portal_mode()
    else:
        main() 