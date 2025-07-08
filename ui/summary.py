from rich.panel import Panel
from rich.table import Table
from typing import Dict

def show_summary(detected_tools: Dict[str, str]) -> Panel:
    """
    Generate a summary panel for the installation.
    """
    table = Table.grid(expand=True)
    table.add_column("Component", style="bold cyan")
    table.add_column("Status", justify="right")
    for name, status in detected_tools.items():
        table.add_row(name, status)
    return Panel(table, title="Install Summary", border_style="magenta")

def show_summary_old(detected, layout):
    from rich.panel import Panel
    summary = "\n".join(f"{name}: {status}" for name, status in detected.items())
    layout.layout["body"].update(Panel(summary, title="Install Summary", border_style="brand"))
    layout.console.print(layout.layout)
    # Write to log
    with open("logs/install-summary.md", "w") as f:
        f.write(summary) 