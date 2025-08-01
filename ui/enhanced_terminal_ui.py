"""
CONFIGO Enhanced Terminal UI
===========================

🚀 Modern, Unique, Stylish, Animated Terminal Interface

Features:
- 🎨 Rich terminal UI with colors and formatting
- 📊 Live progress indicators and animations
- 🧠 AI reasoning displays with syntax highlighting
- ✅ Readable block sections with proper spacing
- 🌈 Consistent color theme (cool branding)
- ⚡ Fast and clean output (no lag or clutter)
- 🎯 Professional developer-focused interface
"""

import logging
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass

from rich.console import Console, Group, RenderableType
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
from rich.console import Group as RichGroup

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
        banner_text.append(" - ", style=self.config.muted_color)
        banner_text.append("Intelligent Development Environment Agent", style=self.config.muted_color)
        
        # Add subtitle
        subtitle = Text()
        subtitle.append("🧠 AI-Powered • ", style=self.config.info_color)
        subtitle.append("🔧 Self-Healing • ", style=self.config.success_color)
        subtitle.append("✅ Validation • ", style=self.config.warning_color)
        subtitle.append("🌐 Portal Integration", style=self.config.primary_color)
        
        panel = Panel(
            Align.center(Group(banner_text, subtitle)),
            border_style=self.config.accent_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title="[bold]Autonomous AI Setup Agent[/bold]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_ai_reasoning(self, title: str, content: str, confidence: float = 1.0) -> None:
        """Display AI reasoning with syntax highlighting and confidence."""
        # Create reasoning panel
        reasoning_text = Text()
        reasoning_text.append(f"🧠 {title}\n\n", style=f"bold {self.config.info_color}")
        reasoning_text.append(content, style="white")
        
        # Add confidence indicator
        if confidence < 1.0:
            confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
            reasoning_text.append(f"\n\n", style=self.config.muted_color)
            reasoning_text.append("Confidence: ", style=f"bold {self.config.muted_color}")
            reasoning_text.append(f"{confidence:.1%}\n", style=self.config.muted_color)
            reasoning_text.append(confidence_bar, style=self.config.success_color)
        
        panel = Panel(
            reasoning_text,
            border_style=self.config.info_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.info_color}]AI Reasoning[/bold {self.config.info_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_tool_detection_table(self, tools: List[Dict[str, Any]]) -> None:
        """Display tool detection results in a modern table."""
        if not tools:
            return
        
        table = Table(
            title="🔍 Tool Detection Results",
            box=box.ROUNDED,
            border_style=self.config.info_color,
            title_style=f"bold {self.config.info_color}"
        )
        
        table.add_column("Tool", style=f"bold {self.config.primary_color}", no_wrap=True)
        table.add_column("Status", style="bold", justify="center")
        table.add_column("Version", style=self.config.muted_color)
        table.add_column("Path", style=self.config.muted_color)
        
        for tool in tools:
            # Status emoji and color
            if tool.get('installed', False):
                status_emoji = "✅"
                status_color = self.config.success_color
                status_text = "Installed"
            else:
                status_emoji = "❌"
                status_color = self.config.error_color
                status_text = "Not Found"
            
            table.add_row(
                f"🔧 {tool['name']}",
                f"[{status_color}]{status_emoji} {status_text}[/{status_color}]",
                tool.get('version', 'N/A'),
                tool.get('path', 'N/A')
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_installation_progress(self, tool_name: str, total_steps: int = 100) -> Tuple[Progress, int]:
        """Show animated installation progress for a tool."""
        progress = Progress(
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=self.config.success_color, finished_style=self.config.success_color),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            expand=True
        )
        
        task_id = progress.add_task(f"Installing {tool_name}...", total=total_steps)
        return progress, task_id
    
    def show_llm_api_call(self, description: str = "Calling AI API...") -> Progress:
        """Show animated LLM API call progress."""
        progress = Progress(
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=self.config.info_color, finished_style=self.config.info_color),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            expand=True
        )
        
        progress.add_task(description, total=100)
        return progress
    
    def show_planning_steps(self, steps: List[Dict[str, Any]]) -> None:
        """Display planning steps in a modern tree structure."""
        if not steps:
            return
        
        tree = Tree(f"[bold {self.config.accent_color}]📋 Installation Plan[/bold {self.config.accent_color}]")
        
        for i, step in enumerate(steps, 1):
            step_text = f"[bold]{step['name']}[/bold]"
            if step.get('description'):
                step_text += f"\n[dim]{step['description']}[/dim]"
            
            step_node = tree.add(step_text)
            
            # Add sub-steps if available
            if step.get('sub_steps'):
                for sub_step in step['sub_steps']:
                    sub_text = f"[cyan]• {sub_step}[/cyan]"
                    step_node.add(sub_text)
        
        panel = Panel(
            tree,
            border_style=self.config.accent_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.accent_color}]Planning Complete[/bold {self.config.accent_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_success_message(self, message: str, details: Optional[str] = None) -> None:
        """Display a success message with modern styling."""
        success_text = Text()
        success_text.append("✅ ", style=f"bold {self.config.success_color}")
        success_text.append(message, style=f"bold {self.config.success_color}")
        
        if details:
            success_text.append(f"\n\n{details}", style=self.config.muted_color)
        
        panel = Panel(
            success_text,
            border_style=self.config.success_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.success_color}]Success[/bold {self.config.success_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_error_message(self, error: str, suggestion: str = "", retry_info: str = "") -> None:
        """Display an error message with clear guidance."""
        error_text = Text()
        error_text.append("❌ ", style=f"bold {self.config.error_color}")
        error_text.append("Error", style=f"bold {self.config.error_color}")
        error_text.append(f": {error}", style=self.config.error_color)
        
        if suggestion:
            error_text.append(f"\n\n💡 ", style=self.config.warning_color)
            error_text.append("Suggestion: ", style=f"bold {self.config.warning_color}")
            error_text.append(f"{suggestion}", style=self.config.warning_color)
        
        if retry_info:
            error_text.append(f"\n\n🔄 ", style=self.config.info_color)
            error_text.append("Retry: ", style=f"bold {self.config.info_color}")
            error_text.append(f"{retry_info}", style=self.config.info_color)
        
        panel = Panel(
            error_text,
            border_style=self.config.error_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.error_color}]Error[/bold {self.config.error_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_info_message(self, message: str, icon: str = "ℹ️") -> None:
        """Display an info message."""
        info_text = Text()
        info_text.append(f"{icon} ", style=f"bold {self.config.info_color}")
        info_text.append(message, style=self.config.info_color)
        
        panel = Panel(
            info_text,
            border_style=self.config.info_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.info_color}]Information[/bold {self.config.info_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_validation_results(self, results: List[Dict[str, Any]]) -> None:
        """Display validation results in a modern table."""
        if not results:
            return
        
        table = Table(
            title="✅ Validation Results",
            box=box.ROUNDED,
            border_style=self.config.success_color,
            title_style=f"bold {self.config.success_color}"
        )
        
        table.add_column("Tool", style=f"bold {self.config.primary_color}")
        table.add_column("Status", style="bold", justify="center")
        table.add_column("Version", style=self.config.muted_color)
        table.add_column("Details", style="white")
        
        for result in results:
            if result.get('valid', False):
                status_emoji = "✅"
                status_color = self.config.success_color
                status_text = "Valid"
            else:
                status_emoji = "❌"
                status_color = self.config.error_color
                status_text = "Invalid"
            
            table.add_row(
                f"🔧 {result['name']}",
                f"[{status_color}]{status_emoji} {status_text}[/{status_color}]",
                result.get('version', 'N/A'),
                result.get('details', '')
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_memory_context(self, memory_stats: Dict[str, Any]) -> None:
        """Display memory context in a modern format."""
        memory_text = Text()
        memory_text.append("🧠 ", style=f"bold {self.config.info_color}")
        memory_text.append("Memory Context", style=f"bold {self.config.info_color}")
        memory_text.append("\n\n", style=self.config.info_color)
        
        # Add memory statistics
        memory_text.append(f"📦 Total Tools: {memory_stats.get('total_tools', 0)}\n", style=self.config.primary_color)
        memory_text.append(f"✅ Successful: {memory_stats.get('successful_installations', 0)}\n", style=self.config.success_color)
        memory_text.append(f"❌ Failed: {memory_stats.get('failed_installations', 0)}\n", style=self.config.error_color)
        memory_text.append(f"📈 Success Rate: {memory_stats.get('success_rate', 0):.1f}%\n", style=self.config.warning_color)
        
        if memory_stats.get('recent_tools'):
            memory_text.append(f"\n🕒 ", style=self.config.muted_color)
            memory_text.append("Recent Tools:", style=f"bold {self.config.muted_color}")
            memory_text.append("\n", style=self.config.muted_color)
            for tool in memory_stats['recent_tools'][:5]:
                memory_text.append(f"  • {tool}\n", style=self.config.muted_color)
        
        panel = Panel(
            memory_text,
            border_style=self.config.info_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.info_color}]Memory Context[/bold {self.config.info_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_login_portal_prompt(self, portal_name: str, url: str, description: str) -> None:
        """Display login portal prompt with modern styling."""
        portal_text = Text()
        portal_text.append("🌐 ", style=f"bold {self.config.primary_color}")
        portal_text.append(f"{portal_name}", style=f"bold {self.config.primary_color}")
        portal_text.append("\n\n", style=self.config.primary_color)
        portal_text.append(f"📝 {description}\n\n", style="white")
        portal_text.append(f"🔗 URL: {url}\n\n", style=self.config.info_color)
        portal_text.append("💡 ", style=self.config.warning_color)
        portal_text.append("Tip: ", style=f"bold {self.config.warning_color}")
        portal_text.append("The browser will open automatically. Complete the login and return here.", style=self.config.warning_color)
        
        panel = Panel(
            portal_text,
            border_style=self.config.primary_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.primary_color}]Login Portal[/bold {self.config.primary_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_completion_summary(self, summary: Dict[str, Any]) -> None:
        """Display completion summary with modern styling."""
        summary_text = Text()
        summary_text.append("🎉 ", style=f"bold {self.config.success_color}")
        summary_text.append("Setup Complete!", style=f"bold {self.config.success_color}")
        summary_text.append("\n\n", style=self.config.success_color)
        
        # Add summary statistics
        summary_text.append(f"🔧 Tools Installed: {summary.get('tools_installed', 0)}\n", style=self.config.primary_color)
        summary_text.append(f"✅ Validations Passed: {summary.get('validations_passed', 0)}\n", style=self.config.success_color)
        summary_text.append(f"🌐 Portals Opened: {summary.get('portals_opened', 0)}\n", style=self.config.info_color)
        summary_text.append(f"⏱️ Total Time: {summary.get('total_time', 'N/A')}\n", style=self.config.muted_color)
        
        if summary.get('suggestions'):
            summary_text.append(f"\n💡 ", style=self.config.warning_color)
            summary_text.append("Suggestions:", style=f"bold {self.config.warning_color}")
            summary_text.append("\n", style=self.config.warning_color)
            for suggestion in summary['suggestions']:
                summary_text.append(f"  • {suggestion}\n", style=self.config.muted_color)
        
        panel = Panel(
            summary_text,
            border_style=self.config.success_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.success_color}]Setup Complete[/bold {self.config.success_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_chat_interface(self, welcome_message: str = "Chat with CONFIGO") -> None:
        """Display chat interface header."""
        chat_text = Text()
        chat_text.append("💬 ", style=f"bold {self.config.primary_color}")
        chat_text.append(welcome_message, style=f"bold {self.config.primary_color}")
        chat_text.append("\n\nType your questions or commands. Type 'quit' to exit.", style=self.config.muted_color)
        
        panel = Panel(
            chat_text,
            border_style=self.config.primary_color,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {self.config.primary_color}]Chat Mode[/bold {self.config.primary_color}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_chat_response(self, response: str, is_ai: bool = True) -> None:
        """Display chat response with modern styling."""
        if is_ai:
            response_text = Text()
            response_text.append("🤖 CONFIGO: ", style=f"bold {self.config.accent_color}")
            response_text.append(response, style="white")
            
            panel = Panel(
                response_text,
                border_style=self.config.accent_color,
                box=box.ROUNDED,
                padding=self.config.panel_padding
            )
        else:
            response_text = Text()
            response_text.append("👤 You: ", style=f"bold {self.config.primary_color}")
            response_text.append(response, style="white")
            
            panel = Panel(
                response_text,
                border_style=self.config.primary_color,
                box=box.ROUNDED,
                padding=self.config.panel_padding
            )
        
        self.console.print(panel)
        self.console.print()
    
    def show_loading_spinner(self, message: str) -> Progress:
        """Show a loading spinner with message."""
        progress = Progress(
            SpinnerColumn(style=self.config.spinner_style),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            expand=True
        )
        
        progress.add_task(message, total=None)
        return progress
    
    def show_separator(self, title: Optional[str] = None) -> None:
        """Display a styled separator."""
        if title:
            rule = Rule(f"[bold {self.config.accent_color}]{title}[/bold {self.config.accent_color}]", style=self.config.accent_color)
        else:
            rule = Rule(style=self.config.muted_color)
        
        self.console.print(rule)
        self.console.print()
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        self.console.clear()
    
    def print_separator(self) -> None:
        """Print a simple separator line."""
        self.console.print(Rule(style=self.config.muted_color))
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input with styled prompt."""
        return Prompt.ask(f"[bold {self.config.primary_color}]{prompt}[/bold {self.config.primary_color}]")
    
    def confirm_action(self, message: str) -> bool:
        """Confirm an action with styled prompt."""
        return Confirm.ask(f"[bold {self.config.warning_color}]{message}[/bold {self.config.warning_color}]")
    
    def show_command_output(self, command: str, output: str, success: bool = True) -> None:
        """Display command output with syntax highlighting."""
        # Command header
        cmd_text = Text()
        cmd_text.append("💻 ", style=f"bold {self.config.primary_color}")
        cmd_text.append("Command: ", style=f"bold {self.config.primary_color}")
        cmd_text.append(command, style="white")
        
        # Output with syntax highlighting
        if success:
            output_style = self.config.success_color
            status_emoji = "✅"
        else:
            output_style = self.config.error_color
            status_emoji = "❌"
        
        output_text = Text()
        output_text.append(f"{status_emoji} ", style=f"bold {output_style}")
        output_text.append("Output:", style=f"bold {output_style}")
        output_text.append(f"\n{output}", style="white")
        
        panel = Panel(
            Group(cmd_text, output_text),
            border_style=output_style,
            box=box.ROUNDED,
            padding=self.config.panel_padding,
            title=f"[bold {output_style}]Command Execution[/bold {output_style}]"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_lite_mode_notice(self) -> None:
        """Show lite mode notice for minimal output."""
        notice_text = Text()
        notice_text.append("📱 ", style=f"bold {self.config.info_color}")
        notice_text.append("Lite Mode Active", style=f"bold {self.config.info_color}")
        notice_text.append(" - Minimal output for low-speed terminals", style=self.config.muted_color)
        
        panel = Panel(
            notice_text,
            border_style=self.config.info_color,
            box=box.ROUNDED,
            padding=(0, 1),
            title=f"[bold {self.config.info_color}]Lite Mode[/bold {self.config.info_color}]"
        )
        
        self.console.print(panel)
        self.console.print() 