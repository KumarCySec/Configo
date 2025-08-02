#!/usr/bin/env python3
"""
CONFIGO - Autonomous AI Setup Agent
===================================

🚀 Professional CLI agent that intelligently sets up full-stack developer environments
using natural language commands and autonomous planning.

Features:
- 🧠 Memory-aware recommendations and learning
- 🤖 LLM-powered stack generation and planning
- 🔧 Self-healing installation with retry logic
- ✅ Post-installation validation and testing
- 🎯 Domain-aware tool recommendations
- 🌐 Browser-based login portal orchestration
- 💬 Interactive chat mode for guidance
- 📊 Project scanning and analysis
- 🎨 Modern, beautiful terminal UI

Usage:
    configo setup <environment>     # Setup development environment
    configo install <tool>          # Install specific tool
    configo chat                    # Interactive chat mode
    configo scan                    # Scan current project
    configo portal                  # Launch login portals
    configo memory <command>        # Memory management
    configo graph <command>         # Graph database operations
    configo --debug                 # Enable debug mode
    configo --help                  # Show help
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Core CONFIGO modules
from core.installer import Installer
from core.validator import Validator
from core.planner import Planner
from agent.agent_engine import AgentEngine
from knowledge.engine import KnowledgeEngine
from memory.memory_store import MemoryStore
from ui.enhanced_terminal_ui import EnhancedTerminalUI, UIConfig
from config import Config


def setup_logging(debug: bool = False) -> None:
    """Configure logging for CONFIGO."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('configo.log'),
            logging.StreamHandler(sys.stdout) if debug else logging.NullHandler()
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="CONFIGO - Autonomous AI Setup Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  configo setup "full stack ai development"
  configo install telegram
  configo chat
  configo scan
  configo portal
  configo memory show-tool torch
  configo graph visualize-plan ai-stack
        """
    )
    
    # Main commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup development environment')
    setup_parser.add_argument('environment', nargs='?', help='Environment description')
    setup_parser.add_argument('--lite', action='store_true', help='Lite mode (faster, less comprehensive)')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install specific tool')
    install_parser.add_argument('tool', help='Tool name to install')
    install_parser.add_argument('--force', action='store_true', help='Force reinstall')
    
    # Chat command
    subparsers.add_parser('chat', help='Interactive chat mode')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan current project')
    scan_parser.add_argument('--deep', action='store_true', help='Deep scan mode')
    
    # Portal command
    portal_parser = subparsers.add_parser('portal', help='Launch login portals')
    portal_parser.add_argument('--list', action='store_true', help='List available portals')
    
    # Memory commands
    memory_parser = subparsers.add_parser('memory', help='Memory management')
    memory_parser.add_argument('action', choices=['show', 'clear', 'stats'], help='Memory action')
    memory_parser.add_argument('--tool', help='Tool name for memory operations')
    
    # Graph commands
    graph_parser = subparsers.add_parser('graph', help='Graph database operations')
    graph_parser.add_argument('action', choices=['visualize', 'query', 'stats'], help='Graph action')
    graph_parser.add_argument('--plan', help='Plan name for visualization')
    
    # Vector commands
    vector_parser = subparsers.add_parser('vector', help='Vector database operations')
    vector_parser.add_argument('action', choices=['search', 'similar', 'stats'], help='Vector action')
    vector_parser.add_argument('query', help='Search query')
    vector_parser.add_argument('--limit', type=int, default=5, help='Maximum results')
    
    # Knowledge commands
    knowledge_parser = subparsers.add_parser('knowledge', help='Knowledge base operations')
    knowledge_parser.add_argument('action', choices=['stats', 'backup', 'clear', 'refresh'], help='Knowledge action')
    knowledge_parser.add_argument('--path', help='Backup path')
    knowledge_parser.add_argument('--domain', help='Domain for refresh')
    
    # Global options
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config', help='Path to config file')
    
    return parser


def main() -> None:
    """Main entry point for CONFIGO."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        config = Config()
        
        # Initialize UI
        ui_config = UIConfig()
        ui = EnhancedTerminalUI(ui_config)
        
        # Show welcome banner
        ui.show_banner()
        
        # Initialize core components
        memory = MemoryStore()
        knowledge = KnowledgeEngine(config)
        agent = AgentEngine(memory, knowledge)
        installer = Installer(config, knowledge)
        validator = Validator(config, knowledge)
        planner = Planner(agent, memory)
        
        # Handle commands
        if args.command == 'setup':
            handle_setup(args, ui, agent, installer, validator, planner, config)
        elif args.command == 'install':
            handle_install(args, ui, agent, installer, validator, config)
        elif args.command == 'chat':
            handle_chat(args, ui, agent, config)
        elif args.command == 'scan':
            handle_scan(args, ui, agent, config)
        elif args.command == 'portal':
            handle_portal(args, ui, agent, config)
        elif args.command == 'memory':
            handle_memory(args, ui, memory, config)
        elif args.command == 'graph':
            handle_graph(args, ui, knowledge, config)
        elif args.command == 'vector':
            handle_vector(args, ui, knowledge, config)
        elif args.command == 'knowledge':
            handle_knowledge(args, ui, knowledge, config)
        else:
            # No command specified, show interactive mode
            handle_interactive_mode(ui, agent, installer, validator, planner, config)
            
    except KeyboardInterrupt:
        ui.show_success_message("Goodbye! (Interrupted)")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            import traceback
            ui.show_error_message("Fatal error", suggestion=str(e), retry_info=traceback.format_exc())
        else:
            ui.show_error_message("An unexpected error occurred. Use --debug for details.")


def handle_setup(args: argparse.Namespace, ui: EnhancedTerminalUI, agent: AgentEngine, 
                installer: Installer, validator: Validator, planner: Planner, config: Config) -> None:
    """Handle setup command."""
    environment = args.environment or ui.get_user_input("Describe your development environment:")
    
    ui.show_mode_header("Environment Setup", f"Setting up: {environment}")
    
    # Generate plan
    plan = planner.create_plan(environment, lite_mode=args.lite)
    
    # Execute plan
    results = installer.execute_plan(plan, ui)
    
    # Validate results
    validation_results = validator.validate_installation(results)
    
    # Show summary
    ui.show_completion_summary({
        'environment': environment,
        'tools_installed': len([r for r in results if r['success']]),
        'tools_failed': len([r for r in results if not r['success']]),
        'validation_passed': len([v for v in validation_results if v['passed']]),
        'validation_failed': len([v for v in validation_results if not v['passed']])
    })


def handle_install(args: argparse.Namespace, ui: EnhancedTerminalUI, agent: AgentEngine,
                  installer: Installer, validator: Validator, config: Config) -> None:
    """Handle install command."""
    ui.show_mode_header("Tool Installation", f"Installing: {args.tool}")
    
    # Get installation plan for tool
    plan = agent.plan_tool_installation(args.tool, force=args.force)
    
    # Execute installation
    result = installer.install_tool(plan, ui)
    
    # Validate installation
    validation = validator.validate_tool(args.tool)
    
    if result['success'] and validation['passed']:
        ui.show_success_message(f"Successfully installed {args.tool}")
    else:
        ui.show_error_message(f"Failed to install {args.tool}", 
                            suggestion=result.get('error', 'Unknown error'))


def handle_chat(args: argparse.Namespace, ui: EnhancedTerminalUI, agent: AgentEngine, config: Config) -> None:
    """Handle chat command."""
    ui.show_mode_header("Chat Mode", "Interactive AI assistant")
    
    ui.show_chat_interface("Welcome to CONFIGO Chat! Ask me anything about development setup.")
    
    while True:
        try:
            user_input = ui.get_user_input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
                
            response = agent.chat(user_input)
            ui.show_chat_response(response, is_ai=True)
            
        except KeyboardInterrupt:
            break
    
    ui.show_success_message("Chat session ended")


def handle_scan(args: argparse.Namespace, ui: EnhancedTerminalUI, agent: AgentEngine, config: Config) -> None:
    """Handle scan command."""
    ui.show_mode_header("Project Scan", "Analyzing current project")
    
    scan_results = agent.scan_project(deep=args.deep)
    
    ui.show_tool_detection_table(scan_results['tools'])
    ui.show_info_message(f"Found {len(scan_results['tools'])} tools in project")


def handle_portal(args: argparse.Namespace, ui: EnhancedTerminalUI, agent: AgentEngine, config: Config) -> None:
    """Handle portal command."""
    if args.list:
        portals = agent.get_available_portals()
        ui.show_info_message("Available login portals:")
        for portal in portals:
            ui.show_info_message(f"  - {portal['name']}: {portal['url']}")
    else:
        ui.show_mode_header("Portal Launch", "Opening login portals")
        agent.launch_portals()


def handle_memory(args: argparse.Namespace, ui: EnhancedTerminalUI, memory: MemoryStore, config: Config) -> None:
    """Handle memory commands."""
    if args.action == 'show':
        if args.tool:
            tool_memory = memory.get_tool_memory(args.tool)
            if tool_memory:
                ui.show_info_message(f"Tool memory for {args.tool}: {tool_memory}")
            else:
                ui.show_info_message(f"No memory found for {args.tool}")
        else:
            stats = memory.get_memory_stats()
            ui.show_memory_context(stats)
    elif args.action == 'clear':
        memory.clear_memory()
        ui.show_success_message("Memory cleared")
    elif args.action == 'stats':
        stats = memory.get_memory_stats()
        ui.show_memory_context(stats)


def handle_graph(args: argparse.Namespace, ui: EnhancedTerminalUI, knowledge: KnowledgeEngine, config: Config) -> None:
    """Handle graph commands."""
    if args.action == 'visualize':
        if args.plan:
            success = knowledge.visualize_plan(args.plan)
            if success:
                ui.show_success_message(f"Visualized plan: {args.plan}")
            else:
                ui.show_error_message(f"Failed to visualize plan: {args.plan}")
        else:
            ui.show_error_message("Please specify a plan name with --plan")
    elif args.action == 'query':
        query = ui.get_user_input("Enter graph query: ")
        results = knowledge.query_graph(query)
        ui.show_info_message(f"Query results: {results}")
    elif args.action == 'stats':
        stats = knowledge.get_graph_stats()
        ui.show_info_message(f"Graph statistics: {stats}")

def handle_vector(args: argparse.Namespace, ui: EnhancedTerminalUI, knowledge: KnowledgeEngine, config: Config) -> None:
    """Handle vector commands."""
    if args.action == 'search':
        results = knowledge.search_tools(args.query, args.limit)
        if results:
            ui.show_info_message(f"Found {len(results)} results for '{args.query}':")
            for i, result in enumerate(results, 1):
                ui.show_info_message(f"  {i}. {result.get('name', 'Unknown')} - {result.get('description', 'No description')}")
        else:
            ui.show_info_message(f"No results found for '{args.query}'")
    elif args.action == 'similar':
        results = knowledge.find_similar_tools(args.query, args.limit)
        if results:
            ui.show_info_message(f"Found {len(results)} similar tools to '{args.query}':")
            for i, result in enumerate(results, 1):
                ui.show_info_message(f"  {i}. {result.get('name', 'Unknown')} - {result.get('description', 'No description')}")
        else:
            ui.show_info_message(f"No similar tools found for '{args.query}'")
    elif args.action == 'stats':
        stats = knowledge.get_vector_stats()
        ui.show_info_message(f"Vector statistics: {stats}")

def handle_knowledge(args: argparse.Namespace, ui: EnhancedTerminalUI, knowledge: KnowledgeEngine, config: Config) -> None:
    """Handle knowledge commands."""
    if args.action == 'stats':
        graph_stats = knowledge.get_graph_stats()
        vector_stats = knowledge.get_vector_stats()
        ui.show_info_message("Knowledge Base Statistics:")
        ui.show_info_message(f"  Graph: {graph_stats}")
        ui.show_info_message(f"  Vector: {vector_stats}")
    elif args.action == 'backup':
        backup_path = args.path or f"configo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        success = knowledge.backup_knowledge(backup_path)
        if success:
            ui.show_success_message(f"Knowledge base backed up to: {backup_path}")
        else:
            ui.show_error_message("Failed to backup knowledge base")
    elif args.action == 'clear':
        confirm = ui.get_user_input("Are you sure you want to clear all knowledge? (yes/no): ")
        if confirm.lower() == 'yes':
            success = knowledge.clear_knowledge()
            if success:
                ui.show_success_message("Knowledge base cleared")
            else:
                ui.show_error_message("Failed to clear knowledge base")
        else:
            ui.show_info_message("Knowledge base clear cancelled")
    elif args.action == 'refresh':
        domain = args.domain or ui.get_user_input("Enter domain to refresh (e.g., 'full stack ai'): ")
        if domain:
            ui.show_info_message(f"Refreshing knowledge for domain: {domain}")
            success = knowledge.expand_graph_from_gemini(domain)
            if success:
                ui.show_success_message(f"Successfully refreshed knowledge for {domain}")
            else:
                ui.show_error_message(f"Failed to refresh knowledge for {domain}")
        else:
            ui.show_error_message("No domain specified")


def handle_interactive_mode(ui: EnhancedTerminalUI, agent: AgentEngine, installer: Installer,
                          validator: Validator, planner: Planner, config: Config) -> None:
    """Handle interactive mode when no command is specified."""
    ui.show_welcome_animation()
    
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
    
    # Create mock args for each mode
    class MockArgs:
        def __init__(self, mode):
            self.command = mode
            self.environment = None
            self.tool = None
            self.lite = False
            self.force = False
            self.deep = False
            self.list = False
            self.action = None
            self.plan = None
    
    args = MockArgs(mode)
    
    # Handle the selected mode
    if mode == 'setup':
        handle_setup(args, ui, agent, installer, validator, planner, config)
    elif mode == 'chat':
        handle_chat(args, ui, agent, config)
    elif mode == 'scan':
        handle_scan(args, ui, agent, config)
    elif mode == 'portal':
        handle_portal(args, ui, agent, config)
    elif mode == 'install':
        tool = ui.get_user_input("Enter tool name to install: ")
        args.tool = tool
        handle_install(args, ui, agent, installer, validator, config)
    elif mode == 'settings':
        ui.show_info_message("Settings mode - coming soon!")


if __name__ == "__main__":
    main() 