import sys
import os
import logging
from datetime import datetime
from typing import Any, Dict

# Core CONFIGO modules
from core.memory import AgentMemory
from core.system_inspector import SystemInspector, display_system_summary
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.chat_agent import ChatAgent
from core.portal_orchestrator import PortalOrchestrator
from core.project_scanner import ProjectScanner
from core.validator import ToolValidator, ValidationReport
from core.planner import PlanGenerator, PlanExecutor, InstallationPlan
from core.shell_executor import ShellExecutor
from core.app_name_extractor import AppNameExtractor

# UI modules
from ui.modern_terminal_ui import ModernTerminalUI, UIConfig, Theme
from ui.settings_menu import SettingsMenu

# Setup logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('ai_setup_agent.log')]
)
logger = logging.getLogger(__name__)

def main():
    debug = '--debug' in sys.argv
    lite_mode = '--lite' in sys.argv
    if debug:
        sys.argv = [arg for arg in sys.argv if arg != '--debug']
    if lite_mode:
        sys.argv = [arg for arg in sys.argv if arg != '--lite']

    # UI config and initialization (default theme)
    ui_config = UIConfig()
    ui = ModernTerminalUI(ui_config)

    # Welcome animation and CONFIGO banner
    ui.show_welcome_animation()
    ui.show_banner()

    # Welcome screen and mode selection
    mode_choice = ui.show_welcome_screen()
    mode_map = {
        1: 'setup',
        2: 'chat',
        3: 'scan',
        4: 'portal',
        5: 'install',
        6: 'settings',
    }
    mode = mode_map.get(mode_choice, 'setup')

    try:
        if mode == 'setup':
            run_full_setup(ui, debug, lite_mode)
        elif mode == 'chat':
            run_chat_mode(ui, debug)
        elif mode == 'scan':
            run_scan_mode(ui, debug)
        elif mode == 'portal':
            run_portal_mode(ui, debug)
        elif mode == 'install':
            run_install_mode(ui, debug)
        elif mode == 'settings':
            run_settings_mode(ui)
        else:
            ui.show_error_message(f'Unknown mode: {mode}')
    except KeyboardInterrupt:
        ui.show_success_message('Goodbye! (Interrupted)')
    except Exception as e:
        logger.error(f'Fatal error in main: {e}')
        if debug:
            import traceback
            ui.show_error_message('Fatal error', suggestion=str(e), retry_info=traceback.format_exc())
        else:
            ui.show_error_message('An unexpected error occurred. Use --debug for details.')

def run_full_setup(ui: ModernTerminalUI, debug: bool, lite_mode: bool) -> None:
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
        logger.info(f"Started session: {session_id}")
        
        # Initialize LLM agent for intelligent recommendations
        ui.show_info_message("Initializing AI agent...")
        llm_agent = EnhancedLLMAgent(memory)
        
        # Generate AI-powered stack recommendations
        ui.show_info_message("Generating AI-powered recommendations...")
        llm_response = llm_agent.generate_enhanced_stack(env, "", debug=debug)
        
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
        
        # Execute the plan
        ui.show_info_message("Executing installation plan...")
        plan_executor = PlanExecutor()
        executor = ShellExecutor(max_retries=3)
        
        success_count = 0
        total_steps = len(plan.steps)
        
        for i, step in enumerate(plan.steps, 1):
            ui.show_info_message(f"Executing step {i}/{total_steps}: {step.name}")
            
            try:
                if step.step_type.value == "tool_installation":
                    success = execute_tool_installation(step, ui)
                elif step.step_type.value == "extension_installation":
                    success = execute_extension_installation(step, ui)
                elif step.step_type.value == "login_portal":
                    success = execute_login_portal(step, ui)
                elif step.step_type.value == "validation":
                    success = execute_validation(step, ui)
                else:
                    success = False
                
                if success:
                    success_count += 1
                    ui.show_success_message(f"Step {i} completed successfully")
                else:
                    ui.show_error_message(f"Step {i} failed", "Will retry automatically")
                    
            except Exception as e:
                logger.error(f"Error executing step {i}: {e}")
                ui.show_error_message(f"Step {i} failed", str(e))
        
        # Final validation and summary
        ui.show_info_message("Performing final validation...")
        validator = ToolValidator()
        validation_report = validator.validate_all_installed_tools()
        
        ui.show_validation_results(validation_report.results)
        
        # Show completion summary
        ui.show_success_message(
            f"Setup completed! {success_count}/{total_steps} steps successful",
            f"Success rate: {(success_count/total_steps)*100:.1f}%"
        )
        
    except Exception as e:
        logger.error(f"Error in full setup: {e}")
        ui.show_error_message("Setup failed", str(e))

def run_chat_mode(ui: ModernTerminalUI, debug: bool) -> None:
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
        logger.error(f"Chat mode failed: {e}")
        ui.show_error_message("Chat mode failed", str(e))

def run_scan_mode(ui: ModernTerminalUI, debug: bool) -> None:
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
        logger.error(f"Scan mode failed: {e}")
        ui.show_error_message("Scan mode failed", str(e))

def run_portal_mode(ui: ModernTerminalUI, debug: bool) -> None:
    """Run portal orchestration mode."""
    ui.show_banner()
    ui.show_mode_header('Portal', 'Login portal orchestration')
    
    try:
        # Initialize portal orchestrator
        orchestrator = PortalOrchestrator()
        
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
        logger.error(f"Portal mode failed: {e}")
        ui.show_error_message("Portal mode failed", str(e))

def run_install_mode(ui: ModernTerminalUI, debug: bool) -> None:
    """Run natural language app installation mode."""
    ui.show_banner()
    ui.show_mode_header('Install', 'Natural language app installation')
    
    try:
        # Initialize components
        memory = AgentMemory()
        llm_agent = EnhancedLLMAgent(memory)
        app_extractor = AppNameExtractor()
        system_inspector = SystemInspector()
        
        # Get app name from user
        app_input = ui.get_user_input("What app would you like to install? (e.g., 'install vscode' or 'I need a text editor'): ")
        
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
        logger.error(f"Install mode failed: {e}")
        ui.show_error_message("Install mode failed", str(e))

def run_settings_mode(ui: ModernTerminalUI) -> None:
    """Run settings menu."""
    settings_menu = SettingsMenu(ui)
    settings_menu.show_settings_menu()

def execute_tool_installation(step, ui: ModernTerminalUI) -> bool:
    """Execute a tool installation step."""
    try:
        ui.show_info_message(f"Installing {step.name}...")
        # TODO: Implement actual tool installation logic
        return True
    except Exception as e:
        ui.show_error_message(f"Failed to install {step.name}", str(e))
        return False

def execute_extension_installation(step, ui: ModernTerminalUI) -> bool:
    """Execute an extension installation step."""
    try:
        ui.show_info_message(f"Installing extension {step.name}...")
        # TODO: Implement actual extension installation logic
        return True
    except Exception as e:
        ui.show_error_message(f"Failed to install extension {step.name}", str(e))
        return False

def execute_login_portal(step, ui: ModernTerminalUI) -> bool:
    """Execute a login portal step."""
    try:
        ui.show_info_message(f"Opening login portal {step.name}...")
        # TODO: Implement actual portal opening logic
        return True
    except Exception as e:
        ui.show_error_message(f"Failed to open portal {step.name}", str(e))
        return False

def execute_validation(step, ui: ModernTerminalUI) -> bool:
    """Execute a validation step."""
    try:
        ui.show_info_message(f"Validating {step.name}...")
        # TODO: Implement actual validation logic
        return True
    except Exception as e:
        ui.show_error_message(f"Failed to validate {step.name}", str(e))
        return False

if __name__ == '__main__':
    main()