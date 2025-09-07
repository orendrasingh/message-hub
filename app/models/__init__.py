"""
Database models and base classes
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime


class DatabaseManager:
    """Centralized database management"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        # Basic SQL injection detection (params should always be used)
        if params is None or (len(params) == 0 and any(char in query.lower() for char in ['%', "'", '"', ';', '--'])):
            import logging
            logging.warning(f"Potentially unsafe SQL query detected: {query}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update/insert/delete query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute insert query and return last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid


class BaseModel:
    """Base model with common functionality"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class User(BaseModel):
    """User model"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.id = None
        self.name = None
        self.email = None
        self.password_hash = None
        self.evolution_instance_name = None
        self.evolution_api_key = None
        self.whatsapp_connected = False
        self.whatsapp_number = None
        self.qr_code = None
        self.connection_status = 'disconnected'
        self.instance_created = False
        self.created_at = None
        self.last_login = None
    
    @classmethod
    def get_by_id(cls, db_manager: DatabaseManager, user_id: int) -> Optional['User']:
        """Get user by ID"""
        query = "SELECT * FROM app_users WHERE id = ?"
        result = db_manager.execute_query(query, (user_id,))
        
        if result:
            user = cls(db_manager)
            user._populate_from_dict(result[0])
            return user
        return None
    
    @classmethod
    def get_by_email(cls, db_manager: DatabaseManager, email: str) -> Optional['User']:
        """Get user by email"""
        query = "SELECT * FROM app_users WHERE email = ?"
        result = db_manager.execute_query(query, (email,))
        
        if result:
            user = cls(db_manager)
            user._populate_from_dict(result[0])
            return user
        return None
    
    def save(self) -> bool:
        """Save user to database"""
        if self.id:
            # Update existing user
            query = """
                UPDATE app_users SET 
                name = ?, email = ?, password_hash = ?,
                evolution_instance_name = ?, evolution_api_key = ?,
                whatsapp_connected = ?, whatsapp_number = ?,
                qr_code = ?, connection_status = ?,
                instance_created = ?, last_login = ?
                WHERE id = ?
            """
            params = (
                self.name, self.email, self.password_hash,
                self.evolution_instance_name, self.evolution_api_key,
                self.whatsapp_connected, self.whatsapp_number,
                self.qr_code, self.connection_status,
                self.instance_created, self.last_login, self.id
            )
            self.db.execute_update(query, params)
            return True
        else:
            # Create new user
            query = """
                INSERT INTO app_users (
                    name, email, password_hash, evolution_instance_name,
                    evolution_api_key, whatsapp_connected, whatsapp_number,
                    qr_code, connection_status, instance_created, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                self.name, self.email, self.password_hash,
                self.evolution_instance_name, self.evolution_api_key,
                self.whatsapp_connected, self.whatsapp_number,
                self.qr_code, self.connection_status,
                self.instance_created, datetime.now()
            )
            self.id = self.db.execute_insert(query, params)
            return self.id is not None
    
    def delete(self) -> bool:
        """Delete user from database"""
        if self.id:
            query = "DELETE FROM app_users WHERE id = ?"
            return self.db.execute_update(query, (self.id,)) > 0
        return False
    
    def _populate_from_dict(self, data: Dict[str, Any]):
        """Populate user from dictionary"""
        self.id = data.get('id')
        self.name = data.get('name')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.evolution_instance_name = data.get('evolution_instance_name')
        self.evolution_api_key = data.get('evolution_api_key')
        self.whatsapp_connected = bool(data.get('whatsapp_connected'))
        self.whatsapp_number = data.get('whatsapp_number')
        self.qr_code = data.get('qr_code')
        self.connection_status = data.get('connection_status', 'disconnected')
        self.instance_created = bool(data.get('instance_created'))
        self.created_at = data.get('created_at')
        self.last_login = data.get('last_login')


class Contact(BaseModel):
    """Contact model"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.id = None
        self.user_id = None
        self.phone = None
        self.name = None
        self.status = 'pending'
        self.sent_at = None
    
    @classmethod
    def get_by_user(cls, db_manager: DatabaseManager, user_id: int, 
                   limit: int = None, offset: int = None, 
                   search: str = None) -> List['Contact']:
        """Get contacts for user with pagination and search"""
        query = "SELECT * FROM contacts WHERE user_id = ?"
        params = [user_id]
        
        if search:
            query += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " ORDER BY name ASC, id DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            if offset:
                query += " OFFSET ?"
                params.append(offset)
        
        results = db_manager.execute_query(query, tuple(params))
        contacts = []
        for result in results:
            contact = cls(db_manager)
            contact._populate_from_dict(result)
            contacts.append(contact)
        
        return contacts
    
    @classmethod
    def count_by_user(cls, db_manager: DatabaseManager, user_id: int, search: str = None) -> int:
        """Count contacts for user"""
        query = "SELECT COUNT(*) as count FROM contacts WHERE user_id = ?"
        params = [user_id]
        
        if search:
            query += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        result = db_manager.execute_query(query, tuple(params))
        return result[0]['count'] if result else 0
    
    def save(self) -> bool:
        """Save contact to database"""
        if self.id:
            # Update existing contact
            query = """
                UPDATE contacts SET 
                user_id = ?, phone = ?, name = ?, status = ?, sent_at = ?
                WHERE id = ?
            """
            params = (self.user_id, self.phone, self.name, self.status, self.sent_at, self.id)
            return self.db.execute_update(query, params) > 0
        else:
            # Create new contact
            try:
                query = """
                    INSERT INTO contacts (user_id, phone, name, status, sent_at)
                    VALUES (?, ?, ?, ?, ?)
                """
                params = (self.user_id, self.phone, self.name, self.status, self.sent_at)
                self.id = self.db.execute_insert(query, params)
                return self.id is not None
            except sqlite3.IntegrityError:
                # Contact already exists for this user
                return False
    
    def delete(self) -> bool:
        """Delete contact from database"""
        if self.id:
            query = "DELETE FROM contacts WHERE id = ?"
            return self.db.execute_update(query, (self.id,)) > 0
        return False
    
    def _populate_from_dict(self, data: Dict[str, Any]):
        """Populate contact from dictionary"""
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.phone = data.get('phone')
        self.name = data.get('name')
        self.status = data.get('status', 'pending')
        self.sent_at = data.get('sent_at')


class Message(BaseModel):
    """Message model"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.id = None
        self.user_id = None
        self.phone = None
        self.message = None
        self.status = None
        self.timestamp = None
    
    @classmethod
    def get_by_user(cls, db_manager: DatabaseManager, user_id: int, 
                   limit: int = None) -> List['Message']:
        """Get messages for user"""
        query = "SELECT * FROM messages WHERE user_id = ? ORDER BY timestamp DESC"
        params = [user_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        results = db_manager.execute_query(query, tuple(params))
        messages = []
        for result in results:
            message = cls(db_manager)
            message._populate_from_dict(result)
            messages.append(message)
        
        return messages
    
    def save(self) -> bool:
        """Save message to database"""
        if not self.timestamp:
            self.timestamp = datetime.now()
        
        query = """
            INSERT INTO messages (user_id, phone, message, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (self.user_id, self.phone, self.message, self.status, self.timestamp)
        self.id = self.db.execute_insert(query, params)
        return self.id is not None
    
    def _populate_from_dict(self, data: Dict[str, Any]):
        """Populate message from dictionary"""
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.phone = data.get('phone')
        self.message = data.get('message')
        self.status = data.get('status')
        self.timestamp = data.get('timestamp')


# Database initialization
def init_database(db_path: str):
    """Initialize database tables safely, preserving existing data"""
    # Import here to avoid circular imports
    import os
    import sys
    
    # Get the correct path to migrations directory
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_file_dir))
    migrations_dir = os.path.join(project_root, 'migrations')
    
    if os.path.exists(migrations_dir) and migrations_dir not in sys.path:
        sys.path.insert(0, migrations_dir)
    
    try:
        from migrate_database import migrate_database
        return migrate_database(db_path)
    except ImportError as e:
        # Fallback to basic initialization if migration script not available
        print(f"Migration script not found ({e}), using basic initialization...")
        _basic_init_database(db_path)
        return True


def _basic_init_database(db_path: str):
    """Basic database initialization (fallback)"""
    db_manager = DatabaseManager(db_path)
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                evolution_instance_name TEXT UNIQUE,
                evolution_api_key TEXT,
                whatsapp_connected BOOLEAN DEFAULT FALSE,
                whatsapp_number TEXT,
                qr_code TEXT,
                connection_status TEXT DEFAULT 'disconnected',
                instance_created BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Contacts table with proper unique constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                name TEXT,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                UNIQUE(user_id, phone),
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'sent',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                remember_me BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
        
        # Password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
