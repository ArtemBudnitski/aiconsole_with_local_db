import json
import logging
from pathlib import Path

from aiconsole.core.db.database import db
from aiconsole.core.db.models import Asset, Chat, Project as ProjectModel
from aiconsole.core.db.operations import DatabaseOperations
from aiconsole.core.project.paths import get_project_assets_path, get_project_chats_path, get_project_settings_path

logger = logging.getLogger(__name__)

def migrate_assets(project_path: Path) -> None:
    """Migrate assets from filesystem to database"""
    assets_path = get_project_assets_path(project_path)
    if not assets_path.exists():
        return

    for asset_file in assets_path.glob("*.json"):
        try:
            with open(asset_file, "r") as f:
                asset_data = json.load(f)
                asset = Asset(**asset_data)
                db.add(asset)
        except Exception as e:
            logger.error(f"Error migrating asset {asset_file}: {e}")

def migrate_chats(project_path: Path) -> None:
    """Migrate chats from filesystem to database"""
    chats_path = get_project_chats_path(project_path)
    if not chats_path.exists():
        return

    for chat_file in chats_path.glob("*.json"):
        try:
            with open(chat_file, "r") as f:
                chat_data = json.load(f)
                chat = Chat(**chat_data)
                db.add(chat)
        except Exception as e:
            logger.error(f"Error migrating chat {chat_file}: {e}")

def migrate_project(project_path: Path) -> None:
    """Migrate project settings from filesystem to database"""
    settings_path = get_project_settings_path(project_path)
    if not settings_path.exists():
        return

    try:
        with open(settings_path, "r") as f:
            project_data = json.load(f)
            project = ProjectModel(**project_data)
            db.add(project)
    except Exception as e:
        logger.error(f"Error migrating project settings: {e}")

def migrate_all() -> None:
    """Migrate all data from filesystem to database"""
    from aiconsole.core.project.init import is_project_initialized
    from aiconsole.core.project.paths import get_project_path

    project_path = get_project_path()
    if not is_project_initialized(project_path):
        return

    try:
        migrate_assets(project_path)
        migrate_chats(project_path)
        migrate_project(project_path)
        db.commit()
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        db.rollback() 