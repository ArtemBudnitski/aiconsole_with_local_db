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

import os
import sys
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from fastapi import BackgroundTasks

from aiconsole.api.websockets.connection_manager import (
    AICConnection,
    connection_manager,
)
from aiconsole.api.websockets.server_messages import (
    InitialProjectStatusServerMessage,
    ProjectClosedServerMessage,
    ProjectLoadingServerMessage,
    ProjectOpenedServerMessage,
)
from aiconsole.core.assets.types import AssetType
from aiconsole.core.code_running.run_code import reset_code_interpreters
from aiconsole.core.code_running.virtual_env.create_dedicated_venv import (
    create_dedicated_venv,
)
from aiconsole.core.db.database import db
from aiconsole.core.db.models import Project as ProjectModel
from aiconsole.core.db.operations import DatabaseOperations
from aiconsole.core.db.migration import migrate_all
from aiconsole.core.project.init import is_project_initialized
from aiconsole.core.project.paths import (
    get_project_assets_directory,
    get_project_chats_directory,
    get_project_database_path,
    get_project_path,
    get_project_settings_path,
)
from aiconsole.core.settings.settings import settings
from aiconsole.core.storage.db_storage import DatabaseStorage

if TYPE_CHECKING:
    from aiconsole.core.assets import assets


_materials: "assets.Assets | None" = None
_agents: "assets.Assets | None" = None
_project_initialized = False

_log = logging.getLogger(__name__)


async def _clear_project():
    global _materials
    global _agents
    global _project_initialized

    if _materials:
        _materials.stop()

    if _agents:
        _agents.stop()

    reset_code_interpreters()

    _materials = None
    _agents = None
    _project_initialized = False


async def send_project_init(connection: AICConnection):
    from aiconsole.core.project.paths import get_project_directory, get_project_name

    await connection.send(
        InitialProjectStatusServerMessage(
            project_name=get_project_name() if is_project_initialized() else None,
            project_path=str(get_project_directory()) if is_project_initialized() else None,
        )
    )


def get_project_materials() -> "assets.Assets":
    if not _materials:
        raise ValueError("Project materials are not initialized")
    return _materials


def get_project_agents() -> "assets.Assets":
    if not _agents:
        raise ValueError("Project agents are not initialized")
    return _agents


async def close_project():
    await _clear_project()

    await connection_manager().send_to_all(ProjectClosedServerMessage())

    settings().configure(DatabaseStorage(project_path=None))


async def reinitialize_project():
    from aiconsole.core.assets import assets
    from aiconsole.core.project.paths import (
        get_project_directory,
        get_project_directory_safe,
        get_project_name,
    )
    from aiconsole.core.recent_projects.recent_projects import add_to_recent_projects

    await connection_manager().send_to_all(ProjectLoadingServerMessage())

    global _materials
    global _agents
    global _project_initialized

    await _clear_project()

    _project_initialized = True

    project_dir = get_project_directory()

    # Check if project needs migration
    if not DatabaseOperations.get_project(str(project_dir)):
        # Project not in database, needs migration
        print(f"Migrating project {project_dir} to database...")
        migrate_all(project_dir)
    else:
        print(f"Project {project_dir} already in database")
        # Save project to database (in case it needs updating)
        project = ProjectModel(
            id=str(project_dir),
            name=project_dir.name,
            path=str(project_dir)
        )
        DatabaseOperations.save_project(project)

    await add_to_recent_projects(project_dir)

    # Configure settings with database storage
    settings().configure(DatabaseStorage(project_path=project_dir))

    _agents = assets.Assets(asset_type=AssetType.AGENT)
    _materials = assets.Assets(asset_type=AssetType.MATERIAL)

    await connection_manager().send_to_all(
        ProjectOpenedServerMessage(path=str(get_project_directory()), name=get_project_name())
    )

    await _materials.reload(initial=True)
    await _agents.reload(initial=True)


async def choose_project(path: Path, background_tasks: BackgroundTasks):
    if not path.exists():
        raise ValueError(f"Path {path} does not exist")

    # Change cwd and import path
    os.chdir(path)
    sys.path[0] = str(path)

    await reinitialize_project()

    background_tasks.add_task(create_dedicated_venv)


def initialize_project(project_path: Path, project_name: str) -> None:
    """
    Initializes a new project at the specified path.
    """
    # Create project directories
    get_project_assets_directory().mkdir(parents=True, exist_ok=True)
    get_project_chats_directory().mkdir(parents=True, exist_ok=True)
    
    # Create project settings
    settings = {
        "name": project_name,
        "version": "1.0.0",
    }
    
    with open(get_project_settings_path(), "w") as f:
        json.dump(settings, f, indent=2)
    
    # Create project record in database
    project = ProjectModel(
        id=str(project_path),
        name=project_name,
        path=str(project_path),
    )
    db.save_project(project)
    
    _log.info(f"Project '{project_name}' initialized at {project_path}")


def get_current_project() -> Optional[ProjectModel]:
    """
    Returns the current project if one is initialized.
    """
    if not is_project_initialized():
        return None
    
    project_path = get_project_path()
    return db.get_project(str(project_path))


def set_current_project(project_path: Path) -> None:
    """
    Sets the current project path.
    """
    os.environ["AICONSOLE_PROJECT_PATH"] = str(project_path)
    
    # Initialize database if it doesn't exist
    db_path = get_project_database_path()
    if not db_path.exists():
        db.initialize()
    
    _log.info(f"Current project set to {project_path}")
