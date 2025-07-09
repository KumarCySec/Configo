#!/usr/bin/env python3
"""
Test script to verify the input formatting fix.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from ui.enhanced_messages import EnhancedMessageDisplay

def test_input_formatting():
    """Test the fixed input formatting."""
    console = Console()
    messages = EnhancedMessageDisplay(console)
    
    print("🧪 Testing Fixed Input Formatting")
    print("=" * 40)
    
    # Test the banner
    messages.show_autonomous_banner()
    
    # Test the app install prompt (without actually taking input)
    print("\n[bold]Testing app install prompt formatting:[/bold]")
    console.print("[bold cyan]What app do you want to install? [/bold cyan]", end="")
    print(" (This should show properly formatted text)")
    
    # Test the confirmation prompt
    print("\n[bold]Testing confirmation prompt formatting:[/bold]")
    console.print("[bold yellow]Proceed with installation? (Y/n): [/bold yellow]", end="")
    print(" (This should show properly formatted text)")
    
    print("\n[green]✅ Input formatting test completed![/green]")
    print("[dim]If you see properly formatted text above without any raw markup, the fix worked![/dim]")

if __name__ == "__main__":
    test_input_formatting() 