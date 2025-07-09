#!/usr/bin/env python3
"""
CONFIGO App Installation Demo
=============================

Demonstrates the natural language app installation feature.
This script shows how CONFIGO can install applications using simple commands.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.system import get_system_info
from core.memory import AgentMemory
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.shell_executor import ShellExecutor
from ui.enhanced_messages import EnhancedMessageDisplay
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def demo_app_installation():
    """Demonstrate the app installation feature."""
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    # Show demo banner
    console.print(Panel(
        "[bold magenta]🚀 CONFIGO App Installation Demo[/bold magenta]\n"
        "[dim]Natural Language App Installation in Action[/dim]",
        title="📱 Demo",
        border_style="magenta"
    ))
    console.print()
    
    # Initialize components
    console.print("[yellow]🔧 Initializing CONFIGO components...[/yellow]")
    memory = AgentMemory()
    llm_agent = EnhancedLLMAgent(memory)
    system_info = get_system_info()
    
    console.print(f"[green]✅ System detected: {system_info['os']} ({system_info['distro']})[/green]")
    console.print(f"[green]✅ Package managers: {', '.join(system_info['package_managers'])}[/green]")
    console.print()
    
    # Demo app installation
    demo_apps = [
        "Slack",
        "Discord", 
        "Chrome",
        "Zoom"
    ]
    
    for app_name in demo_apps:
        console.print(f"[bold cyan]🎯 Demo: Installing {app_name}[/bold cyan]")
        console.print()
        
        # Check if already installed
        if memory.is_app_installed(app_name):
            messages.show_already_installed(app_name)
            continue
        
        # Show installation start
        messages.show_app_install_start(app_name, system_info)
        
        # Generate installation plan
        console.print(f"[yellow]🧠 Generating installation plan for {app_name}...[/yellow]")
        plan = llm_agent.get_install_plan(app_name, system_info)
        
        if not plan:
            console.print(f"[red]❌ Could not generate plan for {app_name}[/red]")
            continue
        
        # Show the plan
        messages.show_install_plan(plan)
        
        # Ask user if they want to proceed
        console.print(f"[bold yellow]⚠️  This is a demo. Would you like to actually install {app_name}? (y/N)[/bold yellow]")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            # Execute the installation
            console.print(f"[yellow]🔄 Executing installation plan...[/yellow]")
            executor = ShellExecutor(max_retries=3)
            result = executor.execute_install_plan(plan, llm_agent)
            
            # Record in memory
            memory.record_app_install(app_name, plan, result)
            
            # Show result
            if result['success']:
                messages.show_install_success(app_name, result)
            else:
                messages.show_install_final_error(app_name, result.get('error', 'Unknown error'))
        else:
            console.print(f"[dim]⏭️  Skipping actual installation of {app_name}[/dim]")
        
        console.print()
        console.print("─" * 60)
        console.print()
    
    # Show final summary
    installed_apps = memory.get_installed_apps()
    console.print(Panel(
        f"[bold green]🎉 Demo Complete![/bold green]\n\n"
        f"📊 [bold]Summary:[/bold]\n"
        f"• Apps in memory: {len(installed_apps)}\n"
        f"• Successful installations: {len([app for app in installed_apps.values() if app.get('success', False)])}\n"
        f"• System: {system_info['os']} ({system_info['distro']})\n\n"
        f"[dim]To use CONFIGO app installer: python main.py install[/dim]",
        title="📱 Demo Summary",
        border_style="green"
    ))

def main():
    """Run the demo."""
    try:
        demo_app_installation()
    except KeyboardInterrupt:
        print("\n[red]Demo interrupted by user[/red]")
    except Exception as e:
        print(f"\n[red]Demo failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 