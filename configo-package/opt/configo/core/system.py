import platform
import shutil

try:
    import distro
except ImportError:
    distro = None

def get_system_info():
    return {
        "os": platform.system(),                 # Linux, Darwin, Windows
        "version": platform.version(),
        "arch": platform.machine(),
        "distro": distro.id() if distro and platform.system() == "Linux" else "",
        "package_managers": detect_pkg_managers()
    }

def detect_pkg_managers():
    return [cmd for cmd in ["apt", "snap", "flatpak", "brew", "winget", "choco"] if shutil.which(cmd)] 