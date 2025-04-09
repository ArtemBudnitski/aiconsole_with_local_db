import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from aiconsole.core.assets.types import Asset, AssetType
from aiconsole.core.chat.types import Chat, AICMessageGroup, ChatOptions
from aiconsole.core.db.database import db
from aiconsole.core.db.models import (
    Asset as AssetModel,
    Chat as ChatModel,
    ChatMessageGroup as ChatMessageGroupModel,
    ChatOption as ChatOptionModel,
    Project as ProjectModel,
)
from aiconsole.core.project.paths import (
    get_project_assets_directory,
    get_project_chats_directory,
    get_project_database_path,
    get_project_path,
)
from aiconsole.core.project.init import is_project_initialized

_log = logging.getLogger(__name__)

def migrate_assets(project_path: Path) -> None:
    """
    Migrates assets from the filesystem to the database.
    """
    assets_dir = get_project_assets_directory()
    if not assets_dir.exists():
        return

    for asset_file in assets_dir.glob("*.json"):
        try:
            with open(asset_file, "r") as f:
                asset_data = json.load(f)
                asset = Asset(**asset_data)
                
                # Convert to database model
                db_asset = AssetModel(
                    id=asset.id,
                    type=asset.type,
                    name=asset.name,
                    version=asset.version,
                    usage=asset.usage,
                    usage_examples=asset.usage_examples,
                    default_status=asset.default_status,
                    content_type=asset.content_type,
                    content=asset.content,
                    system=asset.system,
                    gpt_mode=asset.gpt_mode,
                    execution_mode=asset.execution_mode,
                    project_id=str(project_path),
                )
                
                # Save to database
                db.save_asset(db_asset)
                
                # Delete the file after successful migration
                os.remove(asset_file)
                
        except Exception as e:
            _log.error(f"Error migrating asset {asset_file}: {e}")

def migrate_chats(project_path: Path) -> None:
    """
    Migrates chats from the filesystem to the database.
    """
    chats_dir = get_project_chats_directory()
    if not chats_dir.exists():
        return

    for chat_file in chats_dir.glob("*.json"):
        try:
            with open(chat_file, "r") as f:
                chat_data = json.load(f)
                chat = Chat(**chat_data)
                
                # Convert to database model
                db_chat = ChatModel(
                    id=chat.id,
                    name=chat.name,
                    title_edited=chat.title_edited,
                    last_modified=chat.last_modified,
                )
                
                # Save chat to database
                db.save_chat(db_chat)
                
                # Migrate messages
                for message_group in chat.message_groups:
                    db_message = ChatMessageGroupModel(
                        chat_id=chat.id,
                        role=message_group.role,
                        agent_id=message_group.actor_id,
                        message=message_group.messages[0].content if message_group.messages else None,
                    )
                    db.save_chat_message(db_message)
                
                # Migrate options
                db_option = ChatOptionModel(
                    chat_id=chat.id,
                    option_key="agent_id",
                    option_value=chat.chat_options.agent_id,
                )
                db.save_chat_option(db_option)
                
                db_option = ChatOptionModel(
                    chat_id=chat.id,
                    option_key="materials_ids",
                    option_value=json.dumps(chat.chat_options.materials_ids),
                )
                db.save_chat_option(db_option)
                
                # Delete the file after successful migration
                os.remove(chat_file)
                
        except Exception as e:
            _log.error(f"Error migrating chat {chat_file}: {e}")

def migrate_project(project_path: Path) -> None:
    """
    Migrates project settings from the filesystem to the database.
    """
    settings_path = project_path / "settings.json"
    if not settings_path.exists():
        return

    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
            
            # Create project record
            project = ProjectModel(
                id=str(project_path),
                name=settings.get("name", "Unnamed Project"),
                path=str(project_path),
            )
            
            # Save project to database
            db.save_project(project)
            
            # Delete the settings file after successful migration
            os.remove(settings_path)
            
    except Exception as e:
        _log.error(f"Error migrating project settings: {e}")

def migrate_all() -> None:
    """
    Migrates all data from the filesystem to the database.
    """
    if not is_project_initialized():
        return

    project_path = get_project_path()
    
    # Create database if it doesn't exist
    db_path = get_project_database_path()
    if not db_path.exists():
        db.initialize()
    
    # Migrate data
    migrate_project(project_path)
    migrate_assets(project_path)
    migrate_chats(project_path)
    
    _log.info("Migration completed successfully") 