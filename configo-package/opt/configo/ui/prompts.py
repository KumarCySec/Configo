try:
    from prompt_toolkit import prompt
except ImportError:
    prompt = input

def get_environment(console):
    console.print("[header]What kind of environment are you setting up?[/header]")
    return prompt("> ").strip()

def confirm_install(console):
    console.print("[header]Proceed with installation? (y/n)[/header]")
    return prompt("> ").strip().lower() in ("y", "yes") 