import subprocess

def install_tools(detected, layout, messages=None):
    total_tools = len([s for s in detected.values() if "to be installed" in s.lower()])
    current = 0
    
    for name, status in detected.items():
        if "to be installed" in status.lower():
            current += 1
            
            if messages:
                messages.show_installation_progress(current, total_tools, name)
            else:
                layout.console.print(f"[pending]⬇️ Installing {name}...[/pending]")
            
            # Simulate install
            try:
                subprocess.run(["echo", f"Installing {name}"], check=True)
                if messages:
                    messages.show_installation_success(name)
                else:
                    layout.console.print(f"[success]✅ {name} installed![/success]")
            except subprocess.CalledProcessError as e:
                if messages:
                    messages.show_installation_error(name, str(e))
                else:
                    layout.console.print(f"[error]❌ {name} failed: {e}[/error]") 