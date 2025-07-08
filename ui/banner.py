import pyfiglet

def print_banner(console):
    width = console.size.width
    if width > 60:
        logo = pyfiglet.figlet_format("CONFIGO", font="slant")
    else:
        logo = "CONFIGO"
    console.print(f"[magenta]{logo}[/magenta]\n[bold]🚀 CONFIGO: AI Setup Agent[/bold]", style="magenta") 