import logging
from typing import Dict, List, Optional

from aiconsole.core.chat.types import Chat, ChatMessage, ChatOptions
from aiconsole.core.storage.db_storage import create_storage
from aiconsole.core.project import project

_log = logging.getLogger(__name__)

class ChatService:
    _chats: Dict[str, Chat] = {}
    _storage = None

    def __init__(self):
        self._storage = create_storage(project.get_project_path())

    async def load_chats(self):
        """Load chats from database"""
        self._chats = {}
        
        # Get all chats
        chats = self._storage.get_all_chats()
        
        # Load into memory
        for chat in chats:
            self._chats[chat.id] = chat

    async def save_chat(self, chat: Chat):
        """Save chat to database"""
        self._storage.save_chat(chat)
        self._chats[chat.id] = chat

    async def delete_chat(self, chat_id: str):
        """Delete chat from database"""
        if chat_id in self._chats:
            del self._chats[chat_id]
        self._storage.delete_chat(chat_id)

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        """Get chat from in-memory cache"""
        return self._chats.get(chat_id)

    def get_all_chats(self) -> List[Chat]:
        """Get all chats from in-memory cache"""
        return list(self._chats.values())

    async def save_message(self, chat_id: str, message: ChatMessage):
        """Save message to database"""
        self._storage.save_chat_message(chat_id, message)
        
        # Update in-memory cache
        if chat_id in self._chats:
            self._chats[chat_id].messages.append(message)

    async def save_options(self, chat_id: str, options: ChatOptions):
        """Save chat options to database"""
        self._storage.save_chat_options(chat_id, options)
        
        # Update in-memory cache
        if chat_id in self._chats:
            self._chats[chat_id].options = options 