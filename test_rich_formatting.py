#!/usr/bin/env python3
"""
Test script to verify Rich formatting is working correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel

def test_rich_formatting():
    """Test basic Rich formatting."""
    console = Console()
    
    print("🧪 Testing Rich Formatting")
    print("=" * 40)
    
    # Test basic formatting
    console.print("[bold red]This should be bold red[/bold red]")
    console.print("[cyan]This should be cyan[/cyan]")
    console.print("[dim]This should be dim[/dim]")
    
    # Test panel
    console.print(Panel(
        "[bold magenta]🚀 CONFIGO App Installer[/bold magenta]\n"
        "[dim]Simply tell me what app you want to install![/dim]\n\n"
        "[bold]Examples:[/bold]\n"
        "• Install Discord\n"
        "• I need Chrome\n"
        "• Get me Zoom\n"
        "• Install Slack",
        title="📱 Natural Language App Installation",
        border_style="magenta"
    ))
    
    # Test input prompt
    console.print()
    test_input = input("[bold cyan]Test input prompt: [/bold cyan]")
    console.print(f"[green]You entered: {test_input}[/green]")

def test_ui_component():
    """Test the UI component specifically."""
    console = Console()
    
    print("\n🧪 Testing UI Component")
    print("=" * 40)
    
    try:
        from ui.enhanced_messages import EnhancedMessageDisplay
        messages = EnhancedMessageDisplay(console)
        
        # Test the banner
        messages.show_autonomous_banner()
        
        # Test the app install prompt
        console.print("\n[bold]Testing app install prompt:[/bold]")
        # Don't actually call input() in test, just show the panel
        console.print(Panel(
            "[bold magenta]🚀 CONFIGO App Installer[/bold magenta]\n"
            "[dim]Simply tell me what app you want to install![/dim]\n\n"
            "[bold]Examples:[/bold]\n"
            "• Install Discord\n"
            "• I need Chrome\n"
            "• Get me Zoom\n"
            "• Install Slack",
            title="📱 Natural Language App Installation",
            border_style="magenta"
        ))
        
        console.print("[green]✅ UI component test passed![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ UI component test failed: {e}[/red]")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    console = Console()
    
    try:
        test_rich_formatting()
        test_ui_component()
        
        console.print("\n[bold green]🎉 All Rich formatting tests completed![/bold green]")
        console.print("[dim]If you see properly formatted text above, Rich is working correctly.[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Test failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 