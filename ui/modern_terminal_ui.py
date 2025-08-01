"""
CONFIGO Modern Terminal UI
==========================

🚀 A stunning, modern terminal interface for CONFIGO that feels like
an intelligent assistant rather than a traditional CLI.

Features:
- 🎨 Beautiful rounded panels, shadows, and gradients
- ⚡ Smooth animations and transitions
- 🎯 Context-aware layouts and responsive design
- 🧠 AI-powered interface with intelligent feedback
- 📊 Live progress tracking and real-time updates
- 🌈 Strategic color usage and visual hierarchy
- 🎪 Professional polish with welcome animations
- 🔧 Multiple themes and customization options
"""

import logging
import time
import asyncio
import os
import sys
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.live import Live
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.tree import Tree
from rich.layout import Layout
from rich import box
from rich.emoji import Emoji
from rich.console import Group as RichGroup
from rich.live import Live
from rich.spinner import Spinner
from rich.console import Console
from rich.padding import Padding
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.columns import Columns
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.tree import Tree
from rich.layout import Layout
from rich import box
from rich.emoji import Emoji
from rich.console import Group as RichGroup
from rich.live import Live
from rich.spinner import Spinner
from rich.console import Console
from rich.padding import Padding
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.columns import Columns
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.tree import Tree
from rich.layout import Layout
from rich import box
from rich.emoji import Emoji
from rich.console import Group as RichGroup
from rich.live import Live
from rich.spinner import Spinner
from rich.console import Console
from rich.padding import Padding

logger = logging.getLogger(__name__)

class Theme(Enum):
    """Available UI themes."""
    DEFAULT = "default"
    MINIMAL = "minimal"
    DEVELOPER = "developer"
    VERBOSE = "verbose"
    DARK = "dark"
    LIGHT = "light"

class UIConfig:
    """Modern UI Configuration for CONFIGO."""
    
    def __init__(self, theme: Theme = Theme.DEFAULT):
        self.theme = theme
        self._setup_theme()
    
    def _setup_theme(self):
        """Setup color scheme based on theme."""
        if self.theme == Theme.DEFAULT:
            self.colors = {
                "primary": "cyan",
                "success": "green",
                "warning": "yellow", 
                "error": "red",
                "info": "blue",
                "muted": "dim white",
                "accent": "magenta",
                "background": "black",
                "panel_border": "cyan",
                "text": "white",
                "highlight": "bright_white"
            }
        elif self.theme == Theme.MINIMAL:
            self.colors = {
                "primary": "white",
                "success": "green",
                "warning": "yellow",
                "error": "red", 
                "info": "blue",
                "muted": "dim white",
                "accent": "white",
                "background": "black",
                "panel_border": "white",
                "text": "white",
                "highlight": "bright_white"
            }
        elif self.theme == Theme.DEVELOPER:
            self.colors = {
                "primary": "bright_blue",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "cyan",
                "muted": "dim white",
                "accent": "magenta",
                "background": "black",
                "panel_border": "bright_blue",
                "text": "white",
                "highlight": "bright_white"
            }
        elif self.theme == Theme.VERBOSE:
            self.colors = {
                "primary": "bright_green",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "cyan",
                "muted": "dim white",
                "accent": "magenta",
                "background": "black",
                "panel_border": "bright_green",
                "text": "white",
                "highlight": "bright_white"
            }
        elif self.theme == Theme.DARK:
            self.colors = {
                "primary": "bright_cyan",
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "info": "bright_blue",
                "muted": "dim white",
                "accent": "bright_magenta",
                "background": "black",
                "panel_border": "bright_cyan",
                "text": "white",
                "highlight": "bright_white"
            }
        elif self.theme == Theme.LIGHT:
            self.colors = {
                "primary": "blue",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "cyan",
                "muted": "black",
                "accent": "magenta",
                "background": "white",
                "panel_border": "blue",
                "text": "black",
                "highlight": "bright_black"
            }
        
        # Animation settings
        self.animation_speed = 0.1
        self.spinner_style = self.colors["primary"]
        self.use_animations = True
        self.use_emoji = True
        
        # Layout settings
        self.header_size = 3
        self.footer_size = 2
        self.panel_padding = (1, 2)
        self.rounded_corners = True
        self.show_shadows = True

class ModernTerminalUI:
    """
    Modern Terminal UI for CONFIGO with stunning visuals and responsive design.
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
        self._current_progress = None
        
        # Session state
        self.session_start_time = datetime.now()
        self.current_mode = None
        self.user_profile = None
        
        logger.info("Modern Terminal UI initialized")
    
    def _setup_layout(self) -> None:
        """Setup the main layout structure."""
        self.layout.split_column(
            Layout(name="header", size=self.config.header_size),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=self.config.footer_size)
        )
    
    def show_welcome_animation(self) -> None:
        """Display a stunning welcome animation."""
        welcome_text = Text()
        welcome_text.append("🚀 ", style=f"bold {self.config.colors['primary']}")
        welcome_text.append("CONFIGO", style=f"bold {self.config.colors['primary']}")
        welcome_text.append(" is loading...", style=self.config.colors['muted'])
        
        with Live(
            Panel(
                Align.center(welcome_text),
                border_style=self.config.colors['panel_border'],
                box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
                padding=self.config.panel_padding
            ),
            console=self.console,
            refresh_per_second=10
        ) as live:
            for i in range(20):
                time.sleep(0.1)
                spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[i % 10]
                welcome_text = Text()
                welcome_text.append(f"{spinner} ", style=f"bold {self.config.colors['primary']}")
                welcome_text.append("CONFIGO", style=f"bold {self.config.colors['primary']}")
                welcome_text.append(" is loading...", style=self.config.colors['muted'])
                live.update(
                    Panel(
                        Align.center(welcome_text),
                        border_style=self.config.colors['panel_border'],
                        box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
                        padding=self.config.panel_padding
                    )
                )
    
    def show_banner(self) -> None:
        """Display the modern CONFIGO banner."""
        # ASCII art banner
        banner_art = """
╔══════════════════════════════════════════════════════════════╗
║  🚀 CONFIGO - Intelligent Development Environment Agent 🚀  ║
║                                                              ║
║  🧠 Memory • 📋 Planning • 🔧 Self-Healing • ✅ Validation  ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        banner_panel = Panel(
            Align.center(banner_art),
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding,
            title="[bold]Welcome to CONFIGO[/bold]",
            title_align="center"
        )
        
        self.console.print(banner_panel)
        self.console.print()
    
    def show_mode_header(self, mode: str, description: str) -> None:
        """Display mode-specific header."""
        mode_text = Text()
        mode_text.append(f"🎯 {mode.upper()} MODE", style=f"bold {self.config.colors['primary']}")
        mode_text.append(f" - {description}", style=self.config.colors['muted'])
        
        header_panel = Panel(
            Align.center(mode_text),
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=(0, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
        
        self.current_mode = mode
    
    def show_system_info(self, system_info: Dict[str, Any]) -> None:
        """Display system information in a beautiful table."""
        table = Table(
            title="🖥️ System Information",
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            border_style=self.config.colors['panel_border'],
            title_style=f"bold {self.config.colors['info']}"
        )
        
        table.add_column("Property", style="bold")
        table.add_column("Value", style=self.config.colors['primary'])
        table.add_column("Status", style="bold")
        
        # Add system info rows
        table.add_row("OS", f"{system_info.get('os_name', 'Unknown')} {system_info.get('os_version', '')}", "🖥️")
        table.add_row("Architecture", system_info.get('arch', 'Unknown'), "⚙️")
        table.add_row("RAM", f"{system_info.get('ram_gb', 0)} GB", "💾")
        table.add_row("CPU Cores", str(system_info.get('cpu_cores', 0)), "🔧")
        table.add_row("GPU", system_info.get('gpu', 'None'), "🎮")
        table.add_row("Package Managers", ", ".join(system_info.get('package_managers', [])), "📦")
        
        info_panel = Panel(
            table,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(info_panel)
        self.console.print()
    
    def show_memory_stats(self, memory_stats: Dict[str, Any]) -> None:
        """Display memory statistics."""
        table = Table(
            title="🧠 Memory Statistics",
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            border_style=self.config.colors['panel_border'],
            title_style=f"bold {self.config.colors['info']}"
        )
        
        table.add_column("Metric", style="bold")
        table.add_column("Value", style=self.config.colors['primary'])
        table.add_column("Status", style="bold")
        
        # Add memory stats
        table.add_row("Total Tools", str(memory_stats.get('total_tools', 0)), "📦")
        table.add_row("Successful Installations", str(memory_stats.get('successful_installations', 0)), "✅")
        table.add_row("Failed Installations", str(memory_stats.get('failed_installations', 0)), "❌")
        table.add_row("Success Rate", f"{memory_stats.get('success_rate', 0):.1f}%", "📈")
        table.add_row("Total Sessions", str(memory_stats.get('total_sessions', 0)), "🕒")
        table.add_row("Memory Type", memory_stats.get('memory_type', 'Local'), "🧠")
        
        stats_panel = Panel(
            table,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(stats_panel)
        self.console.print()
    
    def show_ai_reasoning(self, title: str, content: str, confidence: float = 1.0) -> None:
        """Display AI reasoning with confidence score."""
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        confidence_text = f"Confidence: {confidence:.1%} [{confidence_bar}]"
        
        reasoning_text = Text()
        reasoning_text.append(f"🤖 {title}\n\n", style=f"bold {self.config.colors['accent']}")
        reasoning_text.append(content, style=self.config.colors['text'])
        reasoning_text.append(f"\n\n{confidence_text}", style=self.config.colors['muted'])
        
        reasoning_panel = Panel(
            reasoning_text,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding,
            title="🧠 AI Analysis",
            title_align="left"
        )
        
        self.console.print(reasoning_panel)
        self.console.print()
    
    def show_installation_progress(self, tool_name: str, total_steps: int = 100) -> Tuple[Progress, int]:
        """Show installation progress with live updates."""
        progress = Progress(
            SpinnerColumn(style=self.config.colors['primary']),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=self.config.colors['success'], finished_style=self.config.colors['success']),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        
        task_id = progress.add_task(f"Installing {tool_name}...", total=total_steps)
        
        self._current_progress = progress
        return progress, task_id
    
    def show_planning_steps(self, steps: List[Dict[str, Any]]) -> None:
        """Display planning steps in a tree structure."""
        tree = Tree("📋 Installation Plan", style=self.config.colors['primary'])
        
        for i, step in enumerate(steps, 1):
            step_node = tree.add(f"Step {i}: {step['name']}", style=self.config.colors['text'])
            if step.get('description'):
                step_node.add(step['description'], style=self.config.colors['muted'])
            if step.get('sub_steps'):
                for sub_step in step['sub_steps']:
                    step_node.add(f"• {sub_step}", style=self.config.colors['muted'])
        
        plan_panel = Panel(
            tree,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding,
            title="📋 Installation Plan",
            title_align="left"
        )
        
        self.console.print(plan_panel)
        self.console.print()
    
    def show_success_message(self, message: str, details: Optional[str] = None) -> None:
        """Display success message with optional details."""
        success_text = Text()
        success_text.append("✅ ", style=f"bold {self.config.colors['success']}")
        success_text.append(message, style=f"bold {self.config.colors['success']}")
        
        if details:
            success_text.append(f"\n{details}", style=self.config.colors['muted'])
        
        success_panel = Panel(
            success_text,
            border_style=self.config.colors['success'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(success_panel)
        self.console.print()
    
    def show_error_message(self, error: str, suggestion: str = "", retry_info: str = "") -> None:
        """Display error message with suggestions and retry info."""
        error_text = Text()
        error_text.append("❌ ", style=f"bold {self.config.colors['error']}")
        error_text.append(error, style=f"bold {self.config.colors['error']}")
        
        if suggestion:
            error_text.append(f"\n💡 {suggestion}", style=self.config.colors['warning'])
        
        if retry_info:
            error_text.append(f"\n🔄 {retry_info}", style=self.config.colors['info'])
        
        error_panel = Panel(
            error_text,
            border_style=self.config.colors['error'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(error_panel)
        self.console.print()
    
    def show_info_message(self, message: str, icon: str = "ℹ️") -> None:
        """Display info message."""
        info_text = Text()
        info_text.append(f"{icon} ", style=f"bold {self.config.colors['info']}")
        info_text.append(message, style=self.config.colors['info'])
        
        info_panel = Panel(
            info_text,
            border_style=self.config.colors['info'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(info_panel)
        self.console.print()
    
    def show_validation_results(self, results: List[Dict[str, Any]]) -> None:
        """Display validation results."""
        table = Table(
            title="✅ Validation Results",
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            border_style=self.config.colors['panel_border'],
            title_style=f"bold {self.config.colors['success']}"
        )
        
        table.add_column("Tool", style="bold")
        table.add_column("Status", style="bold")
        table.add_column("Version", style=self.config.colors['primary'])
        table.add_column("Details", style=self.config.colors['muted'])
        
        for result in results:
            status_icon = "✅" if result.get('success', False) else "❌"
            status_color = self.config.colors['success'] if result.get('success', False) else self.config.colors['error']
            
            table.add_row(
                result.get('name', 'Unknown'),
                f"{status_icon} {result.get('status', 'Unknown')}",
                result.get('version', 'N/A'),
                result.get('details', '')
            )
        
        validation_panel = Panel(
            table,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(validation_panel)
        self.console.print()
    
    def show_chat_interface(self, welcome_message: str = "Chat with CONFIGO") -> None:
        """Display chat interface."""
        chat_text = Text()
        chat_text.append("💬 ", style=f"bold {self.config.colors['primary']}")
        chat_text.append(welcome_message, style=self.config.colors['text'])
        chat_text.append("\n\nType your message below, or type 'exit' to quit.", style=self.config.colors['muted'])
        
        chat_panel = Panel(
            chat_text,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding,
            title="💬 CONFIGO Chat",
            title_align="left"
        )
        
        self.console.print(chat_panel)
        self.console.print()
    
    def show_chat_response(self, response: str, is_ai: bool = True) -> None:
        """Display chat response."""
        response_text = Text()
        if is_ai:
            response_text.append("🤖 CONFIGO: ", style=f"bold {self.config.colors['primary']}")
        else:
            response_text.append("👤 You: ", style=f"bold {self.config.colors['accent']}")
        
        response_text.append(response, style=self.config.colors['text'])
        
        response_panel = Panel(
            response_text,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(response_panel)
        self.console.print()
    
    def show_loading_spinner(self, message: str) -> Progress:
        """Show loading spinner."""
        progress = Progress(
            SpinnerColumn(style=self.config.colors['primary']),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        
        progress.add_task(message, total=None)
        return progress
    
    def show_separator(self, title: Optional[str] = None) -> None:
        """Show a separator with optional title."""
        if title:
            rule = Rule(title, style=self.config.colors['panel_border'])
        else:
            rule = Rule(style=self.config.colors['panel_border'])
        
        self.console.print(rule)
        self.console.print()
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        self.console.clear()
    
    def print_separator(self) -> None:
        """Print a simple separator."""
        self.console.print()
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input with styled prompt."""
        return Prompt.ask(f"[{self.config.colors['primary']}]{prompt}")
    
    def confirm_action(self, message: str) -> bool:
        """Confirm action with styled prompt."""
        return Confirm.ask(f"[{self.config.colors['warning']}]{message}")
    
    def show_command_output(self, command: str, output: str, success: bool = True) -> None:
        """Display command output."""
        status_icon = "✅" if success else "❌"
        status_color = self.config.colors['success'] if success else self.config.colors['error']
        
        output_text = Text()
        output_text.append(f"{status_icon} ", style=f"bold {status_color}")
        output_text.append(f"Command: {command}\n", style="bold")
        output_text.append(output, style=self.config.colors['text'])
        
        output_panel = Panel(
            output_text,
            border_style=status_color,
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding,
            title="Terminal Output",
            title_align="left"
        )
        
        self.console.print(output_panel)
        self.console.print()
    
    def show_lite_mode_notice(self) -> None:
        """Show lite mode notice."""
        notice_text = Text()
        notice_text.append("📱 ", style=f"bold {self.config.colors['info']}")
        notice_text.append("Lite mode enabled - minimal output for low-speed terminals", style=self.config.colors['info'])
        
        notice_panel = Panel(
            notice_text,
            border_style=self.config.colors['info'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=self.config.panel_padding
        )
        
        self.console.print(notice_panel)
        self.console.print()
    
    def show_dynamic_status_bar(self, stats: Dict[str, Any]) -> None:
        """Show dynamic status bar with memory/success stats."""
        status_text = Text()
        status_text.append("📊 ", style=f"bold {self.config.colors['info']}")
        status_text.append(f"Session: {stats.get('session_duration', '0s')} | ", style=self.config.colors['muted'])
        status_text.append(f"Success Rate: {stats.get('success_rate', 0):.1f}% | ", style=self.config.colors['success'])
        status_text.append(f"Memory: {stats.get('memory_usage', '0MB')}", style=self.config.colors['info'])
        
        status_panel = Panel(
            status_text,
            border_style=self.config.colors['panel_border'],
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            padding=(0, 1)
        )
        
        self.console.print(status_panel)
    
    def show_theme_selector(self) -> Theme:
        """Show theme selector."""
        themes = [
            ("Default", Theme.DEFAULT, "Modern cyan theme with animations"),
            ("Minimal", Theme.MINIMAL, "Clean white theme for low-resource terminals"),
            ("Developer", Theme.DEVELOPER, "Bright blue theme for development focus"),
            ("Verbose", Theme.VERBOSE, "Green theme with detailed output"),
            ("Dark", Theme.DARK, "High contrast dark theme"),
            ("Light", Theme.LIGHT, "Light theme for bright environments")
        ]
        
        table = Table(
            title="🎨 Select Theme",
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            border_style=self.config.colors['panel_border'],
            title_style=f"bold {self.config.colors['info']}"
        )
        
        table.add_column("Theme", style="bold")
        table.add_column("Description", style=self.config.colors['text'])
        table.add_column("Key", style=self.config.colors['primary'])
        
        for i, (name, theme, desc) in enumerate(themes, 1):
            table.add_row(name, desc, str(i))
        
        self.console.print(table)
        self.console.print()
        
        choice = IntPrompt.ask(
            f"[{self.config.colors['primary']}]Select theme (1-{len(themes)})",
            default=1
        )
        
        return themes[choice - 1][1]
    
    def show_welcome_screen(self) -> None:
        """Show comprehensive welcome screen."""
        self.clear_screen()
        
        # Welcome animation
        self.show_welcome_animation()
        
        # Main banner
        self.show_banner()
        
        # Mode selection
        modes = [
            ("🚀 Full Setup", "Complete development environment setup"),
            ("💬 Chat Mode", "Interactive AI chat assistant"),
            ("🔍 Scan Mode", "Project analysis and recommendations"),
            ("🌐 Portal Mode", "Login portal orchestration"),
            ("📦 Install Mode", "Natural language app installation"),
            ("🎨 Theme Selector", "Customize UI appearance")
        ]
        
        table = Table(
            title="🎯 Select Mode",
            box=box.ROUNDED if self.config.rounded_corners else box.SIMPLE,
            border_style=self.config.colors['panel_border'],
            title_style=f"bold {self.config.colors['info']}"
        )
        
        table.add_column("Mode", style="bold")
        table.add_column("Description", style=self.config.colors['text'])
        table.add_column("Key", style=self.config.colors['primary'])
        
        for i, (name, desc) in enumerate(modes, 1):
            table.add_row(name, desc, str(i))
        
        self.console.print(table)
        self.console.print()
        
        choice = IntPrompt.ask(
            f"[{self.config.colors['primary']}]Select mode (1-{len(modes)})",
            default=1
        )
        
        return choice 