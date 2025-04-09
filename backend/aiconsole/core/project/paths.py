# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
from pathlib import Path
from typing import Optional

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project.init import is_project_initialized
from aiconsole.utils.resource_to_path import resource_to_path

_log = logging.getLogger(__name__)


def get_project_path() -> Path:
    """
    Returns the path to the current project.
    If no project is initialized, returns the current working directory.
    """
    return Path(os.getenv("AICONSOLE_PROJECT_PATH", os.getcwd()))


def get_project_assets_directory() -> Path:
    """
    Returns the path to the assets directory of the current project.
    Creates the directory if it doesn't exist.
    """
    path = get_project_path() / "assets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_settings_path() -> Path:
    """
    Returns the path to the settings file of the current project.
    """
    return get_project_path() / "settings.json"


def get_project_chats_directory() -> Path:
    """
    Returns the path to the chats directory of the current project.
    Creates the directory if it doesn't exist.
    """
    path = get_project_path() / "chats"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_chat_path(chat_id: str) -> Path:
    """
    Returns the path to a specific chat file in the current project.
    """
    return get_project_chats_directory() / f"{chat_id}.json"


def get_project_asset_path(asset_id: str) -> Path:
    """
    Returns the path to a specific asset file in the current project.
    """
    return get_project_assets_directory() / f"{asset_id}.json"


def get_project_database_path() -> Path:
    """
    Returns the path to the database file of the current project.
    """
    return get_project_path() / "aiconsole.db"


def get_core_assets_directory(asset_type: AssetType):
    return resource_to_path(f"aiconsole.preinstalled.{asset_type.value}s")


def get_history_directory(project_path: Path | None = None):
    if not is_project_initialized() and not project_path:
        raise ValueError("Project settings are not initialized")
    return get_project_directory(project_path) / "chats"


def get_aic_directory(project_path: Path | None = None):
    if not is_project_initialized() and not project_path:
        raise ValueError("Project settings are not initialized")
    return get_project_directory(project_path) / ".aic"


def get_project_directory(project_path: Path | None = None):
    if not is_project_initialized() and not project_path:
        raise ValueError("Project settings are not initialized")

    project_directory = project_path or Path(os.getcwd())
    return project_directory


def get_project_directory_safe() -> Path | None:
    if not is_project_initialized():
        return None

    return get_project_directory().absolute()


def get_credentials_directory(project_path: Path | None = None):
    if not is_project_initialized() and not project_path:
        raise ValueError("Project settings are not initialized")
    return get_aic_directory(project_path) / "credentials"


def get_project_name(project_path: Path | None = None):
    if not is_project_initialized() and not project_path:
        raise ValueError("Project settings are not initialized")
    return get_project_directory(project_path).name
