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
from config.config import Config


def setup_logging(debug: bool = False) -> None:
    """Configure logging for CONFIGO."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
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
    
    # Knowledge commands
    knowledge_parser = subparsers.add_parser('knowledge', help='Knowledge base operations')
    knowledge_parser.add_argument('action', choices=['stats', 'backup', 'clear', 'refresh'], help='Knowledge action')
    knowledge_parser.add_argument('--path', help='Backup path')
    knowledge_parser.add_argument('--domain', help='Domain for refresh (e.g., "ai stack", "devops essentials")')
    knowledge_parser.add_argument('--force', action='store_true', help='Force refresh even if domain exists')
    
    # Scheduler commands
    scheduler_parser = subparsers.add_parser('scheduler', help='Knowledge scheduler operations')
    scheduler_parser.add_argument('action', choices=['start', 'stop', 'status', 'add', 'remove', 'list', 'history'], help='Scheduler action')
    scheduler_parser.add_argument('--domain', help='Domain for scheduled expansion')
    scheduler_parser.add_argument('--schedule', choices=['daily', 'weekly', 'monthly'], default='daily', help='Schedule frequency')
    scheduler_parser.add_argument('--task-id', help='Task ID for removal')
    
    # Graph commands
    graph_parser = subparsers.add_parser('graph', help='Graph database operations')
    graph_parser.add_argument('action', choices=['visualize', 'query', 'stats', 'expand'], help='Graph action')
    graph_parser.add_argument('--plan', help='Plan name for visualization')
    graph_parser.add_argument('--domain', help='Domain to expand')
    graph_parser.add_argument('--limit', type=int, default=10, help='Limit for query results')
    
    # Vector commands
    vector_parser = subparsers.add_parser('vector', help='Vector database operations')
    vector_parser.add_argument('action', choices=['search', 'similar', 'stats'], help='Vector action')
    vector_parser.add_argument('query', help='Search query')
    vector_parser.add_argument('--limit', type=int, default=5, help='Maximum results')
    
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
        elif args.command == 'scheduler':
            handle_scheduler(args, ui, knowledge, config)
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
    """Handle install commands."""
    tool_name = args.tool
    force = args.force
    
    ui.show_info_message(f"🔧 Installing {tool_name}...")
    
    try:
        # Get system information for logging
        import platform
        import os
        from datetime import datetime
        
        os_type = platform.system().lower()
        architecture = platform.machine()
        user_id = os.getenv('USER', 'unknown')
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Attempt installation
        success = installer.install_tool(tool_name, force=force)
        
        # Log the install event to knowledge graph
        knowledge = agent.knowledge_engine
        if knowledge and hasattr(knowledge, 'log_install_event'):
            # Get error message if installation failed
            error_message = None
            if not success:
                # Try to get the last error from the installer
                if hasattr(installer, 'last_error'):
                    error_message = installer.last_error
                else:
                    error_message = f"Installation failed for {tool_name}"
            
            # Log the event
            knowledge.log_install_event(
                tool_name=tool_name,
                command=f"configo install {tool_name}",
                success=success,
                os_type=os_type,
                architecture=architecture,
                error_message=error_message,
                user_id=user_id,
                session_id=session_id,
                retry_count=0
            )
            
            # If successful, update tool statistics
            if success and hasattr(knowledge, 'graph_db'):
                # Update tool success rate
                knowledge.graph_db.log_install_event(
                    tool_name=tool_name,
                    command=f"configo install {tool_name}",
                    success=True,
                    os_type=os_type,
                    architecture=architecture,
                    user_id=user_id,
                    session_id=session_id
                )
        
        if success:
            ui.show_success_message(f"✅ {tool_name} installed successfully!")
            
            # Validate installation
            ui.show_info_message("🔍 Validating installation...")
            validation_result = validator.validate_tool(tool_name)
            
            if validation_result.is_valid:
                ui.show_success_message(f"✅ {tool_name} validation passed!")
            else:
                ui.show_warning_message(f"⚠️ {tool_name} installed but validation failed:")
                for issue in validation_result.issues:
                    ui.show_warning_message(f"   • {issue}")
        else:
            ui.show_error_message(f"❌ Failed to install {tool_name}")
            
            # Show helpful suggestions
            ui.show_info_message("💡 Suggestions:")
            ui.show_info_message("   • Check your internet connection")
            ui.show_info_message("   • Try running with --force flag")
            ui.show_info_message("   • Check if the tool name is correct")
            
    except Exception as e:
        ui.show_error_message(f"❌ Installation error: {e}")
        
        # Log the error event
        try:
            knowledge = agent.knowledge_engine
            if knowledge and hasattr(knowledge, 'log_install_event'):
                knowledge.log_install_event(
                    tool_name=tool_name,
                    command=f"configo install {tool_name}",
                    success=False,
                    os_type=platform.system().lower(),
                    architecture=platform.machine(),
                    error_message=str(e),
                    user_id=os.getenv('USER', 'unknown'),
                    session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
        except Exception as log_error:
            logger.error(f"Failed to log install error: {log_error}")


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
    elif args.action == 'expand':
        domain = args.domain or ui.get_user_input("Enter domain to expand (e.g., 'ai stack'): ")
        if domain:
            ui.show_info_message(f"Expanding knowledge for domain: {domain}")
            success = knowledge.expand_graph_from_gemini(domain)
            if success:
                ui.show_success_message(f"Successfully expanded knowledge for {domain}")
            else:
                ui.show_error_message(f"Failed to expand knowledge for {domain}")
        else:
            ui.show_error_message("No domain specified for expansion")

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
        # Get comprehensive statistics
        graph_stats = knowledge.get_graph_statistics()
        vector_stats = knowledge.get_vector_stats()
        
        ui.show_info_message("🧠 CONFIGO Knowledge Base Statistics")
        ui.show_info_message("=" * 50)
        
        # Graph statistics
        if graph_stats:
            ui.show_info_message(f"📊 Graph Database:")
            ui.show_info_message(f"   🧠 Total Nodes: {graph_stats.get('total_nodes', 0)}")
            ui.show_info_message(f"   🔗 Total Relationships: {graph_stats.get('total_relationships', 0)}")
            
            # Node breakdown
            node_counts = graph_stats.get('node_counts', {})
            if node_counts:
                ui.show_info_message("   📈 Node Breakdown:")
                for node_type, count in node_counts.items():
                    ui.show_info_message(f"      • {node_type}: {count}")
            
            # Top tools
            top_tools = graph_stats.get('top_installed_tools', [])
            if top_tools:
                ui.show_info_message("   🔧 Top 5 Installed Tools:")
                for i, tool in enumerate(top_tools[:5], 1):
                    ui.show_info_message(f"      {i}. {tool.get('name', 'Unknown')} ({tool.get('installs', 0)} installs)")
            
            # Common failures
            common_failures = graph_stats.get('most_common_failures', [])
            if common_failures:
                ui.show_info_message("   🛠️ Most Common Failures:")
                for i, failure in enumerate(common_failures[:5], 1):
                    ui.show_info_message(f"      {i}. {failure.get('message', 'Unknown')} ({failure.get('tool', 'Unknown')})")
            
            # Recent activity
            recent_activity = graph_stats.get('recent_activity', {})
            if recent_activity:
                ui.show_info_message("   📅 Recent Activity (7 days):")
                ui.show_info_message(f"      • Total Installs: {recent_activity.get('recent_installs', 0)}")
                ui.show_info_message(f"      • Successful: {recent_activity.get('successful', 0)}")
                ui.show_info_message(f"      • Failed: {recent_activity.get('failed', 0)}")
        
        # Vector statistics
        if vector_stats:
            ui.show_info_message(f"🔍 Vector Database:")
            ui.show_info_message(f"   📚 Total Documents: {vector_stats.get('total_documents', 0)}")
            ui.show_info_message(f"   🎯 Embedding Model: {vector_stats.get('embedding_model', 'Unknown')}")
        
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
        domain = args.domain or ui.get_user_input("Enter domain to refresh (e.g., 'ai stack', 'devops essentials'): ")
        if domain:
            ui.show_info_message(f"🔄 Refreshing knowledge for domain: {domain}")
            ui.show_info_message("This may take a few moments...")
            
            success = knowledge.expand_graph_from_gemini(domain)
            if success:
                ui.show_success_message(f"✅ Successfully refreshed knowledge for '{domain}'")
                
                # Show updated statistics
                graph_stats = knowledge.get_graph_statistics()
                if graph_stats:
                    ui.show_info_message(f"📊 Updated Statistics:")
                    ui.show_info_message(f"   🧠 Total Nodes: {graph_stats.get('total_nodes', 0)}")
                    ui.show_info_message(f"   🔗 Total Relationships: {graph_stats.get('total_relationships', 0)}")
            else:
                ui.show_error_message(f"❌ Failed to refresh knowledge for '{domain}'")
                ui.show_info_message("💡 Try using a different domain or check your internet connection")
        else:
            ui.show_error_message("No domain specified")


def handle_scheduler(args: argparse.Namespace, ui: EnhancedTerminalUI, knowledge: KnowledgeEngine, config: Config) -> None:
    """Handle scheduler commands."""
    if args.action == 'start':
        domain = args.domain or ui.get_user_input("Enter domain to schedule expansion (e.g., 'ai stack'): ")
        if domain:
            schedule = args.schedule
            ui.show_info_message(f"🚀 Scheduling daily expansion for domain: {domain}")
            success = knowledge.schedule_knowledge_expansion(domain, schedule)
            if success:
                ui.show_success_message(f"✅ Successfully scheduled daily expansion for '{domain}'")
            else:
                ui.show_error_message(f"❌ Failed to schedule daily expansion for '{domain}'")
        else:
            ui.show_error_message("No domain specified for scheduling")
    elif args.action == 'stop':
        task_id = args.task_id or ui.get_user_input("Enter task ID to stop (e.g., '12345'): ")
        if task_id:
            ui.show_info_message(f"🛑 Stopping task with ID: {task_id}")
            success = knowledge.stop_scheduled_task(task_id)
            if success:
                ui.show_success_message(f"✅ Successfully stopped task with ID: {task_id}")
            else:
                ui.show_error_message(f"❌ Failed to stop task with ID: {task_id}")
        else:
            ui.show_error_message("No task ID specified for stopping")
    elif args.action == 'status':
        ui.show_info_message("📊 Current Scheduled Tasks:")
        tasks = knowledge.get_scheduled_tasks()
        if tasks:
            for i, task in enumerate(tasks, 1):
                ui.show_info_message(f"  {i}. ID: {task.get('id', 'N/A')}, Domain: {task.get('domain', 'N/A')}, Schedule: {task.get('schedule', 'N/A')}, Status: {task.get('status', 'N/A')}")
        else:
            ui.show_info_message("No scheduled tasks found.")
    elif args.action == 'history':
        ui.show_info_message("📜 Task History:")
        history = knowledge.get_task_history()
        if history:
            for i, task in enumerate(history, 1):
                ui.show_info_message(f"  {i}. ID: {task.get('id', 'N/A')}, Domain: {task.get('domain', 'N/A')}, Status: {task.get('status', 'N/A')}, Timestamp: {task.get('timestamp', 'N/A')}")
        else:
            ui.show_info_message("No task history found.")
    elif args.action == 'list':
        ui.show_info_message("🔗 Available Domains for Scheduling:")
        domains = knowledge.get_available_domains_for_scheduling()
        if domains:
            for i, domain in enumerate(domains, 1):
                ui.show_info_message(f"  {i}. {domain}")
        else:
            ui.show_info_message("No domains found for scheduling.")


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