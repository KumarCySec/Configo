from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.layout import Layout
from typing import List, Dict, Any, Optional

class ConfigoLayout:
    def __init__(self):
        self.console = Console()
        self.version = "v1.0"
        self.agent_name = "CONFIGO"
        # Persistent Rich Layout for body/footer
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=2)
        )
        self.layout["header"].update(self.render_header())
        self.layout["footer"].update(self.render_footer())

    def render_header(self) -> Panel:
        # Stylish, concise CONFIGO banner
        banner = Text.assemble(
            ("█▓▒░ ", "bold magenta"),
            ("CONFIGO", "bold white on magenta"),
            (" ░▒▓█", "bold magenta"),
        )
        return Panel(banner, style="magenta", padding=(0,1), border_style="magenta")

    def render_plan(self, tools: List[Dict[str, Any]]) -> Panel:
        table = Table.grid(expand=True)
        table.add_column("Component", style="bold cyan")
        table.add_column("Status", justify="right")
        for tool in tools:
            table.add_row(tool['name'], tool['status'])
        return Panel(table, title="🧠 Setup Plan", border_style="magenta", padding=(0,1))

    def render_detection(self, detected: Dict[str, str]) -> Optional[Panel]:
        if not detected:
            return None
        table = Table.grid(expand=True)
        table.add_column("Tool", style="bold cyan")
        table.add_column("Detected", justify="right")
        for name, status in detected.items():
            table.add_row(name, status)
        return Panel(table, title="🔍 Detection Results", border_style="cyan", padding=(0,1))

    def render_prompt(self, prompt_text: str) -> Panel:
        return Panel(
            Align.center(Text(prompt_text, style="bold white"), vertical="middle"),
            border_style="green", padding=(0,1)
        )

    def render_footer(self) -> Align:
        # One-line, right-aligned, trimmed footer
        footer = Text.assemble(
            ("Tab", "bold cyan"), ("=complete  ", "dim"),
            ("Ctrl+C", "bold cyan"), ("=quit  ", "dim"),
            ("CONFIGO ", "bold magenta"), (self.version, "dim")
        )
        return Align.right(footer)

    def update_body(self, content: RenderableType) -> None:
        """Update the main body section with a Panel, Table, or Group."""
        self.layout["body"].update(content)

    def show_plan(self, tools: List[Dict[str, Any]]) -> None:
        """Display the setup plan in the body section."""
        self.update_body(self.render_plan(tools))

    def final_summary(self, detected: Dict[str, str]) -> None:
        """Display the install summary in the body section."""
        from ui.summary import show_summary
        summary_panel = show_summary(detected)
        self.update_body(summary_panel)

    def render(self, tools: List[Dict[str, Any]], detected: Dict[str, str], prompt_text: str) -> None:
        """
        Compose all sections into a single layout for one-pass rendering.
        This ensures:
        - No duplicate headers/footers
        - No empty space or empty panels
        - Responsive, compact, and modern UI
        """
        self.show_plan(tools)
        # Optionally add detection results below plan
        detection_panel = self.render_detection(detected)
        if detection_panel:
            self.layout["body"].update(Group(self.render_plan(tools), detection_panel))
        self.layout["footer"].update(self.render_footer())
        # Add prompt at the bottom of body if needed
        if prompt_text:
            self.layout["body"].update(Group(self.layout["body"].renderable, self.render_prompt(prompt_text)))
        self.console.clear()
        self.console.print(self.layout)

    # Prevent external .layout access
    @property
    def _layout(self):
        raise AttributeError("Direct access to .layout is not allowed. Use update_body(), show_plan(), or final_summary() methods instead.") 