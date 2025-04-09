from pathlib import Path
from typing import TYPE_CHECKING, Optional, List, Dict, Any

from aiconsole.core.db.database import db
from aiconsole.core.db.models import (
    Setting, Asset, Chat, ChatMessageGroup, 
    ChatOption, UserProfile, Project as ProjectModel
)
from aiconsole.core.db.operations import DatabaseOperations
from aiconsole.core.assets.types import AssetType
from aiconsole.core.chat.types import Chat as ChatType
from aiconsole.core.settings.settings_storage import SettingsStorage

if TYPE_CHECKING:
    from aiconsole.core.assets.assets import Assets

class DatabaseStorage:
    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path
        self.project_id = str(project_path) if project_path else None

    # Settings Storage
    def get_setting(self, key: str) -> Optional[str]:
        setting = DatabaseOperations.get_setting(key, self.project_id)
        return setting.value if setting else None

    def save_setting(self, key: str, value: str, is_global: bool = True):
        DatabaseOperations.save_setting(key, value, is_global, self.project_id)

    @property
    def global_settings(self) -> Dict[str, Any]:
        """Get all global settings"""
        settings = {}
        for setting in DatabaseOperations.get_all_settings(is_global=True):
            settings[setting.key] = setting.value
        return settings

    @property
    def project_settings(self) -> Dict[str, Any]:
        """Get all project settings"""
        if not self.project_id:
            return {}
        settings = {}
        for setting in DatabaseOperations.get_all_settings(is_global=False, project_id=self.project_id):
            settings[setting.key] = setting.value
        return settings

    # Asset Storage
    def get_asset(self, asset_type: AssetType, asset_id: str) -> Optional[Asset]:
        return DatabaseOperations.get_asset(asset_id, self.project_id)

    def save_asset(self, asset: Asset):
        DatabaseOperations.save_asset(asset)

    def delete_asset(self, asset_type: AssetType, asset_id: str):
        # Note: In database, we might want to soft delete or archive instead
        pass

    # Chat Storage
    def get_chat(self, chat_id: str) -> Optional[ChatType]:
        chat = DatabaseOperations.get_chat(chat_id)
        if not chat:
            return None

        messages = DatabaseOperations.get_chat_messages(chat_id)
        options = DatabaseOperations.get_chat_options(chat_id)

        return ChatType(
            id=chat.id,
            name=chat.name,
            title_edited=chat.title_edited,
            message_groups=[msg.to_dict() for msg in messages],
            chat_options=options
        )

    def save_chat(self, chat: ChatType):
        db_chat = Chat(
            id=chat.id,
            name=chat.name,
            title_edited=chat.title_edited
        )
        DatabaseOperations.save_chat(db_chat)

        # Save messages
        for msg in chat.message_groups:
            DatabaseOperations.save_chat_message(
                chat_id=chat.id,
                role=msg.get("role"),
                message=msg.get("message"),
                agent_id=msg.get("agent_id")
            )

        # Save options
        for key, value in chat.chat_options.items():
            DatabaseOperations.save_chat_option(chat.id, key, str(value))

    # Project Storage
    def get_project(self) -> Optional[ProjectModel]:
        if not self.project_id:
            return None
        return db.get_project(self.project_id)

    def save_project(self, project: ProjectModel) -> None:
        db.save_project(project)

    # User Profile Storage
    def get_user_profile(self, email: Optional[str] = None) -> Optional[UserProfile]:
        return DatabaseOperations.get_user_profile(email)

    def save_user_profile(self, profile: UserProfile):
        DatabaseOperations.save_user_profile(profile)

    def get_assets(self, asset_type: str) -> "Assets":
        from aiconsole.core.assets.assets import Assets
        return Assets(asset_type=asset_type)

    def get_chats(self) -> list[Chat]:
        return db.get_all_chats()

# Factory function to create storage instances
def create_storage(project_path: Optional[Path] = None) -> DatabaseStorage:
    return DatabaseStorage(project_path) 