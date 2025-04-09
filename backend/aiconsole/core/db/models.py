from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Setting:
    id: Optional[int] = None
    key: str = ""
    value: Optional[str] = None
    is_global: bool = True
    project_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            key=row['key'],
            value=row['value'],
            is_global=bool(row['is_global']),
            project_id=row['project_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

@dataclass
class Asset:
    id: str
    type: str
    name: str
    version: str
    usage: Optional[str] = None
    usage_examples: Optional[str] = None
    default_status: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None
    system: Optional[str] = None
    gpt_mode: Optional[str] = None
    execution_mode: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            type=row['type'],
            name=row['name'],
            version=row['version'],
            usage=row['usage'],
            usage_examples=row['usage_examples'],
            default_status=row['default_status'],
            content_type=row['content_type'],
            content=row['content'],
            system=row['system'],
            gpt_mode=row['gpt_mode'],
            execution_mode=row['execution_mode'],
            project_id=row['project_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

@dataclass
class AssetFile:
    id: Optional[int] = None
    asset_id: str = ""
    file_type: str = ""
    file_path: str = ""
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            asset_id=row['asset_id'],
            file_type=row['file_type'],
            file_path=row['file_path'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

@dataclass
class Chat:
    id: str
    name: Optional[str] = None
    title_edited: bool = False
    last_modified: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            name=row['name'],
            title_edited=bool(row['title_edited']),
            last_modified=datetime.fromisoformat(row['last_modified']) if row['last_modified'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

@dataclass
class ChatMessageGroup:
    id: Optional[int] = None
    chat_id: str = ""
    role: str = ""
    agent_id: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            chat_id=row['chat_id'],
            role=row['role'],
            agent_id=row['agent_id'],
            message=row['message'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

@dataclass
class ChatOption:
    id: Optional[int] = None
    chat_id: str = ""
    option_key: str = ""
    option_value: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            chat_id=row['chat_id'],
            option_key=row['option_key'],
            option_value=row['option_value'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

@dataclass
class UserProfile:
    id: Optional[int] = None
    username: str = ""
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            avatar_url=row['avatar_url'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

@dataclass
class Project:
    id: str
    name: str
    path: str
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            name=row['name'],
            path=row['path'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None
        )

@dataclass
class CommandHistory:
    id: Optional[int] = None
    command: str = ""
    executed_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            command=row['command'],
            executed_at=datetime.fromisoformat(row['executed_at']) if row['executed_at'] else None
        ) 