import os
from pathlib import Path

def is_project_initialized() -> bool:
    """
    Checks if a project is initialized by looking for the project settings file.
    """
    project_path = Path(os.getenv("AICONSOLE_PROJECT_PATH", os.getcwd()))
    settings_path = project_path / "settings.json"
    return settings_path.exists() 