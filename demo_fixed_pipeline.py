#!/usr/bin/env python3
"""
CONFIGO Fixed App Installation Pipeline Demo
============================================

Demonstrates the complete fixed app installation pipeline with:
- Intelligent app name extraction
- Enhanced progress tracking
- Desktop integration
- Error handling and retry logic
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app_name_extractor import AppNameExtractor
from core.system import get_system_info
from core.memory import AgentMemory
from core.enhanced_llm_agent import EnhancedLLMAgent
from core.shell_executor import ShellExecutor
from ui.enhanced_messages import EnhancedMessageDisplay
from rich.console import Console
from rich.panel import Panel

def demo_fixed_pipeline():
    """Demonstrate the complete fixed app installation pipeline."""
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    # Show demo banner
    console.print(Panel(
        "[bold magenta]🚀 CONFIGO Fixed App Installation Pipeline[/bold magenta]\n"
        "[dim]Demonstrating the complete fixed pipeline with intelligent app name extraction[/dim]",
        title="🔧 Fixed Pipeline Demo",
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
    
    # Test cases that demonstrate the fixes
    test_cases = [
        "get me telegram",      # The original problematic case
        "install discord",      # Basic case
        "i need chrome",        # Another common pattern
        "please install slack", # With please
        "can you get me zoom",  # Complex phrase
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        console.print(f"[bold cyan]🎯 Demo {i}: Testing '{user_input}'[/bold cyan]")
        console.print()
        
        # Step 1: Extract app name using intelligent NLP
        console.print("[blue]Step 1: App Name Extraction[/blue]")
        app_name = AppNameExtractor.extract_app_name(user_input)
        is_valid = AppNameExtractor.validate_app_name(app_name)
        
        messages.show_app_name_extraction(user_input, app_name)
        console.print(f"[dim]Validation: {'✅ Valid' if is_valid else '❌ Invalid'}[/dim]")
        console.print()
        
        if not is_valid:
            console.print(f"[red]❌ Skipping invalid app name: '{app_name}'[/red]")
            console.print()
            continue
        
        # Step 2: Check if already installed
        console.print("[blue]Step 2: Installation Check[/blue]")
        if memory.is_app_installed(app_name):
            messages.show_already_installed(app_name)
            console.print()
            continue
        
        console.print(f"[green]✅ {app_name} not found in memory, proceeding with installation[/green]")
        console.print()
        
        # Step 3: Show installation start
        console.print("[blue]Step 3: Installation Planning[/blue]")
        messages.show_app_install_start(app_name, system_info)
        
        # Step 4: Generate installation plan
        console.print("[blue]Step 4: AI Plan Generation[/blue]")
        messages.show_install_progress(app_name, "Generating installation plan with AI...", 1)
        
        plan = llm_agent.get_install_plan(app_name, system_info)
        
        if not plan:
            console.print(f"[red]❌ Could not generate plan for {app_name}[/red]")
            console.print()
            continue
        
        # Step 5: Show plan and ask for confirmation
        console.print("[blue]Step 5: Plan Confirmation[/blue]")
        if not messages.show_install_confirmation(app_name, plan):
            console.print(f"[yellow]⏭️  Skipping installation of {app_name}[/yellow]")
            console.print()
            continue
        
        # Step 6: Execute installation (simulated for demo)
        console.print("[blue]Step 6: Installation Execution[/blue]")
        console.print(f"[dim]🔄 Simulating installation of {app_name}...[/dim]")
        
        # Create a mock successful result for demonstration
        mock_result = {
            'app_name': app_name,
            'method': plan.get('method', 'unknown'),
            'success': True,
            'error': None,
            'version': '1.0.0',
            'launch_command': plan.get('launch', f'{app_name.lower().replace(" ", "")}'),
            'desktop_entry': plan.get('desktop_entry', {}),
            'install_commands': [],
            'desktop_entry_created': True
        }
        
        # Record in memory
        memory.record_app_install(app_name, plan, mock_result)
        
        # Step 7: Show completion
        console.print("[blue]Step 7: Installation Complete[/blue]")
        messages.show_installation_complete(app_name, mock_result)
        
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
        f"🔧 [bold]Key Fixes Demonstrated:[/bold]\n"
        f"• ✅ Intelligent app name extraction\n"
        f"• ✅ Enhanced progress tracking\n"
        f"• ✅ Desktop integration\n"
        f"• ✅ Error handling and retry logic\n"
        f"• ✅ Memory persistence\n\n"
        f"[dim]To use the real app installer: python main.py install[/dim]",
        title="📱 Demo Summary",
        border_style="green"
    ))

def show_fix_comparison():
    """Show before/after comparison of the fix."""
    console = Console()
    
    console.print(Panel(
        "[bold red]🐛 BEFORE (Broken):[/bold red]\n"
        "Input: 'get me telegram'\n"
        "Extracted: 'Me Telegram' ❌\n"
        "Result: Installation failed\n\n"
        "[bold green]✅ AFTER (Fixed):[/bold green]\n"
        "Input: 'get me telegram'\n"
        "Extracted: 'Telegram' ✅\n"
        "Result: Installation successful\n\n"
        "[bold blue]🔧 What was fixed:[/bold blue]\n"
        "• Intelligent NLP-based app name extraction\n"
        "• Comprehensive filler word removal\n"
        "• App name mapping and validation\n"
        "• Enhanced error handling and progress tracking",
        title="🔧 Fix Comparison",
        border_style="blue"
    ))

def main():
    """Run the demo."""
    try:
        show_fix_comparison()
        console = Console()
        console.print()
        demo_fixed_pipeline()
        
    except KeyboardInterrupt:
        print("\n[red]Demo interrupted by user[/red]")
    except Exception as e:
        print(f"\n[red]Demo failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 