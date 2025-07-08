"""
CONFIGO Enhanced UI Messages
===========================

Rich, interactive UI components for displaying planning steps, tool justifications,
validation results, and real-time progress updates.

Features:
- 🎨 Rich terminal UI with colors and formatting
- 📊 Progress bars and spinners
- 🧠 Tool justification displays
- ✅ Validation result summaries
- 🔄 Real-time status updates
- 🌐 Login portal prompts
- 📈 Memory context displays
"""

import logging
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.live import Live
from rich.tree import Tree
from rich.layout import Layout
from core.planner import PlanningStep, StepStatus, InstallationPlan
from core.enhanced_llm_agent import ToolRecommendation, LLMResponse
from core.validator import ValidationResult, ValidationReport
from core.memory import AgentMemory

logger = logging.getLogger(__name__)

class EnhancedMessageDisplay:
    """
    Enhanced message display with support for planning, justifications, and validation.
    """
    
    def __init__(self, console: Console):
        self.console = console
    
    def show_autonomous_banner(self) -> None:
        """Display the enhanced CONFIGO banner with autonomous agent features."""
        import pyfiglet
        
        # Get the ASCII art banner
        width = self.console.size.width
        if width > 60:
            logo = pyfiglet.figlet_format("CONFIGO", font="slant")
        else:
            logo = "CONFIGO"
        
        # Display the banner
        self.console.print(f"[magenta]{logo}[/magenta]")
        self.console.print("[bold magenta]🚀 CONFIGO: Autonomous AI Setup Agent[/bold magenta]", style="magenta")
        self.console.print("[dim]🧠 Memory • 📋 Planning • 🔧 Self-Healing • ✅ Validation[/dim]")
        self.console.print()
    
    def show_planning_header(self, environment: str):
        """Show the planning process header"""
        self.console.print()
        self.console.print(Panel(
            f"[bold magenta]🧠 CONFIGO Autonomous Agent[/bold magenta]\n"
            f"[bold]Planning setup for:[/bold] {environment}",
            title="🚀 Setup Planning",
            border_style="magenta"
        ))
        self.console.print()
    
    def show_planning_step(self, step: PlanningStep, step_number: int, total_steps: int):
        """Show a single planning step with status"""
        status_icons = {
            StepStatus.PENDING: "⏳",
            StepStatus.IN_PROGRESS: "🔄",
            StepStatus.COMPLETED: "✅",
            StepStatus.FAILED: "❌",
            StepStatus.SKIPPED: "⏭️",
            StepStatus.RETRYING: "🔄"
        }
        
        status_colors = {
            StepStatus.PENDING: "yellow",
            StepStatus.IN_PROGRESS: "blue",
            StepStatus.COMPLETED: "green",
            StepStatus.FAILED: "red",
            StepStatus.SKIPPED: "dim",
            StepStatus.RETRYING: "cyan"
        }
        
        icon = status_icons.get(step.status, "❓")
        color = status_colors.get(step.status, "white")
        
        # Create step display
        step_text = f"{icon} [bold {color}]Step {step_number}/{total_steps}:[/bold {color}] {step.name}"
        
        if step.status == StepStatus.IN_PROGRESS:
            step_text += f"\n   [dim]{step.description}[/dim]"
        elif step.status == StepStatus.COMPLETED:
            step_text += f"\n   [green]✓ {step.description}[/green]"
        elif step.status == StepStatus.FAILED:
            step_text += f"\n   [red]✗ {step.description}[/red]"
            if step.error_message:
                step_text += f"\n   [red]Error: {step.error_message}[/red]"
        elif step.status == StepStatus.RETRYING:
            step_text += f"\n   [cyan]🔄 Retrying (attempt {step.retry_count + 1})[/cyan]"
        
        self.console.print(step_text)
        self.console.print()
    
    def show_planning_progress(self, completed: int, total: int, current_step: str):
        """Show planning progress with progress bar"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Planning: {current_step}", total=total)
            progress.update(task, completed=completed)
    
    def show_tool_justifications(self, tools: List[ToolRecommendation]):
        """Show tool justifications in a formatted table"""
        if not tools:
            return
        
        self.console.print()
        self.console.print("[bold cyan]🧠 Tool Recommendations & Justifications[/bold cyan]")
        self.console.print()
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Priority", style="yellow")
        table.add_column("Justification", style="white")
        table.add_column("Confidence", style="dim")
        
        # Sort by confidence score (higher first)
        sorted_tools = sorted(tools, key=lambda t: t.confidence_score, reverse=True)
        
        for tool in sorted_tools:
            priority_text = f"P{int(tool.confidence_score * 10)}"
            confidence_text = f"{tool.confidence_score:.1%}"
            table.add_row(
                f"🔧 {tool.name}",
                priority_text,
                tool.justification,
                confidence_text
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_enhanced_stack_summary(self, response: LLMResponse):
        """Show enhanced stack summary with confidence and reasoning"""
        self.console.print()
        self.console.print(Panel(
            f"[bold green]Stack Generation Complete![/bold green]\n\n"
            f"📊 [bold]Confidence Score:[/bold] {response.confidence_score:.1%}\n"
            f"🧠 [bold]Reasoning:[/bold] {response.reasoning}\n"
            f"🔧 [bold]Tools:[/bold] {len(response.tools)}\n"
            f"🌐 [bold]Login Portals:[/bold] {len(response.login_portals)}",
            title="🎯 AI-Powered Stack Recommendation",
            border_style="green"
        ))
        self.console.print()
    
    def show_validation_start(self):
        """Show validation process start"""
        self.console.print()
        self.console.print(Panel(
            "[bold blue]🔍 Starting Environment Validation[/bold blue]\n"
            "Checking installed tools and configurations...",
            title="Validation",
            border_style="blue"
        ))
        self.console.print()
    
    def show_validation_progress(self, current: int, total: int, current_tool: str):
        """Show validation progress"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Validating: {current_tool}", total=total)
            progress.update(task, completed=current)
    
    def show_self_healing_start(self, failed_tools: List[ValidationResult]):
        """Show self-healing process start"""
        self.console.print()
        self.console.print(Panel(
            f"[bold cyan]🔧 Starting Self-Healing Process[/bold cyan]\n"
            f"Attempting to fix {len(failed_tools)} failed tools...",
            title="Self-Healing",
            border_style="cyan"
        ))
        self.console.print()
    
    def show_healing_attempt(self, tool_name: str, command: str, source: str):
        """Show a healing attempt"""
        source_text = "Memory" if source == "memory" else "AI Suggestion"
        self.console.print(f"🔄 [cyan]Healing {tool_name}[/cyan] ({source_text})")
        self.console.print(f"   [dim]Command: {command}[/dim]")
    
    def show_memory_context(self, memory: AgentMemory):
        """Show memory context information"""
        self.console.print()
        self.console.rule("[bold blue]🧠 Memory Context[/bold blue]", style="blue")
        
        # Get memory stats
        stats = memory.get_memory_stats()
        
        # Create memory summary table
        table = Table(title="Memory Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Tools", str(stats["total_tools"]))
        table.add_row("Successful Installations", str(stats["successful_installations"]))
        table.add_row("Failed Installations", str(stats["failed_installations"]))
        table.add_row("Total Sessions", str(stats["total_sessions"]))
        table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
        
        self.console.print(table)
        
        # Show recent sessions
        recent_sessions = memory.get_recent_sessions(3)
        if recent_sessions:
            self.console.print("\n[bold cyan]Recent Sessions:[/bold cyan]")
            for session in recent_sessions:
                # Handle both datetime objects and strings
                if hasattr(session.start_time, 'strftime'):
                    time_str = session.start_time.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = str(session.start_time)
                self.console.print(f"  📅 {session.environment} ({time_str})")
        
        # Show failed tools
        failed_tools = memory.get_failed_tools()
        if failed_tools:
            self.console.print("\n[bold yellow]Recently Failed Tools:[/bold yellow]")
            for tool in failed_tools[:3]:  # Show last 3
                self.console.print(f"  ❌ {tool.name} (failed {tool.failure_count} times)")
    
    def show_login_portal_prompt(self, portal_name: str, url: str, description: str):
        """Show login portal prompt with browser opening"""
        self.console.print()
        self.console.print(Panel(
            f"[bold green]🌐 Login Required[/bold green]\n\n"
            f"Portal: [bold]{portal_name}[/bold]\n"
            f"Description: {description}\n"
            f"URL: {url}\n\n"
            f"Opening browser for login...",
            title="Login Portal",
            border_style="green"
        ))
        self.console.print()
    
    def show_completion_with_improvements(self, environment: str, installed_tools: List[str], 
                                        suggestions: List[str]):
        """Show completion message with optional improvements"""
        self.console.print()
        self.console.print(Panel(
            f"[bold green]🎉 Setup Complete![/bold green]\n\n"
            f"Environment: [bold]{environment}[/bold]\n"
            f"Installed Tools: {len(installed_tools)}\n\n"
            f"Your development environment is ready! 🚀",
            title="Setup Complete",
            border_style="green"
        ))
        self.console.print()
        
        if suggestions:
            self.show_improvement_suggestions(suggestions)
    
    def show_error_with_retry(self, error_message: str, tool_name: str, retry_count: int, max_retries: int):
        """Show error message with retry information"""
        self.console.print()
        self.console.print(Panel(
            f"[bold red]❌ Error: {error_message}[/bold red]\n\n"
            f"Tool: [bold]{tool_name}[/bold]\n"
            f"Retry: {retry_count}/{max_retries}\n\n"
            f"Attempting automatic fix...",
            title="Error & Retry",
            border_style="red"
        ))
        self.console.print()
    
    def show_planning_complete(self, total_steps: int, completed_steps: int, failed_steps: int):
        """Show planning completion summary"""
        self.console.print()
        
        status_color = "green" if failed_steps == 0 else "yellow"
        status_icon = "✅" if failed_steps == 0 else "⚠️"
        
        self.console.print(Panel(
            f"{status_icon} [bold {status_color}]Planning Complete[/bold {status_color}]\n\n"
            f"📊 [bold]Steps Completed:[/bold] {completed_steps}/{total_steps}\n"
            f"❌ [bold]Failed Steps:[/bold] {failed_steps}\n"
            f"📈 [bold]Success Rate:[/bold] {(completed_steps/total_steps)*100:.1f}%",
            title="Planning Summary",
            border_style=status_color
        ))
        self.console.print()
    
    def show_welcome(self):
        """Show welcome message"""
        self.console.print()
        self.console.print(Panel(
            "[bold magenta]🧠 Welcome to CONFIGO - Autonomous Development Environment Setup[/bold magenta]\n\n"
            "I'm your AI-powered assistant that will help you set up a complete development environment.\n"
            "I'll remember your preferences, plan the setup, and even fix issues automatically!",
            title="🚀 CONFIGO Agent",
            border_style="magenta"
        ))
        self.console.print()
    
    def show_environment_prompt(self) -> str:
        """Show environment prompt and get user input"""
        self.console.print()
        self.console.print(Panel(
            "[bold cyan]What type of development environment would you like to set up?[/bold cyan]\n\n"
            "Examples:\n"
            "• Full Stack AI Development\n"
            "• Web Development (React/Node.js)\n"
            "• Data Science & Machine Learning\n"
            "• Mobile Development\n"
            "• DevOps & Cloud\n\n"
            "Describe your environment:",
            title="Environment Setup",
            border_style="cyan"
        ))
        self.console.print()
        
        # Get user input
        from prompt_toolkit import prompt
        from prompt_toolkit.styles import Style
        
        style = Style.from_dict({
            'prompt': 'bold cyan',
        })
        
        user_input = prompt('> ', style=style)
        return user_input.strip()
    
    def show_error_message(self, message: str):
        """Show error message"""
        self.console.print()
        self.console.print(Panel(
            f"[bold red]❌ Error: {message}[/bold red]",
            title="Error",
            border_style="red"
        ))
        self.console.print()
    
    def show_detection_start(self):
        """Show detection start message"""
        self.console.print()
        self.console.print(Panel(
            "[bold blue]🔍 Detecting installed tools...[/bold blue]",
            title="Detection",
            border_style="blue"
        ))
        self.console.print()
    
    def show_detection_complete(self, installed_count: int, total_count: int):
        """Show detection complete message"""
        self.console.print()
        self.console.print(Panel(
            f"[bold green]✅ Detection Complete[/bold green]\n\n"
            f"Found {installed_count} already installed tools out of {total_count} total.",
            title="Detection Results",
            border_style="green"
        ))
        self.console.print()
    
    def show_installation_start(self):
        """Show installation start message"""
        self.console.print()
        self.console.print(Panel(
            "[bold yellow]🔧 Starting installation...[/bold yellow]",
            title="Installation",
            border_style="yellow"
        ))
        self.console.print()
    
    def show_installation_prompt(self) -> bool:
        """Show installation prompt and get user confirmation"""
        self.console.print()
        self.console.print(Panel(
            "[bold green]Ready to install the recommended tools?[/bold green]\n\n"
            "This will set up your complete development environment.\n"
            "The process is automated and safe.",
            title="Installation Confirmation",
            border_style="green"
        ))
        self.console.print()
        
        # Get user confirmation
        from prompt_toolkit import prompt
        from prompt_toolkit.styles import Style
        
        style = Style.from_dict({
            'prompt': 'bold green',
        })
        
        user_input = prompt('Proceed? (y/N): ', style=style)
        return user_input.strip().lower() in ['y', 'yes']
    
    def show_aborted_message(self):
        """Show aborted message"""
        self.console.print()
        self.console.print(Panel(
            "[bold yellow]⚠️ Setup aborted by user[/bold yellow]",
            title="Setup Aborted",
            border_style="yellow"
        ))
        self.console.print()
    
    def show_planning_steps(self, plan: InstallationPlan) -> None:
        """Display the installation plan with steps and justifications."""
        self.console.print()
        self.console.rule(f"[bold green]📋 Installation Plan: {plan.environment}[/bold green]", style="green")
        
        # Plan summary
        self.console.print(f"[cyan]📊 Plan ID: {plan.plan_id}[/cyan]")
        self.console.print(f"[cyan]⏱️  Estimated Duration: {plan.estimated_duration} minutes[/cyan]")
        self.console.print(f"[cyan]📦 Total Steps: {plan.total_steps}[/cyan]")
        
        # Create steps tree
        tree = Tree("🔧 Installation Steps")
        
        # Group steps by type
        tool_steps = [step for step in plan.steps if step.step_type.value == "tool_install"]
        extension_steps = [step for step in plan.steps if step.step_type.value == "extension_install"]
        portal_steps = [step for step in plan.steps if step.step_type.value == "login_portal"]
        validation_steps = [step for step in plan.steps if step.step_type.value == "validation"]
        
        # Add tool installation steps
        if tool_steps:
            tool_branch = tree.add("🔧 Base Tools")
            for step in tool_steps:
                self._add_step_to_tree(tool_branch, step)
        
        # Add extension steps
        if extension_steps:
            ext_branch = tree.add("🔌 Extensions")
            for step in extension_steps:
                self._add_step_to_tree(ext_branch, step)
        
        # Add login portal steps
        if portal_steps:
            portal_branch = tree.add("🌐 Login Portals")
            for step in portal_steps:
                self._add_step_to_tree(portal_branch, step)
        
        # Add validation steps
        if validation_steps:
            validation_branch = tree.add("✅ Validation")
            for step in validation_steps:
                self._add_step_to_tree(validation_branch, step)
        
        self.console.print(tree)
    
    def _add_step_to_tree(self, parent, step: PlanningStep) -> None:
        """Add a step to the tree with status and justification."""
        # Status icon
        status_icon = {
            StepStatus.PENDING: "⏳",
            StepStatus.IN_PROGRESS: "🔄",
            StepStatus.COMPLETED: "✅",
            StepStatus.FAILED: "❌",
            StepStatus.SKIPPED: "⏭️",
            StepStatus.RETRYING: "🔄"
        }.get(step.status, "❓")
        
        # Confidence indicator
        confidence_color = "green" if step.confidence_score >= 0.8 else "yellow" if step.confidence_score >= 0.6 else "red"
        
        # Create step label
        step_label = f"{status_icon} {step.name} ([{confidence_color}]{step.confidence_score:.1f}[/{confidence_color}])"
        
        step_branch = parent.add(step_label)
        
        # Add justification
        if step.justification:
            step_branch.add(f"[dim]💡 {step.justification}[/dim]")
        
        # Add dependencies if any
        if step.dependencies:
            deps_text = ", ".join(step.dependencies)
            step_branch.add(f"[dim]🔗 Depends on: {deps_text}[/dim]")
    
    def show_step_progress(self, step: PlanningStep, current: int, total: int) -> None:
        """Show progress for a specific step."""
        self.console.print()
        self.console.rule(f"[bold yellow]🔄 Executing Step {current}/{total}[/bold yellow]", style="yellow")
        
        # Step details
        self.console.print(f"[bold cyan]📦 {step.name}[/bold cyan]")
        self.console.print(f"[dim]📝 {step.description}[/dim]")
        
        # Justification
        if step.justification:
            self.console.print(f"[dim]💡 {step.justification}[/dim]")
        
        # Command being executed
        if step.command:
            self.console.print(f"[dim]💻 {step.command}[/dim]")
        
        # Confidence score
        confidence_color = "green" if step.confidence_score >= 0.8 else "yellow" if step.confidence_score >= 0.6 else "red"
        self.console.print(f"[{confidence_color}]🎯 Confidence: {step.confidence_score:.1f}[/{confidence_color}]")
    
    def show_step_result(self, step: PlanningStep, success: bool, version: Optional[str] = None, error: Optional[str] = None) -> None:
        """Show the result of a step execution."""
        if success:
            self.console.print(f"[bold green]✅ {step.name} completed successfully[/bold green]")
            if version:
                self.console.print(f"[dim]📦 Version: {version}[/dim]")
        else:
            self.console.print(f"[bold red]❌ {step.name} failed[/bold red]")
            if error:
                self.console.print(f"[dim]💥 Error: {error}[/dim]")
        
        self.console.print()
    
    def show_validation_results(self, report: ValidationReport) -> None:
        """Display validation results with detailed information."""
        self.console.print()
        self.console.rule("[bold blue]✅ Post-Installation Validation[/bold blue]", style="blue")
        
        # Summary
        self.console.print(f"[cyan]📊 Validation Summary:[/cyan]")
        self.console.print(f"  📦 Total Tools: {report.total_tools}")
        self.console.print(f"  ✅ Successful: {report.successful_validations}")
        self.console.print(f"  ❌ Failed: {report.failed_validations}")
        self.console.print(f"  ⏭️  Skipped: {report.skipped_validations}")
        self.console.print(f"  📈 Success Rate: {report.overall_success_rate:.1f}%")
        
        # Create validation results table
        if report.validation_results:
            table = Table(title="Validation Results", show_header=True, header_style="bold magenta")
            table.add_column("Tool", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Version", style="blue")
            table.add_column("Confidence", style="yellow")
            table.add_column("Error", style="red")
            
            for result in report.validation_results:
                # Status icon
                status_icon = "✅" if result.is_installed else "❌" if result.error_message != "Skipped based on memory" else "⏭️"
                status_text = "Installed" if result.is_installed else "Failed" if result.error_message != "Skipped based on memory" else "Skipped"
                
                # Version
                version_text = result.version or "N/A"
                
                # Confidence
                confidence_color = "green" if result.confidence >= 0.8 else "yellow" if result.confidence >= 0.6 else "red"
                confidence_text = f"[{confidence_color}]{result.confidence:.1f}[/{confidence_color}]"
                
                # Error (truncated)
                error_text = result.error_message[:50] + "..." if result.error_message and len(result.error_message) > 50 else result.error_message or ""
                
                table.add_row(
                    result.tool_name,
                    f"{status_icon} {status_text}",
                    version_text,
                    confidence_text,
                    error_text
                )
            
            self.console.print(table)
        
        # Recommendations
        if report.recommendations:
            self.console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
            for rec in report.recommendations:
                self.console.print(f"  • {rec}")
    
    def show_self_healing_progress(self, failed_tools: List[ValidationResult]) -> None:
        """Show self-healing progress."""
        if not failed_tools:
            return
        
        self.console.print()
        self.console.rule("[bold orange]🔧 Self-Healing Attempts[/bold orange]", style="orange")
        
        self.console.print(f"[orange]🔄 Attempting to heal {len(failed_tools)} failed tools...[/orange]")
        
        for tool in failed_tools:
            self.console.print(f"  🔧 [bold]{tool.tool_name}[/bold] - {tool.error_message}")
    
    def show_healing_result(self, tool_name: str, success: bool, fix_command: Optional[str] = None) -> None:
        """Show the result of a self-healing attempt."""
        if success:
            self.console.print(f"  [bold green]✅ {tool_name} healed successfully[/bold green]")
            if fix_command:
                self.console.print(f"    [dim]💻 Used: {fix_command}[/dim]")
        else:
            self.console.print(f"  [bold red]❌ {tool_name} healing failed[/bold red]")
    
    def show_login_portals(self, portals: List[Dict[str, str]]) -> None:
        """Display login portals with enhanced information."""
        if not portals:
            return
        
        self.console.print()
        self.console.rule("[bold blue]🌐 Login Portals[/bold blue]", style="blue")
        
        table = Table(title="Required Logins", show_header=True, header_style="bold magenta")
        table.add_column("Portal", style="cyan")
        table.add_column("URL", style="blue")
        table.add_column("Description", style="green")
        table.add_column("Justification", style="yellow")
        
        for portal in portals:
            table.add_row(
                portal.get("name", "Unknown"),
                portal.get("url", ""),
                portal.get("description", ""),
                portal.get("justification", "")
            )
        
        self.console.print(table)
        
        self.console.print("\n[bold cyan]💡 Next Steps:[/bold cyan]")
        self.console.print("  1. Complete the required logins in your browser")
        self.console.print("  2. Set up any necessary API keys or authentication")
        self.console.print("  3. Configure your development environment preferences")
    
    def show_improvement_suggestions(self, suggestions: List[str]) -> None:
        """Display improvement suggestions."""
        if not suggestions:
            return
        
        self.console.print()
        self.console.rule("[bold purple]💡 Improvement Suggestions[/bold purple]", style="purple")
        
        for i, suggestion in enumerate(suggestions, 1):
            self.console.print(f"  {i}. {suggestion}")
        
        self.console.print("\n[dim]💡 These are optional enhancements to improve your development experience.[/dim]")
    
    def show_completion_summary(self, plan: InstallationPlan, validation_report: ValidationReport, 
                              healing_results: List[Dict[str, Any]]) -> None:
        """Show comprehensive completion summary."""
        self.console.print()
        self.console.rule("[bold green]🎉 Installation Complete![/bold green]", style="green")
        
        # Overall statistics
        total_healed = len([r for r in healing_results if r.get("success", False)])
        
        self.console.print("[bold cyan]📊 Final Statistics:[/bold cyan]")
        self.console.print(f"  📦 Total Tools: {plan.total_steps}")
        self.console.print(f"  ✅ Successfully Installed: {plan.completed_steps}")
        self.console.print(f"  ❌ Failed: {plan.failed_steps}")
        self.console.print(f"  ⏭️  Skipped: {plan.skipped_steps}")
        self.console.print(f"  🔧 Self-Healed: {total_healed}")
        self.console.print(f"  📈 Overall Success Rate: {validation_report.overall_success_rate:.1f}%")
        
        # Success message
        if validation_report.overall_success_rate >= 80:
            self.console.print("\n[bold green]🎉 Excellent! Your development environment is ready![/bold green]")
        elif validation_report.overall_success_rate >= 60:
            self.console.print("\n[bold yellow]👍 Good! Your development environment is mostly ready.[/bold yellow]")
        else:
            self.console.print("\n[bold red]⚠️  Some tools failed installation. Consider manual setup.[/bold red]")
        
        # Next steps
        self.console.print("\n[bold cyan]🚀 Next Steps:[/bold cyan]")
        self.console.print("  1. Complete any remaining browser logins")
        self.console.print("  2. Configure your development environment")
        self.console.print("  3. Set up any required API keys")
        self.console.print("  4. Start coding! 🎯")
        
        # Memory update
        self.console.print("\n[dim]💾 Your installation history has been saved to memory for future sessions.[/dim]")
    
    def show_error_with_context(self, error: str, context: str = "") -> None:
        """Show error with additional context."""
        self.console.print()
        self.console.rule("[bold red]❌ Error[/bold red]", style="red")
        self.console.print(f"[red]❌ {error}[/red]")
        
        if context:
            self.console.print(f"[dim]📋 Context: {context}[/dim]")
    
    def show_memory_cleared(self) -> None:
        """Show message when memory is cleared."""
        self.console.print()
        self.console.rule("[bold yellow]🧹 Memory Cleared[/bold yellow]", style="yellow")
        self.console.print("[yellow]🧹 All memory data has been cleared.[/yellow]")
        self.console.print("[dim]💡 The agent will start fresh on the next run.[/dim]")
    
    def show_retry_attempt(self, tool_name: str, attempt: int, max_attempts: int) -> None:
        """Show retry attempt information."""
        self.console.print(f"[yellow]🔄 Retrying {tool_name} (attempt {attempt}/{max_attempts})[/yellow]")
    
    def show_plan_execution_progress(self, progress: Dict[str, Any]) -> None:
        """Show overall plan execution progress."""
        total = progress["total_steps"]
        completed = progress["completed_steps"]
        failed = progress["failed_steps"]
        skipped = progress["skipped_steps"]
        in_progress = progress["in_progress"]
        pending = progress["pending_steps"]
        percentage = progress["progress_percentage"]
        remaining = progress["estimated_remaining"]
        
        self.console.print(f"\n[cyan]📊 Progress: {completed}/{total} completed ({percentage:.1f}%)[/cyan]")
        self.console.print(f"[cyan]⏱️  Estimated remaining: {remaining} minutes[/cyan]")
        
        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress_bar:
            task = progress_bar.add_task("Installing tools...", total=total)
            progress_bar.update(task, completed=completed)
    
    def show_domain_detection(self, detected_domain: str, confidence: float) -> None:
        """Show domain detection results."""
        self.console.print()
        self.console.rule("[bold purple]🎯 Domain Detection[/bold purple]", style="purple")
        
        domain_names = {
            "ai_ml": "AI/ML Development",
            "web_dev": "Web Development",
            "data_science": "Data Science",
            "devops": "DevOps/Infrastructure"
        }
        
        domain_name = domain_names.get(detected_domain, detected_domain)
        confidence_color = "green" if confidence >= 0.8 else "yellow" if confidence >= 0.6 else "red"
        
        self.console.print(f"[bold cyan]🎯 Detected Domain: {domain_name}[/bold cyan]")
        self.console.print(f"[{confidence_color}]📊 Confidence: {confidence:.1f}[/{confidence_color}]")
        
        # Domain-specific information
        domain_info = {
            "ai_ml": "Focusing on AI/ML tools: Python, Jupyter, Cursor, AI extensions",
            "web_dev": "Focusing on web development: Node.js, VS Code, web extensions",
            "data_science": "Focusing on data science: Python, Jupyter, data analysis tools",
            "devops": "Focusing on DevOps: Docker, Terraform, cloud CLI tools"
        }
        
        info = domain_info.get(detected_domain, "Using general development tools")
        self.console.print(f"[dim]💡 {info}[/dim]") 