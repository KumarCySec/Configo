from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.rule import Rule
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from typing import List, Dict, Any, Optional
import time

class MessageDisplay:
    """Handles all user-facing console messages with friendly, styled output."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def show_welcome(self) -> None:
        """Display the welcome message with the CONFIGO banner."""
        import pyfiglet
        
        # Get the ASCII art banner
        width = self.console.size.width
        if width > 60:
            logo = pyfiglet.figlet_format("CONFIGO", font="slant")
        else:
            logo = "CONFIGO"
        
        # Display the banner
        self.console.print(f"[magenta]{logo}[/magenta]")
        self.console.print("[bold magenta]🚀 CONFIGO: AI Setup Agent[/bold magenta]", style="magenta")
        self.console.print()
    
    def show_environment_prompt(self) -> str:
        """Display the environment setup prompt."""
        self.console.print()
        self.console.print("[bold cyan]🧠 What kind of environment are you setting up?[/bold cyan]")
        self.console.print("[dim]Examples:[/dim]")
        self.console.print("  • [green]Full Stack AI Developer on Linux[/green]")
        self.console.print("  • [green]Data Science Environment[/green]")
        self.console.print("  • [green]Web Development Stack[/green]")
        self.console.print("  • [green]Machine Learning Setup[/green]")
        self.console.print()
        return self.console.input("[bold white]> [/bold white]").strip()
    
    def show_ai_query_start(self, environment: str) -> None:
        """Show that we're starting the AI query process."""
        self.console.print()
        self.console.rule("[bold blue]🤖 AI Stack Generation[/bold blue]", style="blue")
        self.console.print(f"[cyan]🧠 Analyzing environment: [bold green]{environment}[/bold green][/cyan]")
        self.console.print("[dim]⏳ Checking with Gemini for the best tech stack...[/dim]")
    
    def show_ai_query_success(self, tool_count: int, portal_count: int = 0) -> None:
        """Show successful AI response."""
        self.console.print(f"[bold green]✅ Stack generated successfully[/bold green]")
        self.console.print(f"[white]📦 Tools: [bold]{tool_count}[/bold] | 🔗 Logins: [bold]{portal_count}[/bold][/white]")
    
    def show_ai_query_fallback(self) -> None:
        """Show fallback to default tools."""
        self.console.print("[yellow]⚠️  Using default stack (AI unavailable)[/yellow]")
    
    def show_detection_start(self) -> None:
        """Show that we're starting tool detection."""
        self.console.print()
        self.console.rule("[bold cyan]🔍 Tool Detection[/bold cyan]", style="cyan")
        self.console.print("[cyan]🔍 Checking for already installed tools...[/cyan]")
    
    def show_detection_complete(self, installed_count: int, total_count: int) -> None:
        """Show detection results."""
        self.console.print(f"[green]✅ Detection complete: [bold]{installed_count}[/bold] of [bold]{total_count}[/bold] tools already installed[/green]")
    
    def show_plan_header(self, environment: str) -> None:
        """Show the setup plan header."""
        self.console.print()
        self.console.rule(f"[bold green]🔍 Setup Plan for: {environment}[/bold green]", style="green")
    
    def show_plan_section(self, title: str, tools: List[Dict[str, Any]], icon: str = "📦") -> None:
        """Show a section of the setup plan."""
        if not tools:
            return
            
        self.console.print(f"\n[bold blue]{icon} {title}:[/bold blue]")
        
        for tool in tools:
            name = tool.get('name', 'Unknown Tool')
            status = tool.get('status', '⬇️ To be installed')
            
            if '✅' in status or 'Already' in status:
                status_style = "green"
                icon = "  ✔️"
            else:
                status_style = "yellow"
                icon = "  ⬇️"
            
            self.console.print(f"{icon} [bold]{name}[/bold] -> [{status_style}]{status}[/{status_style}]")
    
    def show_login_portals(self, portals: List[Any]) -> None:
        """Show login portals section."""
        if not portals:
            return
            
        self.console.print(f"\n[bold blue]🌐 Browser Logins Required:[/bold blue]")
        
        for portal in portals:
            # Handle both LoginPortal objects and dictionaries
            if hasattr(portal, 'name'):
                # LoginPortal object
                name = portal.name
                url = portal.url
                description = portal.description
            else:
                # Dictionary
                name = portal.get('name', 'Unknown Portal')
                url = portal.get('url', '')
                description = portal.get('description', '')
            
            self.console.print(f"  🔗 [bold]{name}[/bold] ([link={url}]{url}[/link])")
            if description:
                self.console.print(f"     [dim]{description}[/dim]")
    
    def show_plan_summary(self, total_tools: int, installed_count: int, portal_count: int) -> None:
        """Show the plan summary."""
        to_install_count = total_tools - installed_count
        
        self.console.print()
        self.console.rule("[bold white]📊 Summary[/bold white]", style="white")
        self.console.print(f"  📦 Total tools: [bold]{total_tools}[/bold]")
        self.console.print(f"  ✔️ Already installed: [bold green]{installed_count}[/bold green]")
        self.console.print(f"  ⬇️ To be installed: [bold yellow]{to_install_count}[/bold yellow]")
        self.console.print(f"  🌐 Login portals: [bold blue]{portal_count}[/bold blue]")
        self.console.print()
    
    def show_installation_prompt(self) -> bool:
        """Show the installation confirmation prompt."""
        response = self.console.input("[bold green]🚀 Proceed with installation? (y/n): [/bold green]").strip().lower()
        return response in ['y', 'yes']
    
    def show_installation_start(self) -> None:
        """Show that installation is starting."""
        self.console.print()
        self.console.rule("[bold yellow]🔧 Installation Process[/bold yellow]", style="yellow")
        self.console.print("[yellow]🔧 Installing tools and extensions...[/yellow]")
    
    def show_installation_progress(self, current: int, total: int, tool_name: str) -> None:
        """Show installation progress."""
        self.console.print(f"[{current}/{total}] 🔧 [bold]{tool_name}[/bold]")
    
    def show_installation_success(self, tool_name: str, version: str | None = None) -> None:
        """Show successful installation."""
        if version:
            self.console.print(f"  ✅ [green]{tool_name}[/green] installed successfully")
            self.console.print(f"     Version: [dim]{version}[/dim]")
        else:
            self.console.print(f"  ✅ [green]{tool_name}[/green] installed successfully")
    
    def show_installation_skipped(self, tool_name: str, reason: str = "already installed") -> None:
        """Show skipped installation."""
        self.console.print(f"  ⏭️  [blue]{tool_name}[/blue] skipped ({reason})")
    
    def show_installation_error(self, tool_name: str, error: str) -> None:
        """Show installation error."""
        self.console.print(f"  ❌ [red]{tool_name}[/red] failed: {error}")
    
    def show_login_portals_opening(self) -> None:
        """Show that login portals are being opened."""
        self.console.print()
        self.console.rule("[bold blue]🌐 Opening Login Portals[/bold blue]", style="blue")
        self.console.print("[blue]🌐 Opening browser tabs for required logins...[/blue]")
    
    def show_login_portal_opened(self, portal_name: str) -> None:
        """Show that a login portal was opened."""
        self.console.print(f"  ✅ [green]{portal_name}[/green] opened in browser")
    
    def show_login_portal_error(self, portal_name: str, error: str) -> None:
        """Show login portal error."""
        self.console.print(f"  ❌ [red]{portal_name}[/red] failed to open: {error}")
    
    def show_completion_message(self) -> None:
        """Show completion message."""
        self.console.print()
        self.console.rule("[bold green]🎉 Installation Complete![/bold green]", style="green")
        self.console.print("[green]🎉 Your development environment is ready![/green]")
        self.console.print()
        self.console.print("[dim]💡 Next steps:[/dim]")
        self.console.print("  1. Complete any browser logins")
        self.console.print("  2. Configure your development environment")
        self.console.print("  3. Start coding! 🚀")
        self.console.print()
    
    def show_aborted_message(self) -> None:
        """Show aborted message."""
        self.console.print()
        self.console.rule("[bold yellow]⏹️  Installation Aborted[/bold yellow]", style="yellow")
        self.console.print("[yellow]⏹️  Installation was cancelled by user.[/yellow]")
        self.console.print()
    
    def show_error_message(self, error: str) -> None:
        """Show error message."""
        self.console.print()
        self.console.rule("[bold red]❌ Error[/bold red]", style="red")
        self.console.print(f"[red]❌ {error}[/red]")
        self.console.print()
    
    def show_spinner(self, message: str) -> None:
        """Show a spinner with message."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(message, total=None)
            time.sleep(0.5)  # Brief pause to show spinner
    
    def show_step_progress(self, current_step: int, total_steps: int, step_name: str) -> None:
        """Show step progress."""
        self.console.print(f"[bold blue]Step {current_step}/{total_steps}:[/bold blue] [cyan]{step_name}[/cyan]") 