from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "src" / "resources"

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative
    else:
        return RESOURCES_DIR / relative