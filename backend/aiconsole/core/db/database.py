import sqlite3
from pathlib import Path
from typing import Optional

from aiconsole.consts import AICONSOLE_USER_CONFIG_DIR

class Database:
    _instance: Optional['Database'] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._connection is None:
            db_path = AICONSOLE_USER_CONFIG_DIR() / "aiconsole.db"
            self._connection = sqlite3.connect(str(db_path))
            self._connection.row_factory = sqlite3.Row
            self._create_tables()

    def _create_tables(self):
        cursor = self._connection.cursor()
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT,
                is_global BOOLEAN DEFAULT 1,
                project_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(key, project_id)
            )
        ''')

        # Assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                usage TEXT,
                usage_examples TEXT,
                default_status TEXT,
                content_type TEXT,
                content TEXT,
                system TEXT,
                gpt_mode TEXT,
                execution_mode TEXT,
                project_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Asset files table (for images, etc.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES assets(id)
            )
        ''')

        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                name TEXT,
                title_edited BOOLEAN DEFAULT 0,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Chat message groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_message_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                agent_id TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            )
        ''')

        # Chat options table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                option_key TEXT NOT NULL,
                option_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id),
                UNIQUE(chat_id, option_key)
            )
        ''')

        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Command history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_project ON assets(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_messages ON chat_message_groups(chat_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_options ON chat_options(chat_id)')
        
        self._connection.commit()

    def get_connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def __del__(self):
        self.close()

# Singleton instance
db = Database() 