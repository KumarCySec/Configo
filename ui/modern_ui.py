"""
CONFIGO Modern Terminal UI
==========================

Signature terminal UI/UX for CONFIGO using Rich.
Features:
- Clean, modern design with consistent spacing
- Borderless boxes and clean layouts
- Minimal emoji + visual cues
- Spinners, progress bars, summary tables
- Humanized error messages
- Responsive and beautiful interface
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.tree import Tree
from rich import box
from core.memory import AgentMemory
from core.project_scanner import ProjectAnalysis
from core.portal_orchestrator import PortalOrchestrator
from core.chat_agent import ChatResponse

logger = logging.getLogger(__name__)

class ModernUI:
    """
    Modern terminal UI for CONFIGO with Rich.
    """
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        
        # Color scheme
        self.colors = {
            "primary": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "blue",
            "muted": "dim white"
        }
        
        logger.info("Modern UI initialized")
    
    def show_banner(self) -> None:
        """Display the CONFIGO banner."""
        banner_text = Text()
        banner_text.append("🚀 ", style=f"bold {self.colors['primary']}")
        banner_text.append("CONFIGO", style=f"bold {self.colors['primary']}")
        banner_text.append(" - Intelligent Development Environment Agent", style=self.colors['muted'])
        
        panel = Panel(
            Align.center(banner_text),
            border_style=self.colors['primary'],
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_memory_stats(self, memory: AgentMemory) -> None:
        """Display memory statistics in a clean format."""
        stats = memory.get_memory_stats()
        
        # Create stats table
        table = Table(
            title="📊 Memory Statistics",
            box=box.ROUNDED,
            border_style=self.colors['info'],
            title_style=f"bold {self.colors['info']}"
        )
        
        table.add_column("Metric", style="bold")
        table.add_column("Value", style=self.colors['primary'])
        table.add_column("Status", style="bold")
        
        # Add rows
        table.add_row("Total Tools", str(stats['total_tools']), "📦")
        table.add_row("Successful Installations", str(stats['successful_installations']), "✅")
        table.add_row("Failed Installations", str(stats['failed_installations']), "❌")
        table.add_row("Success Rate", f"{stats['success_rate']:.1f}%", "📈")
        table.add_row("Total Sessions", str(stats['total_sessions']), "🕒")
        table.add_row("Total Profiles", str(stats['total_profiles']), "👤")
        table.add_row("Memory Type", stats['memory_type'], "🧠")
        
        self.console.print(table)
        self.console.print()
    
    def show_project_analysis(self, analysis: ProjectAnalysis) -> None:
        """Display project analysis results."""
        # Project overview panel
        overview_text = Text()
        overview_text.append(f"📁 Project Type: ", style="bold")
        overview_text.append(analysis.project_type.title(), style=self.colors['primary'])
        overview_text.append(f"\n🎯 Confidence: ", style="bold")
        overview_text.append(f"{analysis.confidence:.1%}", style=self.colors['success'])
        
        overview_panel = Panel(
            overview_text,
            title="🔍 Project Analysis",
            border_style=self.colors['info'],
            box=box.ROUNDED
        )
        
        self.console.print(overview_panel)
        
        # Frameworks and languages
        if analysis.detected_frameworks or analysis.languages:
            tech_table = Table(
                title="🛠️ Detected Technologies",
                box=box.ROUNDED,
                border_style=self.colors['info']
            )
            
            tech_table.add_column("Type", style="bold")
            tech_table.add_column("Items", style=self.colors['primary'])
            
            if analysis.detected_frameworks:
                tech_table.add_row("Frameworks", ", ".join(analysis.detected_frameworks))
            if analysis.languages:
                tech_table.add_row("Languages", ", ".join(analysis.languages))
            
            self.console.print(tech_table)
        
        # Recommendations
        if analysis.recommendations:
            rec_panel = Panel(
                "\n".join([f"• {rec}" for rec in analysis.recommendations]),
                title="💡 Recommendations",
                border_style=self.colors['success'],
                box=box.ROUNDED
            )
            self.console.print(rec_panel)
        
        self.console.print()
    
    def show_portal_status(self, orchestrator: PortalOrchestrator) -> None:
        """Display portal status in a clean format."""
        summary = orchestrator.get_portal_summary()
        statuses = orchestrator.get_all_portal_statuses()
        
        # Summary panel
        summary_text = Text()
        summary_text.append(f"🌐 Total Portals: ", style="bold")
        summary_text.append(str(summary['total_portals']), style=self.colors['primary'])
        summary_text.append(f"\n🔧 CLI Tools Installed: ", style="bold")
        summary_text.append(str(summary['installed_cli_tools']), style=self.colors['success'])
        summary_text.append(f"\n🔑 Logged In: ", style="bold")
        summary_text.append(str(summary['logged_in_portals']), style=self.colors['info'])
        
        summary_panel = Panel(
            summary_text,
            title="🔗 Portal Status",
            border_style=self.colors['info'],
            box=box.ROUNDED
        )
        
        self.console.print(summary_panel)
        
        # Individual portal status
        if statuses:
            portal_table = Table(
                title="📋 Portal Details",
                box=box.ROUNDED,
                border_style=self.colors['info']
            )
            
            portal_table.add_column("Portal", style="bold")
            portal_table.add_column("Status", style="bold")
            portal_table.add_column("CLI Tool", style=self.colors['primary'])
            portal_table.add_column("Login", style="bold")
            
            for portal_name, status in statuses.items():
                # Status emoji
                status_emoji = "✅" if status.installation_status == "installed" else "❌"
                
                # Login emoji
                login_emoji = "🔑" if status.is_logged_in else "🔒"
                
                portal_table.add_row(
                    status.name,
                    f"{status_emoji} {status.installation_status}",
                    status.cli_tool or "N/A",
                    login_emoji
                )
            
            self.console.print(portal_table)
        
        self.console.print()
    
    def show_chat_interface(self, chat_agent) -> None:
        """Display the chat interface."""
        self.console.print(Panel(
            "💬 CONFIGO Chat Mode\n\nAsk me anything about tools, setup, or development!",
            title="Chat Interface",
            border_style=self.colors['primary'],
            box=box.ROUNDED
        ))
        
        # Show quick help
        help_text = chat_agent.get_quick_help()
        self.console.print(Panel(
            help_text,
            title="💡 Quick Help",
            border_style=self.colors['info'],
            box=box.ROUNDED
        ))
        
        self.console.print()
    
    def show_chat_response(self, response: ChatResponse) -> None:
        """Display a chat response."""
        # Determine response style based on type
        if response.action_type == "info":
            border_style = self.colors['info']
            icon = "💡"
        elif response.action_type == "command":
            border_style = self.colors['warning']
            icon = "⚡"
        elif response.action_type == "error":
            border_style = self.colors['error']
            icon = "❌"
        else:
            border_style = self.colors['primary']
            icon = "💬"
        
        # Create response panel
        response_text = Text()
        response_text.append(f"{icon} ", style="bold")
        response_text.append(response.message, style="white")
        
        if response.command:
            response_text.append(f"\n\n🔧 Command: ", style="bold")
            response_text.append(response.command, style=self.colors['primary'])
        
        if response.requires_confirmation:
            response_text.append(f"\n\n⚠️ This action requires confirmation", style=self.colors['warning'])
        
        panel = Panel(
            response_text,
            title=f"CONFIGO Response ({response.action_type.title()})",
            border_style=border_style,
            box=box.ROUNDED
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_validation_results(self, results: List[Dict[str, Any]]) -> None:
        """Display validation results in a clean format."""
        if not results:
            self.console.print(Panel(
                "No validation results to display",
                border_style=self.colors['muted'],
                box=box.ROUNDED
            ))
            return
        
        # Create validation table
        table = Table(
            title="🔍 Validation Results",
            box=box.ROUNDED,
            border_style=self.colors['info']
        )
        
        table.add_column("Tool", style="bold")
        table.add_column("Status", style="bold")
        table.add_column("Version", style=self.colors['primary'])
        table.add_column("Time", style=self.colors['muted'])
        table.add_column("Confidence", style="bold")
        
        for result in results:
            # Status emoji and color
            if result.get('is_installed', False):
                status_emoji = "✅"
                status_style = self.colors['success']
            else:
                status_emoji = "❌"
                status_style = self.colors['error']
            
            # Version
            version = result.get('version', 'N/A')
            
            # Time
            time_taken = f"{result.get('validation_time', 0):.2f}s"
            
            # Confidence
            confidence = f"{result.get('confidence', 0):.1%}"
            
            table.add_row(
                result.get('tool_name', 'Unknown'),
                f"{status_emoji} {'Installed' if result.get('is_installed') else 'Failed'}",
                version,
                time_taken,
                confidence
            )
        
        self.console.print(table)
        
        # Show summary
        successful = sum(1 for r in results if r.get('is_installed', False))
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        summary_text = Text()
        summary_text.append(f"✅ Successful: ", style="bold")
        summary_text.append(str(successful), style=self.colors['success'])
        summary_text.append(f" | ❌ Failed: ", style="bold")
        summary_text.append(str(total - successful), style=self.colors['error'])
        summary_text.append(f" | 📊 Success Rate: ", style="bold")
        summary_text.append(f"{success_rate:.1f}%", style=self.colors['primary'])
        
        summary_panel = Panel(
            summary_text,
            border_style=self.colors['info'],
            box=box.ROUNDED
        )
        
        self.console.print(summary_panel)
        self.console.print()
    
    def show_error_message(self, error: str, suggestion: str = "") -> None:
        """Display a humanized error message."""
        error_text = Text()
        error_text.append("❌ Oops! ", style=f"bold {self.colors['error']}")
        error_text.append(error, style="white")
        
        if suggestion:
            error_text.append(f"\n\n💡 Suggestion: ", style=f"bold {self.colors['info']}")
            error_text.append(suggestion, style="white")
        
        panel = Panel(
            error_text,
            title="Error",
            border_style=self.colors['error'],
            box=box.ROUNDED
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_success_message(self, message: str) -> None:
        """Display a success message."""
        success_text = Text()
        success_text.append("✅ ", style=f"bold {self.colors['success']}")
        success_text.append(message, style="white")
        
        panel = Panel(
            success_text,
            title="Success",
            border_style=self.colors['success'],
            box=box.ROUNDED
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_info_message(self, message: str) -> None:
        """Display an info message."""
        info_text = Text()
        info_text.append("ℹ️ ", style=f"bold {self.colors['info']}")
        info_text.append(message, style="white")
        
        panel = Panel(
            info_text,
            title="Info",
            border_style=self.colors['info'],
            box=box.ROUNDED
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_progress(self, description: str, total: int = 100) -> tuple[Progress, int]:
        """Show a progress bar."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
        
        task = progress.add_task(description, total=total)
        return progress, task
    
    def show_profile_selector(self, profiles: List[Any]) -> str:
        """Show profile selection interface."""
        if not profiles:
            self.console.print(Panel(
                "No profiles found. Creating default profile...",
                border_style=self.colors['info'],
                box=box.ROUNDED
            ))
            return "default"
        
        # Create profile table
        table = Table(
            title="👤 Select Profile",
            box=box.ROUNDED,
            border_style=self.colors['info']
        )
        
        table.add_column("#", style="bold")
        table.add_column("Name", style=self.colors['primary'])
        table.add_column("Created", style=self.colors['muted'])
        table.add_column("Last Used", style=self.colors['muted'])
        
        for i, profile in enumerate(profiles, 1):
            created = profile.created_at.strftime('%Y-%m-%d') if hasattr(profile, 'created_at') else 'Unknown'
            last_used = profile.last_used.strftime('%Y-%m-%d %H:%M') if hasattr(profile, 'last_used') and profile.last_used else 'Never'
            
            table.add_row(
                str(i),
                profile.name,
                created,
                last_used
            )
        
        self.console.print(table)
        
        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    f"Select profile (1-{len(profiles)}) or 'new' for new profile",
                    default="1"
                )
                
                if choice.lower() == 'new':
                    name = Prompt.ask("Enter profile name")
                    return f"new:{name}"
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(profiles):
                    return profiles[choice_num - 1].profile_id
                else:
                    self.console.print("Invalid selection. Please try again.", style=self.colors['error'])
                    
            except ValueError:
                self.console.print("Please enter a valid number.", style=self.colors['error'])
    
    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for an action."""
        return Confirm.ask(message, default=True)
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input."""
        return Prompt.ask(prompt)
    
    def show_loading_spinner(self, message: str):
        """Show a loading spinner."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(message, total=None)
            yield progress, task
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        self.console.clear()
    
    def print_separator(self) -> None:
        """Print a visual separator."""
        self.console.print("─" * self.console.width, style=self.colors['muted'])
    
    def show_command_output(self, command: str, output: str, success: bool = True) -> None:
        """Display command output in a clean format."""
        # Command header
        cmd_text = Text()
        cmd_text.append("🔧 Command: ", style="bold")
        cmd_text.append(command, style=self.colors['primary'])
        
        cmd_panel = Panel(
            cmd_text,
            border_style=self.colors['info'],
            box=box.ROUNDED
        )
        
        self.console.print(cmd_panel)
        
        # Output
        if output:
            output_style = self.colors['success'] if success else self.colors['error']
            output_panel = Panel(
                Syntax(output, "bash", theme="monokai"),
                title="Output" if success else "Error",
                border_style=output_style,
                box=box.ROUNDED
            )
            self.console.print(output_panel)
        
        self.console.print() 