import sys
import os
import platform
import subprocess
from pathlib import Path

def get_platform():
    return platform.system().lower()

def get_python_executable():
    """Returns the path to the current Python interpreter."""
    return sys.executable

def open_file_default(filepath: str):
    """Opens a file using the OS default application (cross-platform)."""
    if get_platform() == "windows":
        os.startfile(filepath)
    elif get_platform() == "darwin": # macOS
        subprocess.call(["open", filepath])
    else: # Linux
        subprocess.call(["xdg-open", filepath])

def get_config_dir():
    """Returns a cross-platform directory for app configuration."""
    if get_platform() == "windows":
        return Path(os.getenv("APPDATA")) / "ApexHunter"
    elif get_platform() == "darwin":
        return Path.home() / "Library" / "Application Support" / "ApexHunter"
    else:
        return Path.home() / ".config" / "apexhunter"
