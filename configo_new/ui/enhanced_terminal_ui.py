"""
CONFIGO Enhanced Terminal UI
===========================

🚀 Modern, beautiful terminal interface for CONFIGO with rich formatting,
animations, and professional styling.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.tree import Tree
from rich.layout import Layout
from rich import box
from rich.emoji import Emoji

logger = logging.getLogger(__name__)


@dataclass
class UIConfig:
    """UI Configuration for CONFIGO."""
    primary_color: str = "cyan"
    success_color: str = "green"
    warning_color: str = "yellow"
    error_color: str = "red"
    info_color: str = "blue"
    muted_color: str = "dim white"
    accent_color: str = "magenta"
    background_color: str = "black"
    
    # Animation settings
    animation_speed: float = 0.1
    spinner_style: str = "cyan"
    
    # Layout settings
    header_size: int = 3
    footer_size: int = 2
    panel_padding: Tuple[int, int] = (1, 2)
    
    # Theme
    theme_name: str = "CONFIGO_DARK"
    use_emoji: bool = True
    use_animations: bool = True


class EnhancedTerminalUI:
    """
    Enhanced Terminal UI for CONFIGO with modern styling and animations.
    """
    
    def __init__(self, config: Optional[UIConfig] = None):
        """Initialize the enhanced terminal UI."""
        self.config = config or UIConfig()
        self.console = Console()
        self.layout = Layout()
        
        # Initialize layout
        self._setup_layout()
        
        # Animation state
        self._animation_tasks = {}
        self._live_displays = {}
        
        logger.info("Enhanced Terminal UI initialized")
    
    def _setup_layout(self) -> None:
        """Setup the main layout structure."""
        self.layout.split_column(
            Layout(name="header", size=self.config.header_size),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=self.config.footer_size)
        )
    
    def show_banner(self) -> None:
        """Display the enhanced CONFIGO banner with animations."""
        banner_text = Text()
        banner_text.append("🚀 ", style=f"bold {self.config.primary_color}")
        banner_text.append("CONFIGO", style=f"bold {self.config.accent_color}")
        banner_text.append(" - Autonomous AI Setup Agent", style=self.config.muted_color)
        
        banner_panel = Panel(
            Align.center(banner_text),
            border_style=self.config.primary_color,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(banner_panel)
        self.console.print()  # Add spacing
    
    def show_welcome_animation(self) -> None:
        """Show welcome animation."""
        if not self.config.use_animations:
            return
        
        welcome_text = Text()
        welcome_text.append("Welcome to ", style=self.config.muted_color)
        welcome_text.append("CONFIGO", style=f"bold {self.config.accent_color}")
        welcome_text.append("! 🎉", style=self.config.primary_color)
        
        with Live(
            Panel(Align.center(welcome_text), border_style=self.config.primary_color),
            console=self.console,
            refresh_per_second=10
        ) as live:
            for i in range(20):
                time.sleep(0.1)
                # Add some animation effect
                if i % 2 == 0:
                    live.update(Panel(Align.center(welcome_text), border_style=self.config.accent_color))
                else:
                    live.update(Panel(Align.center(welcome_text), border_style=self.config.primary_color))
    
    def show_welcome_screen(self) -> int:
        """Show welcome screen with mode selection."""
        self.console.clear()
        self.show_banner()
        
        # Welcome message
        welcome_panel = Panel(
            Markdown("""
# Welcome to CONFIGO! 🚀

I'm your intelligent development environment setup assistant. 
I can help you install tools, set up environments, and provide guidance.

**What would you like to do?**
            """),
            border_style=self.config.primary_color,
            title="Welcome",
            title_align="center"
        )
        self.console.print(welcome_panel)
        self.console.print()
        
        # Mode selection table
        table = Table(title="Available Modes", show_header=True, header_style=self.config.accent_color)
        table.add_column("Number", style=self.config.primary_color, width=8)
        table.add_column("Mode", style=self.config.accent_color, width=20)
        table.add_column("Description", style=self.config.muted_color)
        
        modes = [
            (1, "Setup", "Complete development environment setup"),
            (2, "Chat", "Interactive AI assistant"),
            (3, "Scan", "Analyze current project"),
            (4, "Portal", "Launch login portals"),
            (5, "Install", "Install specific tool"),
            (6, "Settings", "Configure CONFIGO")
        ]
        
        for number, mode, description in modes:
            table.add_row(str(number), mode, description)
        
        self.console.print(table)
        self.console.print()
        
        # Get user choice
        choice = Prompt.ask(
            "Select a mode",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )
        
        return int(choice)
    
    def show_mode_header(self, mode: str, description: str) -> None:
        """Show mode header with description."""
        header_text = Text()
        header_text.append(f"🎯 {mode}", style=f"bold {self.config.accent_color}")
        header_text.append(f" - {description}", style=self.config.muted_color)
        
        header_panel = Panel(
            Align.center(header_text),
            border_style=self.config.accent_color,
            box=box.ROUNDED
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def show_ai_reasoning(self, title: str, content: str, confidence: float = 1.0) -> None:
        """Show AI reasoning with syntax highlighting."""
        # Create confidence indicator
        confidence_text = Text()
        if confidence > 0.8:
            confidence_text.append("🔍 High Confidence", style=self.config.success_color)
        elif confidence > 0.5:
            confidence_text.append("🤔 Medium Confidence", style=self.config.warning_color)
        else:
            confidence_text.append("❓ Low Confidence", style=self.config.error_color)
        
        # Format content as code if it looks like code
        if any(keyword in content.lower() for keyword in ['install', 'command', 'sudo', 'apt-get']):
            formatted_content = Syntax(content, "bash", theme="monokai")
        else:
            formatted_content = Markdown(content)
        
        reasoning_panel = Panel(
            Group(
                Align.right(confidence_text),
                formatted_content
            ),
            title=f"🤖 {title}",
            border_style=self.config.info_color,
            box=box.ROUNDED
        )
        
        self.console.print(reasoning_panel)
        self.console.print()
    
    def show_tool_detection_table(self, tools: List[Dict[str, Any]]) -> None:
        """Show tool detection results in a table."""
        if not tools:
            self.console.print("No tools detected.", style=self.config.muted_color)
            return
        
        table = Table(title="🔍 Detected Tools", show_header=True, header_style=self.config.accent_color)
        table.add_column("Tool", style=self.config.primary_color, width=20)
        table.add_column("Type", style=self.config.info_color, width=15)
        table.add_column("Version", style=self.config.success_color, width=15)
        table.add_column("Confidence", style=self.config.warning_color, width=12)
        table.add_column("Recommendations", style=self.config.muted_color)
        
        for tool in tools:
            confidence = tool.get('confidence', 0.0)
            confidence_text = f"{confidence:.1%}"
            
            recommendations = tool.get('recommendations', [])
            recommendations_text = "; ".join(recommendations[:2])  # Limit to 2 recommendations
            
            table.add_row(
                tool.get('name', 'Unknown'),
                tool.get('type', 'Unknown'),
                tool.get('version', 'Unknown'),
                confidence_text,
                recommendations_text
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_installation_progress(self, tool_name: str, total_steps: int = 100) -> Tuple[Progress, int]:
        """Show installation progress for a tool."""
        progress = Progress(
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        
        task_id = progress.add_task(f"Installing {tool_name}...", total=total_steps)
        
        return progress, task_id
    
    def show_llm_api_call(self, description: str = "Calling AI API...") -> Progress:
        """Show LLM API call progress."""
        progress = Progress(
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        
        progress.add_task(description, total=None)
        
        return progress
    
    def show_planning_steps(self, steps: List[Dict[str, Any]]) -> None:
        """Show installation planning steps."""
        if not steps:
            self.console.print("No steps planned.", style=self.config.muted_color)
            return
        
        tree = Tree("📋 Installation Plan", style=self.config.accent_color)
        
        for i, step in enumerate(steps, 1):
            step_text = f"{i}. {step.get('name', 'Unknown step')}"
            step_node = tree.add(step_text, style=self.config.primary_color)
            
            # Add step details
            description = step.get('description', '')
            if description:
                step_node.add(f"📝 {description}", style=self.config.muted_color)
            
            tool_name = step.get('tool_name', '')
            if tool_name:
                step_node.add(f"🔧 Tool: {tool_name}", style=self.config.info_color)
            
            command = step.get('command', '')
            if command:
                step_node.add(f"⚡ Command: {command}", style=self.config.warning_color)
        
        self.console.print(tree)
        self.console.print()
    
    def show_success_message(self, message: str, details: Optional[str] = None) -> None:
        """Show success message with optional details."""
        success_text = Text()
        success_text.append("✅ ", style=self.config.success_color)
        success_text.append(message, style=f"bold {self.config.success_color}")
        
        if details:
            success_text.append(f"\n{details}", style=self.config.muted_color)
        
        success_panel = Panel(
            success_text,
            border_style=self.config.success_color,
            box=box.ROUNDED
        )
        
        self.console.print(success_panel)
        self.console.print()
    
    def show_error_message(self, error: str, suggestion: str = "", retry_info: str = "") -> None:
        """Show error message with suggestions."""
        error_text = Text()
        error_text.append("❌ ", style=self.config.error_color)
        error_text.append(error, style=f"bold {self.config.error_color}")
        
        if suggestion:
            error_text.append(f"\n💡 Suggestion: {suggestion}", style=self.config.warning_color)
        
        if retry_info:
            error_text.append(f"\n🔧 Technical Details: {retry_info}", style=self.config.muted_color)
        
        error_panel = Panel(
            error_text,
            border_style=self.config.error_color,
            box=box.ROUNDED
        )
        
        self.console.print(error_panel)
        self.console.print()
    
    def show_info_message(self, message: str, icon: str = "ℹ️") -> None:
        """Show informational message."""
        info_text = Text()
        info_text.append(f"{icon} ", style=self.config.info_color)
        info_text.append(message, style=self.config.info_color)
        
        self.console.print(info_text)
    
    def show_validation_results(self, results: List[Dict[str, Any]]) -> None:
        """Show validation results."""
        if not results:
            self.console.print("No validation results to show.", style=self.config.muted_color)
            return
        
        table = Table(title="✅ Validation Results", show_header=True, header_style=self.config.accent_color)
        table.add_column("Test", style=self.config.primary_color, width=25)
        table.add_column("Tool", style=self.config.info_color, width=15)
        table.add_column("Status", style=self.config.success_color, width=10)
        table.add_column("Details", style=self.config.muted_color)
        
        for result in results:
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            status_style = self.config.success_color if result.get('passed', False) else self.config.error_color
            
            details = result.get('output', '')[:50] + "..." if len(result.get('output', '')) > 50 else result.get('output', '')
            
            table.add_row(
                result.get('test_name', 'Unknown'),
                result.get('tool_name', 'Unknown'),
                status,
                details
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_memory_context(self, memory_stats: Dict[str, Any]) -> None:
        """Show memory context and statistics."""
        stats_panel = Panel(
            Markdown(f"""
# 🧠 Memory Statistics

- **Total Tools**: {memory_stats.get('total_tools', 0)}
- **Successful Installations**: {memory_stats.get('successful_installations', 0)}
- **Failed Installations**: {memory_stats.get('failed_installations', 0)}
- **Success Rate**: {memory_stats.get('success_rate', 0):.1%}
- **Total Sessions**: {memory_stats.get('total_sessions', 0)}
- **Chat Entries**: {memory_stats.get('total_chat_entries', 0)}
- **Semantic Entries**: {memory_stats.get('semantic_entries', 0)}
            """),
            title="Memory Context",
            border_style=self.config.info_color,
            box=box.ROUNDED
        )
        
        self.console.print(stats_panel)
        self.console.print()
    
    def show_login_portal_prompt(self, portal_name: str, url: str, description: str) -> None:
        """Show login portal prompt."""
        portal_text = Text()
        portal_text.append(f"🌐 {portal_name}", style=f"bold {self.config.accent_color}")
        portal_text.append(f"\n📝 {description}", style=self.config.muted_color)
        portal_text.append(f"\n🔗 URL: {url}", style=self.config.info_color)
        
        portal_panel = Panel(
            portal_text,
            title="Login Portal",
            border_style=self.config.accent_color,
            box=box.ROUNDED
        )
        
        self.console.print(portal_panel)
        self.console.print()
    
    def show_completion_summary(self, summary: Dict[str, Any]) -> None:
        """Show completion summary."""
        summary_text = Text()
        summary_text.append("🎉 Installation Complete!", style=f"bold {self.config.success_color}")
        summary_text.append(f"\n\n📊 Summary:", style=self.config.accent_color)
        summary_text.append(f"\n- Environment: {summary.get('environment', 'Unknown')}", style=self.config.muted_color)
        summary_text.append(f"\n- Tools Installed: {summary.get('tools_installed', 0)}", style=self.config.success_color)
        summary_text.append(f"\n- Tools Failed: {summary.get('tools_failed', 0)}", style=self.config.error_color)
        summary_text.append(f"\n- Validation Passed: {summary.get('validation_passed', 0)}", style=self.config.success_color)
        summary_text.append(f"\n- Validation Failed: {summary.get('validation_failed', 0)}", style=self.config.error_color)
        
        summary_panel = Panel(
            summary_text,
            title="Installation Summary",
            border_style=self.config.success_color,
            box=box.ROUNDED
        )
        
        self.console.print(summary_panel)
        self.console.print()
    
    def show_chat_interface(self, welcome_message: str = "Chat with CONFIGO") -> None:
        """Show chat interface."""
        chat_panel = Panel(
            Markdown(f"""
# 💬 {welcome_message}

Type your message below. Use 'exit', 'quit', or 'bye' to end the chat.
            """),
            border_style=self.config.accent_color,
            box=box.ROUNDED
        )
        
        self.console.print(chat_panel)
        self.console.print()
    
    def show_chat_response(self, response: str, is_ai: bool = True) -> None:
        """Show chat response."""
        if is_ai:
            response_panel = Panel(
                Markdown(response),
                title="🤖 CONFIGO",
                border_style=self.config.info_color,
                box=box.ROUNDED
            )
        else:
            response_panel = Panel(
                response,
                title="👤 You",
                border_style=self.config.primary_color,
                box=box.ROUNDED
            )
        
        self.console.print(response_panel)
        self.console.print()
    
    def show_loading_spinner(self, message: str) -> Progress:
        """Show loading spinner."""
        progress = Progress(
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        
        progress.add_task(message, total=None)
        
        return progress
    
    def show_separator(self, title: Optional[str] = None) -> None:
        """Show a separator line."""
        if title:
            self.console.print(Rule(title, style=self.config.muted_color))
        else:
            self.console.print(Rule(style=self.config.muted_color))
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        self.console.clear()
    
    def print_separator(self) -> None:
        """Print a simple separator."""
        self.console.print("─" * 80, style=self.config.muted_color)
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input."""
        return Prompt.ask(prompt, console=self.console)
    
    def confirm_action(self, message: str) -> bool:
        """Confirm an action with the user."""
        return Confirm.ask(message, console=self.console)
    
    def show_command_output(self, command: str, output: str, success: bool = True) -> None:
        """Show command output."""
        status_icon = "✅" if success else "❌"
        status_style = self.config.success_color if success else self.config.error_color
        
        output_text = Text()
        output_text.append(f"{status_icon} Command: ", style=status_style)
        output_text.append(command, style=self.config.primary_color)
        
        if output:
            output_text.append(f"\n📄 Output:\n{output}", style=self.config.muted_color)
        
        output_panel = Panel(
            output_text,
            border_style=status_style,
            box=box.ROUNDED
        )
        
        self.console.print(output_panel)
        self.console.print()
    
    def show_lite_mode_notice(self) -> None:
        """Show lite mode notice."""
        notice_panel = Panel(
            Markdown("""
# ⚡ Lite Mode Enabled

Running in lite mode for faster installation.
Only essential tools will be installed.
            """),
            border_style=self.config.warning_color,
            box=box.ROUNDED
        )
        
        self.console.print(notice_panel)
        self.console.print() 