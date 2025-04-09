import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from aiconsole.core.assets.types import Asset
from aiconsole.core.db.database import db
from aiconsole.core.db.models import (
    User,
    Setting,
    Asset as AssetModel,
    AssetFile,
    Chat,
    ChatMessageGroup,
    ChatOption,
    UserProfile,
    Project,
    CommandHistory
)

class DatabaseOperations:
    @staticmethod
    def save_setting(key: str, value: str, is_global: bool = True, project_id: Optional[str] = None):
        """Save a setting"""
        with Session(db.engine) as session:
            setting = Setting(
                key=key,
                value=value,
                is_global=is_global,
                project_id=project_id
            )
            session.merge(setting)
            session.commit()

    @staticmethod
    def get_setting(key: str, project_id: Optional[str] = None) -> Optional[Setting]:
        """Get a setting by key and optionally project_id"""
        with Session(db.engine) as session:
            query = session.query(Setting).filter(Setting.key == key)
            if project_id:
                query = query.filter(Setting.project_id == project_id)
            return query.first()

    @staticmethod
    def get_all_settings(is_global: bool = True, project_id: Optional[str] = None) -> List[Setting]:
        """Get all settings matching the criteria"""
        with Session(db.engine) as session:
            query = session.query(Setting).filter(Setting.is_global == is_global)
            if project_id:
                query = query.filter(Setting.project_id == project_id)
            return query.all()

    @staticmethod
    def save_asset(asset: Asset):
        """Save an asset"""
        with Session(db.engine) as session:
            session.merge(asset)
            session.commit()

    @staticmethod
    def get_asset(asset_id: str, project_id: Optional[str] = None) -> Optional[Asset]:
        """Get an asset by ID and optionally project_id"""
        with Session(db.engine) as session:
            query = session.query(Asset).filter(Asset.id == asset_id)
            if project_id:
                query = query.filter(Asset.project_id == project_id)
            return query.first()

    @staticmethod
    def save_asset_file(asset_id: str, file_type: str, file_path: str):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO asset_files (asset_id, file_type, file_path)
            VALUES (?, ?, ?)
        ''', (asset_id, file_type, file_path))
        
        conn.commit()

    @staticmethod
    def get_asset_files(asset_id: str) -> List[AssetFile]:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM asset_files WHERE asset_id = ?', (asset_id,))
        return [AssetFile.from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def save_chat(chat: Chat):
        """Save a chat"""
        with Session(db.engine) as session:
            session.merge(chat)
            session.commit()

    @staticmethod
    def get_chat(chat_id: str) -> Optional[Chat]:
        """Get a chat by ID"""
        with Session(db.engine) as session:
            return session.query(Chat).filter(Chat.id == chat_id).first()

    @staticmethod
    def get_chat_messages(chat_id: str) -> List[ChatMessageGroup]:
        """Get all messages for a chat"""
        with Session(db.engine) as session:
            return session.query(ChatMessageGroup).filter(ChatMessageGroup.chat_id == chat_id).all()

    @staticmethod
    def save_chat_message(chat_id: str, role: str, message: str, agent_id: Optional[str] = None):
        """Save a chat message"""
        with Session(db.engine) as session:
            msg = ChatMessageGroup(
                chat_id=chat_id,
                role=role,
                message=message,
                agent_id=agent_id
            )
            session.merge(msg)
            session.commit()

    @staticmethod
    def get_chat_options(chat_id: str) -> Dict[str, str]:
        """Get all options for a chat"""
        with Session(db.engine) as session:
            options = session.query(ChatOption).filter(ChatOption.chat_id == chat_id).all()
            return {opt.key: opt.value for opt in options}

    @staticmethod
    def save_chat_option(chat_id: str, key: str, value: str):
        """Save a chat option"""
        with Session(db.engine) as session:
            opt = ChatOption(
                chat_id=chat_id,
                key=key,
                value=value
            )
            session.merge(opt)
            session.commit()

    @staticmethod
    def save_user_profile(profile: UserProfile):
        """Save a user profile"""
        with Session(db.engine) as session:
            session.merge(profile)
            session.commit()

    @staticmethod
    def get_user_profile(email: Optional[str] = None) -> Optional[UserProfile]:
        """Get a user profile by email"""
        with Session(db.engine) as session:
            if email:
                return session.query(UserProfile).filter(UserProfile.email == email).first()
            return session.query(UserProfile).first()

    @staticmethod
    def save_project(project: Project):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO projects (id, name, path, last_accessed)
            VALUES (?, ?, ?, ?)
        ''', (project.id, project.name, project.path, datetime.now().isoformat()))
        
        conn.commit()

    @staticmethod
    def get_project(project_id: str) -> Optional[Project]:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return Project.from_row(row) if row else None

    @staticmethod
    def save_command(command: str):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO command_history (command) VALUES (?)', (command,))
        conn.commit()

    @staticmethod
    def get_command_history(limit: int = 100) -> List[CommandHistory]:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM command_history ORDER BY executed_at DESC LIMIT ?', (limit,))
        return [CommandHistory.from_row(row) for row in cursor.fetchall()] 