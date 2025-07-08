import shutil
import subprocess

def detect_installed_tools(tools):
    detected = {}
    for tool in tools:
        cmd = tool.get('detect_cmd', tool['name'].lower())
        if shutil.which(cmd):
            try:
                version = subprocess.check_output([cmd, '--version'], text=True, stderr=subprocess.DEVNULL).split('\n')[0]
                detected[tool['name']] = f"✅ {version}"
                # Update the tool status in the original list
                tool['status'] = f"✅ {version}"
            except Exception:
                detected[tool['name']] = "✅ Already installed"
                tool['status'] = "✅ Already installed"
        else:
            detected[tool['name']] = "⬇️ To be installed"
            tool['status'] = "⬇️ To be installed"
    return detected 